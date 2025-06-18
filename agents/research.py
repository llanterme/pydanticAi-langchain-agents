"""
Research Agent implementation.

This agent is responsible for researching a topic and generating 5-7 factual bullet points
that will be used by the ContentAgent for content generation.
"""

import os
import time
from typing import Dict, Any

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from models.schema import ResearchRequest, ResearchResponse
from utils.app_logging import log_agent_start, log_agent_completion, log_agent_error

# Load environment variables
load_dotenv()


class ResearchAgent:
    """
    Agent responsible for researching topics and generating factual bullet points.
    
    Uses PydanticAI Agent with GPT-4o to generate high-quality research results
    based on user-provided topic, platform, and tone.
    """
    
    def __init__(self) -> None:
        """Initialize the ResearchAgent with OpenAI model configuration."""
        self.agent = Agent(
            model="openai:gpt-4o",
            output_type=ResearchResponse,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the research agent."""
        return """
        You are an expert research assistant specializing in finding accurate, relevant information.
        Your task is to gather 5-7 factual bullet points on a given topic.
        
        Each bullet point should:
        - Be concise and factual (no opinions)
        - Include specific data points, statistics, or quotable facts when possible
        - Be tailored to be useful for the specified platform and tone
        - Avoid repetition across bullet points
        - Be presented without numbering or prefixes
        
        Your output will be used to generate content for the specified platform,
        so focus on information that would be valuable in that context.
        """
    
    def research(self, research_request: ResearchRequest) -> ResearchResponse:
        """
        Execute research on the given topic and return factual bullet points.
        
        Args:
            research_request: The research request containing topic, platform, and tone.
            
        Returns:
            A research response containing 5-7 factual bullet points.
        """
        prompt = f"""
        Research Topic: {research_request.topic}
        Target Platform: {research_request.platform.value}
        Content Tone: {research_request.tone.value}
        
        Please provide 5-7 factual bullet points on this topic that would be useful
        for creating content for {research_request.platform.value} with a {research_request.tone.value} tone.
        
        Focus on recent data, surprising facts, and information that would engage the
        target audience on {research_request.platform.value}.
        """
        
        # Log the start of agent execution
        log_agent_start(
            agent_type="ResearchAgent",
            prompt=prompt,
            ctx={
                "topic": research_request.topic,
                "platform": research_request.platform.value,
                "tone": research_request.tone.value,
                "input_type": "ResearchRequest"
            }
        )
        
        start_time = time.time()
        try:
            result = self.agent.run_sync(prompt)
            
            # Calculate elapsed time in milliseconds
            elapsed_time_ms = (time.time() - start_time) * 1000
            
            # Log successful completion
            log_agent_completion(
                agent_type="ResearchAgent",
                result=result.output,
                elapsed_time_ms=elapsed_time_ms,
                ctx={
                    "topic": research_request.topic,
                    "bullet_point_count": len(result.output.bullet_points),
                    "output_type": "ResearchResponse"
                }
            )
            
            return result.output
        
        except Exception as e:
            # Log error
            log_agent_error(
                agent_type="ResearchAgent",
                error=e,
                ctx={
                    "topic": research_request.topic,
                    "platform": research_request.platform.value,
                    "tone": research_request.tone.value
                }
            )
            raise
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph compatible node function to process state in the agent workflow.
        
        Args:
            state: Current workflow state containing research request parameters.
            
        Returns:
            Updated state with research_result added to it.
        """
        # Extract research request from the state
        research_request = ResearchRequest(
            topic=state.get("topic", ""),
            platform=state.get("platform", ""),
            tone=state.get("tone", ""),
        )
        
        # Perform research
        research_result = self.research(research_request)
        
        # Update state with research results
        state["research_result"] = research_result
        
        return state
