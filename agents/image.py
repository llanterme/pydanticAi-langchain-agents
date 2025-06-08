"""
Image generation agent implementation.

This module defines the ImageAgent class responsible for generating images
based on the content produced by the ContentAgent.
"""

import os
import base64
import logging
from pathlib import Path
from typing import Dict, Any
import uuid

from openai import OpenAI
from pydantic_ai import Agent, RunContext

from models.schema import ImageRequest, ImageResponse

class ImageAgent:
    """
    Agent responsible for generating images based on content.
    
    This agent uses OpenAI's GPT-Image-1 model to generate images that align
    with the platform-specific content created by the ContentAgent.
    """
    
    def __init__(self) -> None:
        """Initialize the ImageAgent with OpenAI model configuration."""
        self.agent = Agent(
            model="openai:gpt-4o",
            output_type=ImageResponse,
            system_prompt=self._get_system_prompt()
        )
        self.client = OpenAI()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the image agent."""
        return """
        You are an expert image prompt engineer specialized in creating effective prompts
        for AI image generation based on text content.
        
        Your task is to:
        1. Analyze the provided content
        2. Extract key visual elements that would make a compelling image
        3. Create a detailed, descriptive prompt for image generation
        
        The image prompt should:
        - Be visually descriptive and detailed (colors, style, mood, etc.)
        - Relate directly to the main points in the content
        - Match the tone of the original content
        - Be appropriate for the target platform
        
        Focus on creating a prompt that will generate a single cohesive image that
        best represents the essence of the content.
        """
    
    def generate_image(self, image_request: ImageRequest) -> ImageResponse:
        """
        Generate an image based on content.
        
        Args:
            image_request: The image request containing content, platform, and tone.
            
        Returns:
            An image response with the prompt used and path to the generated image.
        """
        # Extract content for prompt generation
        platform = image_request.platform.value
        tone = image_request.tone.value
        content = image_request.content.content
        title = image_request.content.title
        
        # Format the prompt request
        prompt_request = f"""
        Content: {content}
        Title (if any): {title}
        Platform: {platform}
        Tone: {tone}
        
        Please create a detailed image generation prompt that captures the essence of this content.
        The prompt should be descriptive and include visual elements like style, colors, mood, and composition.
        """
        
        # Generate the image prompt
        result = self.agent.run_sync(prompt_request)
        image_prompt = result.output.image_prompt
        
        # Ensure the images directory exists
        image_dir = Path("data/images")
        image_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate a unique filename
        filename = f"{platform}_{uuid.uuid4().hex[:8]}.png"
        image_path = image_dir / filename
        
        # Generate the image using OpenAI's direct images.generate API
        try:
            # Use the exact method shown in the curl example
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=image_prompt,
                n=1,
                size="1024x1024"
            )
            
            # Extract the base64 image data as shown in the response example
            image_b64 = response.data[0].b64_json
                
            # Decode and save the image
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_b64))
                
            print(f"Image generated and saved to {image_path}")
                
        except Exception as e:
            print(f"Error generating image: {e}")
            # Create a placeholder path in case of error
            image_path = Path("data/images/error_placeholder.png")
        
        return ImageResponse(
            image_prompt=image_prompt,
            image_path=image_path
        )
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the state and generate an image.
        
        Args:
            state: The current workflow state containing content and research data.
            
        Returns:
            Updated state with image generation results.
        """
        # Create an image request from the state
        image_request = ImageRequest(
            content=state["content_result"],
            platform=state["platform"],
            tone=state["tone"]
        )
        
        # Generate the image
        image_result = self.generate_image(image_request)
        
        # Update the state with the image result
        state["image_result"] = image_result
        
        return state
