"""
Main entry point for the multi-agent LLM system.

This module provides a command-line interface to run the content generation workflow,
accepting topic, platform, and tone arguments.
"""

import argparse
import os
import sys
import time
from typing import Dict, Any, Optional

import logfire
from dotenv import load_dotenv

from models.schema import Platform, Tone
from flow.graph import create_workflow_graph, WorkflowState
from utils.app_logging import initialize_logfire, log_workflow_event


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Multi-agent LLM system for automated content generation"
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Topic for content generation",
    )
    
    parser.add_argument(
        "--platform",
        type=str,
        choices=[p.value for p in Platform],
        required=True,
        help="Target platform for content generation",
    )
    
    parser.add_argument(
        "--tone",
        type=str,
        choices=[t.value for t in Tone],
        required=True,
        help="Tone for the generated content",
    )
    
    return parser.parse_args()


def validate_environment() -> Optional[str]:
    """
    Validate that required environment variables are set.
    
    Returns:
        Error message if validation fails, None otherwise.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "ERROR: OPENAI_API_KEY environment variable is not set. Please create a .env file with this key."
    return None


def run_workflow(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Run the multi-agent workflow with the specified arguments.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        Final workflow state with results.
    """
    # Create initial state for workflow
    initial_state: WorkflowState = {
        "topic": args.topic,
        "platform": Platform(args.platform),
        "tone": Tone(args.tone),
    }
    
    # Create and execute the workflow
    workflow = create_workflow_graph()
    
    print(f"Starting content generation workflow for:")
    print(f"  - Topic: {args.topic}")
    print(f"  - Platform: {args.platform}")
    print(f"  - Tone: {args.tone}")
    
    # Log workflow start with execution ID
    execution_id = str(int(time.time()))
    log_workflow_event(
        event_name="workflow_start",
        state=initial_state,
        additional_data={
            "execution_id": execution_id,
            "args": {
                "topic": args.topic,
                "platform": args.platform,
                "tone": args.tone
            }
        }
    )
    
    try:
        # Execute the workflow and get the final state
        final_state = workflow.invoke(initial_state)
        
        # Log workflow completion
        log_workflow_event(
            event_name="workflow_complete",
            state=final_state,
            additional_data={
                "execution_id": execution_id,
                "status": "success"
            }
        )
        
        return final_state
    except Exception as e:
        # Log workflow error
        log_workflow_event(
            event_name="workflow_error",
            state=initial_state,
            additional_data={
                "execution_id": execution_id,
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )
        raise


def display_results(state: Dict[str, Any]) -> None:
    """
    Display the workflow results."""
    platform = state["platform"].value
    content = state["content_result"]
    image_result = state.get("image_result")
    
    print("=" * 50)
    print(f"GENERATED CONTENT FOR {platform.upper()}")
    print("=" * 50)
    
    if content.title:
        print("\nTITLE: " + content.title)
    
    print("\nCONTENT:")
    print(content.content)
    
    if image_result:
        print("\nGENERATED IMAGE:")
        print(f"Prompt: {image_result.image_prompt}")
        print(f"Saved to: {image_result.image_path}")
    
    print("=" * 50)


def main() -> int:
    """
    Main function that orchestrates the workflow.
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize logfire for structured logging
    initialize_logfire()
    
    # Validate environment
    error = validate_environment()
    if error:
        print(error)
        return 1
    
    # Parse command-line arguments
    try:
        args = parse_args()
    except SystemExit:
        # Handle --help or invalid arguments
        return 1
    
    # Create a span context for the entire execution
    with logfire.span("agent_workflow_execution") as span:
        # Set additional attributes on the span
        span.set_attributes({
            "service": "pydantic-ai-agents",
            "topic": args.topic,
            "platform": args.platform,
            "tone": args.tone
        })
        try:
            # Run the workflow
            final_state = run_workflow(args)
            
            # Display results
            display_results(final_state)
            
            return 0
        except Exception as e:
            print(f"Error during workflow execution: {str(e)}")
            # Log the error in the trace context
            logfire.exception(e, message="Workflow execution failed", error_type=type(e).__name__)
            return 1


if __name__ == "__main__":
    sys.exit(main())
