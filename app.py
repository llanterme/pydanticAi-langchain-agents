"""
Streamlit application for the multi-agent LLM system.

This module provides a web interface for users to interact with the content generation workflow,
allowing them to specify topic, platform, and tone for content generation.
"""

import os
from pathlib import Path
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

from models.schema import Platform, Tone
from flow.graph import create_workflow_graph, WorkflowState


def initialize_app():
    """Initialize the application and set up the page configuration."""
    st.set_page_config(
        page_title="AI Content Generator",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("AI Content Generator")
    st.write("Generate content and images using advanced AI agents.")


def validate_environment():
    """
    Validate that required environment variables are set.
    
    Returns:
        Error message if validation fails, None otherwise.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "ERROR: OPENAI_API_KEY environment variable is not set. Please create a .env file with this key."
    return None


def user_input_form():
    """
    Create a form for user input.
    
    Returns:
        Dictionary with user inputs if form is submitted, None otherwise.
    """
    with st.form("content_generation_form"):
        col1, col2 = st.columns(2)

        with col1:
            topic = st.text_input(
                "Topic", 
                placeholder="e.g., artificial intelligence ethics",
                help="Enter the subject you want to generate content about"
            )
            platform = st.selectbox(
                "Platform",
                options=[p.value for p in Platform],
                format_func=lambda x: x.capitalize(),
                help="Select the platform where your content will be published"
            )

        with col2:
            tone = st.selectbox(
                "Tone",
                options=[t.value for t in Tone],
                format_func=lambda x: x.capitalize(),
                help="Select the style and mood for your content"
            )
            
        submit_button = st.form_submit_button("Generate Content")
        
        if submit_button and topic:
            return {
                "topic": topic,
                "platform": platform,
                "tone": tone
            }
        elif submit_button and not topic:
            st.error("Please enter a topic before generating content.")
            
        return None


def run_workflow(inputs):
    """
    Run the multi-agent workflow with the user inputs.
    
    Args:
        inputs: Dictionary containing user inputs.
        
    Returns:
        Final workflow state with results.
    """
    # Create initial state for workflow
    initial_state: WorkflowState = {
        "topic": inputs["topic"],
        "platform": Platform(inputs["platform"]),
        "tone": Tone(inputs["tone"]),
    }
    
    # Create and execute the workflow
    workflow = create_workflow_graph()
    
    with st.spinner("Generating content and image... This may take a minute or two."):
        # Execute the workflow and get the final state
        final_state = workflow.invoke(initial_state)
        
    return final_state


def display_results(state):
    """
    Display the workflow results in the Streamlit UI.
    
    Args:
        state: Final workflow state with results.
    """
    platform = state["platform"].value
    content = state["content_result"]
    image_result = state.get("image_result")
    
    st.success("Content generated successfully!")
    
    # Create tabs to organize results
    tab1, tab2, tab3 = st.tabs(["Generated Content", "Image", "Research Notes"])
    
    # Content tab
    with tab1:
        st.subheader(f"{platform.capitalize()} Content")
        
        if content.title:
            st.markdown(f"### {content.title}")
            
        st.write(content.content)
        
        tone = state["tone"].value
        st.caption(f"Generated with a {tone} tone for {platform}")
        
    # Image tab
    with tab2:
        if image_result and Path(str(image_result.image_path)).exists():
            st.subheader("Generated Image")
            
            # Display the image
            image = Image.open(image_result.image_path)
            st.image(image, caption=f"Generated for {platform} content", use_column_width=True)
            
            with st.expander("Image Generation Prompt"):
                st.write(image_result.image_prompt)
        else:
            st.warning("No image was generated or the image file was not found.")
            
    # Research tab        
    with tab3:
        st.subheader("Research Bullet Points")
        
        research = state.get("research_result")
        if research and research.bullet_points:
            for i, point in enumerate(research.bullet_points, 1):
                st.markdown(f"{i}. {point.content}")
        else:
            st.info("No research data available.")


def main():
    """Main function to run the Streamlit app."""
    # Load environment variables
    load_dotenv()
    
    # Initialize the app
    initialize_app()
    
    # Validate environment
    error = validate_environment()
    if error:
        st.error(error)
        return
    
    # Get user input
    inputs = user_input_form()
    
    # Run workflow if inputs are provided
    if inputs:
        try:
            # Create placeholder for generated content
            result_container = st.container()
            
            with result_container:
                # Run the workflow
                final_state = run_workflow(inputs)
                
                # Display results
                display_results(final_state)
                
        except Exception as e:
            st.error(f"Error during content generation: {str(e)}")
            st.exception(e)


if __name__ == "__main__":
    main()
