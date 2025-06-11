"""
Logging utilities with logfire integration for structured tracing of agent workflows.

This module provides logfire-based logging functionality to capture prompt/response
cycles from all agents in the system with structured tracing.
"""

import os
from typing import Any, Dict, Optional

import logfire
from pydantic import BaseModel, Field
import openai


def initialize_logfire() -> None:
    """
    Initialize logfire for structured logging and tracing.
    
    Sets up logfire with appropriate configuration for development and 
    production environments.
    """
    try:
        # Initialize with minimal configuration
        # For testing purposes only - suppress warnings about missing configuration
        import os
        os.environ.setdefault('LOGFIRE_IGNORE_NO_CONFIG', '1')  # Suppress warnings
        
        # Initialize logfire with the simplest possible configuration
        logfire.configure(token='pylf_v1_eu_1P5yR9LS0nK5FCRqxB9b3rgc0dT9bhCKdmnNwQ6DBbwq')
        
        # Configure OpenAI to use logfire for tracing
        openai.log = "debug"  # Enable logging for OpenAI API calls
    except Exception as e:
        # Fallback if logfire cannot be initialized
        print(f"Warning: Failed to initialize logfire: {e}")
        print("Continuing without structured logging capabilities.")



class AgentContext(BaseModel):
    """Context information for agent logging."""
    
    agent_type: str = Field(description="Type/name of the agent")
    input_type: str = Field(description="Type of input provided to the agent")
    output_type: str = Field(description="Type of output expected from the agent")


def log_agent_start(agent_type: str, prompt: Any, ctx: Optional[Dict[str, Any]] = None) -> None:
    """
    Log the start of an agent operation with the input prompt.
    
    Args:
        agent_type: Type of the agent (e.g., "ResearchAgent", "ContentAgent")
        prompt: The prompt being sent to the agent
        ctx: Optional additional context information
    """
    event_data = {
        "agent_type": agent_type,
        "event": "agent_start",
        "prompt": str(prompt),
    }
    
    if ctx:
        event_data.update(ctx)
        
    logfire.info("Agent execution started", **event_data)


def log_agent_completion(
    agent_type: str, 
    result: Any, 
    elapsed_time_ms: Optional[float] = None,
    ctx: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log the completion of an agent operation with the result.
    
    Args:
        agent_type: Type of the agent (e.g., "ResearchAgent", "ContentAgent")
        result: The result from the agent execution
        elapsed_time_ms: Optional elapsed time in milliseconds
        ctx: Optional additional context information
    """
    event_data = {
        "agent_type": agent_type,
        "event": "agent_completion",
    }
    
    # Add result to event data, handling different result types
    if isinstance(result, BaseModel):
        event_data["result"] = result.model_dump()
    elif hasattr(result, "__dict__"):
        event_data["result"] = result.__dict__
    else:
        event_data["result"] = str(result)
    
    if elapsed_time_ms is not None:
        event_data["elapsed_time_ms"] = elapsed_time_ms
        
    if ctx:
        event_data.update(ctx)
        
    logfire.info("Agent execution completed", **event_data)


def log_agent_error(
    agent_type: str, 
    error: Exception, 
    ctx: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an error that occurred during agent execution.
    
    Args:
        agent_type: Type of the agent (e.g., "ResearchAgent", "ContentAgent")
        error: The exception that occurred
        ctx: Optional additional context information
    """
    event_data = {
        "agent_type": agent_type,
        "event": "agent_error",
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if ctx:
        event_data.update(ctx)
        
    logfire.error("Agent execution error", **event_data)


def log_workflow_event(
    event_name: str,
    state: Dict[str, Any],
    additional_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a workflow event with the current state.
    
    Args:
        event_name: Name of the workflow event (e.g., "workflow_start", "node_transition")
        state: The current workflow state
        additional_data: Optional additional data to include in the log
    """
    event_data = {
        "event": event_name,
        "state_keys": list(state.keys()),
    }
    
    # Add safe representation of state (exclude large objects)
    safe_state = {}
    for k, v in state.items():
        if isinstance(v, BaseModel):
            # For BaseModel objects, include class name and some metadata
            safe_state[k] = f"{v.__class__.__name__} instance"
        else:
            # For other objects use string representation (limited length)
            str_rep = str(v)
            safe_state[k] = (str_rep[:100] + '...') if len(str_rep) > 100 else str_rep
            
    event_data["state"] = safe_state
    
    if additional_data:
        event_data.update(additional_data)
        
    logfire.info(f"Workflow event: {event_name}", **event_data)
