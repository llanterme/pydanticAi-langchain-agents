# Multi-Agent LLM System

A multi-agent LLM system that automates content generation using typed models, LangGraph orchestration, and OpenAI completions. This system uses a pipeline of specialized agents to research a topic, transform that research into platform-optimized content, and generate accompanying images.

## Features

- **Research Agent**: Generates 5-7 factual bullet points on a given topic
- **Content Agent**: Creates platform-specific content based on research with appropriate tone
- **Image Agent**: Creates visual imagery using OpenAI's image generation API (gpt-image-1 model)
- **Streamlit Web UI**: Interactive interface for easy content generation
- **LangGraph orchestration**: Structured workflow between agents
- **PydanticAI**: Strong typing and structured LLM outputs

## Core Technologies

| Library        | Version     | Purpose                                                           |
|----------------|-------------|-------------------------------------------------------------------|
| PydanticAI     | 0.2.15      | Declarative prompt modeling & structured LLM output parsing       |
| LangGraph      | 0.4.8       | DAG-style multi-agent orchestration                              |
| OpenAI SDK     | 1.84.0      | Call GPT-4o and other models through API endpoints               |
| Logfire        | 3.18.0      | Structured tracing and logging for all prompt/response cycles    |
| Poetry         | 1.8.4       | Dependency, packaging, and virtualenv management                 |
| Streamlit      | Latest      | Interactive web interface                                        |

## Prerequisites

- Python 3.10 or higher
- Poetry package manager
- OpenAI API key
- Docker (optional, if you want to containerize the application)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd pydanticAi-langchain
```

### 2. Install Dependencies

Install all dependencies using Poetry:

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install --no-root
```

### 3. Set Up Environment

Create a `.env` file in the project root with your OpenAI API key:

```bash
echo "OPENAI_API_KEY=your_key_here" > .env
```

### 4. Activate Poetry Environment

```bash
poetry shell
```

## Usage

### Command Line Interface

Generate content and images by running the main script with your desired topic, platform, and tone:

```bash
# Basic usage
python main.py --topic "your topic here" --platform [twitter|linkedin|medium] --tone [professional|casual|informative|persuasive|enthusiastic]

# Example: Create a professional Medium post about AI ethics with an accompanying image
python main.py --topic "artificial intelligence ethics" --platform medium --tone professional

# Example: Create a casual Twitter post about renewable energy with an accompanying image
python main.py --topic "renewable energy trends" --platform twitter --tone casual
```

### Docker Container

You can run the application in a Docker container for a consistent environment across platforms:

```bash
# Build the Docker image
docker build -t pydanticai-langchain .

# Run the container
docker run -p 8501:8501 --env-file .env pydanticai-langchain
```

This will make the Streamlit application accessible at http://localhost:8501 in your web browser.

### Streamlit Web Interface

Alternatively, use the Streamlit web interface directly for a more interactive experience:

```bash
# Run the Streamlit app
streamlit run app.py
```

This will open a web interface where you can:
- Enter your desired topic
- Select platform (Twitter, LinkedIn, Medium)
- Choose tone (Professional, Casual, Informative, Persuasive, Enthusiastic)
- Generate and view content and images directly in your browser

#### Workflow:

1. **Research Phase**: The Research Agent generates 5-7 factual bullet points about your topic
2. **Content Creation**: The Content Agent transforms these facts into platform-specific content with the specified tone
3. **Image Generation**: The Image Agent uses OpenAI's gpt-image-1 model to create an AI-generated image that complements the content
4. **Display**: Results are presented with both the generated content and image

## Supported Platforms

- **Twitter**: Concise posts under 280 characters with relevant hashtags
- **LinkedIn**: Professional posts optimized for business audience (300-500 characters)
- **Medium**: Longer-form content with title and multiple paragraphs

## Supported Tones

- **Professional**: Formal and business-oriented language
- **Casual**: Conversational and relaxed style
- **Informative**: Educational and fact-focused approach
- **Persuasive**: Convincing and compelling language
- **Enthusiastic**: Energetic and passionate expression

## Project Structure

```
.
├── agents/           # Agent implementations
│   ├── research.py   # ResearchAgent using PydanticAI
│   ├── content.py    # ContentAgent using PydanticAI
│   └── image.py      # ImageAgent using PydanticAI and OpenAI's image generation
├── flow/             # LangGraph workflow
│   └── graph.py      # Agent orchestration graph
├── models/           # Typed models
│   └── schema.py     # Pydantic models for agent I/O
├── utils/            # Utility modules
│   ├── logging.py    # Logfire integration for structured logging
│   └── trace_viewer.py # Tool for viewing and analyzing logfire traces
├── data/             # Generated output
│   └── images/       # Generated images
├── main.py           # CLI entrypoint
├── app.py            # Streamlit web interface
├── prompts/          # System prompt templates
├── pyproject.toml    # Poetry configuration
├── README.md         # Project documentation
├── PLANNING.md       # Project planning and requirements
└── Dockerfile        # Docker container configuration
```

## Observability with Logfire

This project integrates [Logfire](https://ai.pydantic.dev/logfire) v3.18.0 for comprehensive structured tracing and logging of all prompt/response cycles in the agent system.

### Tracing Features

- **Complete Agent Lifecycle Tracing**: Traces every operation from prompt submission to response generation
- **Detailed Timing Metrics**: Records response times for each agent and operation
- **Workflow State Tracking**: Monitors state changes across the entire agent workflow
- **Exception Handling**: Captures and logs all errors with context
- **Structured Data**: All trace data is structured for easy analysis

### Using the Trace Viewer

The project includes a trace viewer utility for analyzing agent performance and behavior:

```bash
# View trace summaries from the last 24 hours
python -m utils.trace_viewer

# View a specific trace by ID
python -m utils.trace_viewer --trace-id <trace-id>

# Filter traces by agent type
python -m utils.trace_viewer --agent ResearchAgent

# Filter traces containing a specific topic
python -m utils.trace_viewer --topic "artificial intelligence"

# View detailed trace information
python -m utils.trace_viewer --format detailed

# Export trace data as JSON
python -m utils.trace_viewer --format json > traces.json
```

### Programmatic Access to Traces

You can also access trace data programmatically:

```python
import logfire
from utils.logging import initialize_logfire

# Initialize logfire
initialize_logfire()

# Query traces from the last hour
from datetime import datetime, timedelta
start_time = datetime.now() - timedelta(hours=1)
traces = logfire.query_traces(start_time=start_time.isoformat())

# Analyze trace data
for trace in traces:
    print(f"Trace ID: {trace['id']}")
    print(f"Duration: {trace['duration']}ms")
    # Access spans, events, and other trace data
```

## Development

To contribute to this project:

1. Ensure you have Poetry installed for dependency management
2. Make your changes following PEP 8 and the project's functional style guidelines
3. Maintain Python 3.10+ compatibility
4. Run the application to test your changes
5. Add comprehensive unit tests for any new functionality
6. Keep functions/classes small with single responsibilities
7. Prioritize immutability and pure functions where possible

## Future Extensions

The project structure is designed to support additional agents such as:
- SEO Agent for optimizing content for search engines
- Fact Checker Agent for verifying generated content
- Analytics Agent for tracking content performance
- Additional platform support (Instagram, Facebook, etc.)
