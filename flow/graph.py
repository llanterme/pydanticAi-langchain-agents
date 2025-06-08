"""
LangGraph workflow definition.

This module defines a directed acyclic graph (DAG) to orchestrate the agent workflow
from research to content generation.
"""

from typing import TypedDict, Annotated

from langgraph.graph import StateGraph
from langgraph.constants import END

from agents.research import ResearchAgent
from agents.content import ContentAgent
from agents.image import ImageAgent
from models.schema import ResearchResponse, ContentResponse, ImageResponse, Platform, Tone


class WorkflowState(TypedDict, total=False):
    """Type definition for the state passed between graph nodes."""
    
    topic: str
    platform: Platform
    tone: Tone
    research_result: ResearchResponse
    content_result: ContentResponse
    image_result: ImageResponse


def create_workflow_graph():
    """
    Create a LangGraph workflow that orchestrates the multi-agent system.
    
    The workflow follows a sequential path:
    1. Research agent gathers factual bullet points
    2. Content agent generates platform-specific content
    
    Returns:
        A compiled LangGraph workflow instance defining the workflow.
    """
    # Initialize agents
    research_agent = ResearchAgent()
    content_agent = ContentAgent()
    image_agent = ImageAgent()
    
    # Create state graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes to the graph
    workflow.add_node("research", research_agent.run)
    workflow.add_node("content", content_agent.run)
    workflow.add_node("image", image_agent.run)
    
    # Define the edges (research → content → image → end)
    workflow.add_edge("research", "content")
    workflow.add_edge("content", "image")
    workflow.add_edge("image", END)
    
    # Set the entry point
    workflow.set_entry_point("research")
    
    # Compile the graph
    return workflow.compile()
