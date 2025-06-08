"""
Content Agent implementation.

This agent consumes research bullet points and generates platform-specific content
with the specified tone.
"""

import os
from typing import Dict, Any

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from models.schema import ContentRequest, ContentResponse, Platform

# Load environment variables
load_dotenv()


class ContentAgent:
    """
    Agent responsible for generating platform-specific content.
    
    Uses PydanticAI Agent with GPT-4o to create content based on research bullet points
    tailored to the target platform and desired tone.
    """
    
    def __init__(self) -> None:
        """Initialize the ContentAgent with OpenAI model configuration."""
        self.agent = Agent(
            model="openai:gpt-4o",
            output_type=ContentResponse,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the content agent."""
        return """
        You are an expert content creator specializing in crafting engaging, platform-optimized
        content from research bullet points.
        
        Your task is to create content that:
        - Is perfectly tailored for the specified platform in both format and length
        - Maintains the requested tone consistently
        - Incorporates the provided research points naturally into the content
        - For Medium posts, includes an engaging title and longer-form content
        - For Twitter, is concise and within character limits with appropriate hashtags
        - For LinkedIn, balances professionalism with engagement
        
        Be creative while ensuring all key research points are incorporated.
        """
    
    def generate_content(self, content_request: ContentRequest) -> ContentResponse:
        """
        Generate platform-specific content based on research bullet points.
        
        Args:
            content_request: The content request containing research, platform, and tone.
            
        Returns:
            A content response with platform-appropriate content.
        """
        platform = content_request.platform.value
        tone = content_request.tone.value
        
        # Extract bullet points into a readable format
        bullet_points = "\n".join(
            [f"• {point.content}" for point in content_request.research.bullet_points]
        )
        
        # Platform-specific instructions
        platform_instructions = {
            Platform.TWITTER.value: (
                "Create a Twitter post (max 280 characters) that's engaging and concise. "
                "Include 1-2 relevant hashtags. No title needed."
            ),
            Platform.LINKEDIN.value: (
                "Create a professional LinkedIn post (300-500 characters) that's insightful "
                "and valuable to professionals. No title needed."
            ),
            Platform.MEDIUM.value: (
                "Create a Medium post with an engaging title and 2-3 paragraphs of content. "
                "The title should be attention-grabbing but accurate."
            ),
        }
        
        prompt = f"""
        Platform: {platform}
        Tone: {tone}
        
        Research Bullet Points:
        {bullet_points}
        
        Instructions:
        {platform_instructions.get(platform, "Create content appropriate for the platform.")}
        
        Ensure the content uses a {tone} tone consistently throughout.
        Incorporate the key points from the research naturally into your content.
        """
        
        result = self.agent.run_sync(prompt)
        return result.output
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph compatible node function to process state in the agent workflow.
        
        Args:
            state: Current workflow state containing research results and preferences.
            
        Returns:
            Updated state with content_result added to it.
        """
        # Extract content request from the state
        content_request = ContentRequest(
            research=state["research_result"],
            platform=state["platform"],
            tone=state["tone"],
        )
        
        # Generate content
        content_result = self.generate_content(content_request)
        
        # Update state with content results
        state["content_result"] = content_result
        
        return state
