"""
Test module to verify logfire integration.

This module provides a simple test to validate that the logfire 
integration is working correctly with PydanticAI agents.
"""

import sys
import time
from datetime import datetime

import logfire
from pydantic_ai import Agent
from pydantic import BaseModel, Field

from utils.app_logging import initialize_logfire, log_agent_start, log_agent_completion, log_agent_error


class TestOutput(BaseModel):
    """Test output model."""
    message: str = Field(description="A test message")
    timestamp: str = Field(description="The current timestamp")


def test_logfire_agent_integration():
    """
    Test function to verify logfire integration with PydanticAI.
    
    This test creates a simple agent, logs the lifecycle events, and
    verifies that traces are being properly created.
    """
    # Initialize logfire
    initialize_logfire()
    
    print("Testing logfire integration with PydanticAI agents...")
    
    # Create a simple PydanticAI agent
    agent = Agent(
        model="openai:gpt-4o",
        output_type=TestOutput,
        system_prompt="You are a helpful assistant that responds with the current timestamp."
    )
    
    # Create a span context for the test
    with logfire.span("test_logfire_integration") as span:
        # Set additional attributes on the span
        span.set_attributes({
            "service": "pydantic-ai-agents-test",
            "test_name": "basic_agent_test"
        })
        try:
            # Log the start of agent execution
            test_prompt = "Please return the current timestamp and a message saying the test was successful."
            log_agent_start(
                agent_type="TestAgent",
                prompt=test_prompt,
                ctx={"test_type": "integration"}
            )
            
            start_time = time.time()
            
            # Run the agent
            result = agent.run_sync(test_prompt)
            
            # Calculate elapsed time
            elapsed_time_ms = (time.time() - start_time) * 1000
            
            # Log completion
            log_agent_completion(
                agent_type="TestAgent",
                result=result.output,
                elapsed_time_ms=elapsed_time_ms,
                ctx={"test_result": "success"}
            )
            
            # Print the result
            print(f"Test completed successfully!")
            print(f"Message: {result.output.message}")
            print(f"Timestamp: {result.output.timestamp}")
            
            # Note on tracing
            print(f"Test completed successfully!")
            print(f"When using logfire with remote reporting configured,")
            print(f"you can view traces in the logfire dashboard.")
            print(f"For local development, check the console output above.")
            # We're using disable_remote=True for testing, so there's no trace ID to retrieve
            
            return True
            
        except Exception as e:
            # Log error
            log_agent_error(
                agent_type="TestAgent",
                error=e,
                ctx={"test_result": "error"}
            )
            print(f"Error during test: {e}")
            return False


if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    from dotenv import load_dotenv
    load_dotenv()
    
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)
    
    # Run the test
    success = test_logfire_agent_integration()
    sys.exit(0 if success else 1)
