"""
Schema definitions for agent inputs and outputs.

This module contains all Pydantic models used by the research, content, and image agents.
"""

from enum import Enum
from typing import List, Optional
from pathlib import Path

from pydantic import BaseModel, Field


class Platform(str, Enum):
    """Supported social media platforms for content generation."""
    
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    MEDIUM = "medium"


class Tone(str, Enum):
    """Available tones for content generation."""
    
    INFORMATIVE = "informative"
    PERSUASIVE = "persuasive"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    ENTHUSIASTIC = "enthusiastic"


class ResearchRequest(BaseModel):
    """
    Input schema for ResearchAgent.
    
    Contains the topic to research along with platform and tone preferences
    to guide the research focus.
    """
    
    topic: str = Field(
        description="The subject or theme to research",
        examples=["artificial intelligence ethics", "sustainable fashion"]
    )
    platform: Platform = Field(
        description="Target platform for the final content",
        examples=["twitter", "linkedin", "medium"]
    )
    tone: Tone = Field(
        description="Desired tone for the final content",
        examples=["informative", "persuasive", "casual", "professional", "enthusiastic"]
    )


class ResearchBulletPoint(BaseModel):
    """A single research bullet point with content."""
    
    content: str = Field(
        description="Factual, well-researched information point",
        examples=["75% of enterprises plan to use AI by 2025 according to Gartner."]
    )


class ResearchResponse(BaseModel):
    """
    Output schema for ResearchAgent.
    
    Contains 5-7 factual bullet points that will be used by the ContentAgent.
    """
    
    bullet_points: List[ResearchBulletPoint] = Field(
        description="5-7 factual bullet points about the requested topic",
        min_items=5,
        max_items=7
    )


class ContentRequest(BaseModel):
    """
    Input schema for ContentAgent.
    
    Contains the research bullet points along with platform and tone preferences
    for content generation.
    """
    
    research: ResearchResponse = Field(
        description="Research results containing factual bullet points"
    )
    platform: Platform = Field(
        description="Target platform for content generation",
        examples=["twitter", "linkedin", "medium"]
    )
    tone: Tone = Field(
        description="Desired tone for the content",
        examples=["informative", "persuasive", "casual", "professional", "enthusiastic"]
    )


class ContentResponse(BaseModel):
    """
    Output schema for ContentAgent.
    
    Contains the generated content tailored for the specified platform and tone.
    Medium posts include a title, while other platforms do not.
    """
    
    title: Optional[str] = Field(
        None,
        description="Title for the content (only for Medium posts)",
        examples=["The Evolution of AI Ethics: 5 Key Considerations for 2025"]
    )
    content: str = Field(
        description="Generated content for the specified platform and tone",
        examples=[
            "AI ethics isn't just theoretical anymore. With 75% of enterprises adopting AI by 2025, we need practical governance frameworks now. #AIethics #TechTrends",
            "Excited to share my latest thoughts on sustainable fashion! 🌱👗 The industry is transforming with 65% of consumers now willing to pay more for eco-friendly options. What's your take?"
        ]
    )


class ImageRequest(BaseModel):
    """Request for the ImageAgent."""
    
    content: ContentResponse = Field(
        description="The generated content from which to create an image."
    )
    platform: Platform = Field(
        description="The platform for which the content was created."
    )
    tone: Tone = Field(
        description="The tone of the content."
    )


class ImageResponse(BaseModel):
    """Response from the ImageAgent."""
    
    image_prompt: str = Field(
        description="The prompt used to generate the image."
    )
    image_path: Path = Field(
        description="Path to the generated image file."
    )
