# Multi-Agent LLM System

A multi-agent LLM system that automates content generation using typed models, LangGraph orchestration, and OpenAI completions. This system uses a pipeline of specialized agents to first research a topic, then transform that research into platform-optimized content.

## Features

- Research Agent: Generates factual bullet points on a given topic
- Content Agent: Creates platform-specific content based on research
- Image Agent: Creates visual imagery based on the generated content
- LangGraph orchestration for agent workflow
- PydanticAI for strong typing and structured LLM outputs

## Prerequisites

- Python 3.9.10 or higher
- Poetry package manager
- OpenAI API key

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

Generate content and images by running the main script with your desired topic, platform, and tone:

```bash
# Basic usage
python main.py --topic "your topic here" --platform [twitter|linkedin|medium] --tone [professional|casual|informative]

# Example: Create a professional Medium post about AI ethics with an accompanying image
python main.py --topic "artificial intelligence ethics" --platform medium --tone professional

# Example: Create a casual Twitter post about renewable energy with an accompanying image
python main.py --topic "renewable energy trends" --platform twitter --tone casual
```

The system will:
1. Research factual bullet points about your topic
2. Generate platform-specific content with the specified tone
3. Create an AI-generated image that complements the content

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
├── data/             # Generated output
│   └── images/       # Generated images
└── main.py          # CLI entrypoint
```

## Development

To contribute to this project:

1. Ensure you have Poetry installed
2. Make your changes following PEP 8 and project conventions
3. Run the application to test your changes
4. Add unit tests for new functionality

