"""
LangGraph workflow definition.

This module defines a directed acyclic graph (DAG) to orchestrate the agent workflow
from research to content generation.
"""

from typing import TypedDict, Annotated, Dict, Any, Callable

from langgraph.graph import StateGraph
from langgraph.constants import END

from agents.research import ResearchAgent
from agents.content import ContentAgent
from agents.image import ImageAgent
from models.schema import ResearchResponse, ContentResponse, ImageResponse, Platform, Tone
from utils.logging import log_workflow_event


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
    3. Image agent generates an image based on content
    
    Returns:
        A compiled LangGraph workflow instance defining the workflow.
    """
    # Initialize agents
    research_agent = ResearchAgent()
    content_agent = ContentAgent()
    image_agent = ImageAgent()
    
    # Create state graph
    workflow = StateGraph(WorkflowState)
    
    # Define tracing wrappers for each agent
    def trace_node(node_name: str, agent_func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        def traced_func(state: Dict[str, Any]) -> Dict[str, Any]:
            # Log node entry
            log_workflow_event(
                event_name=f"{node_name}_start",
                state=state,
                additional_data={"node": node_name}
            )
            
            # Execute the agent function
            result = agent_func(state)
            
            # Log node exit
            log_workflow_event(
                event_name=f"{node_name}_complete",
                state=result,
                additional_data={"node": node_name}
            )
            
            return result
        return traced_func
    
    # Add nodes to the graph with tracing
    workflow.add_node("research", trace_node("research", research_agent.run))
    workflow.add_node("content", trace_node("content", content_agent.run))
    workflow.add_node("image", trace_node("image", image_agent.run))
    
    # Define the edges (research → content → image → end)
    workflow.add_edge("research", "content")
    workflow.add_edge("content", "image")
    workflow.add_edge("image", END)
    
    # Set the entry point
    workflow.set_entry_point("research")
    
    # Compile the graph
    return workflow.compile()
