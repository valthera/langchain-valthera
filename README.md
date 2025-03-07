# langchain-valthera

**langchain-valthera** is an open-source package that integrates LangChain with the Valthera framework, enabling smarter and more timely user engagement through LLM agents.

## Installation

Install the package via pip:

```bash
pip install -U langchain-valthera
```

Make sure to configure your credentials by setting the following environment variables:
* `OPENAI_API_KEY`: Your OpenAI API key
* Additional environment variables as needed for your data connectors

## Tools

The main component of the `langchain-valthera` package is the `ValtheraTool` which integrates with LangGraph agents.

```python
from langchain_valthera.tools import ValtheraTool
```

### Overview

langchain-valthera leverages data from multiple sources to compute real-time engagement metrics. By evaluating a user's context, the framework helps determine the right time and approach to interact with users, ensuring that engagement actions are both timely and context-aware.

### Key Components

* **Data Aggregator**: Collects and unifies data from various sources like HubSpot, PostHog, and Snowflake.
* **Scorer**: Computes user engagement scores (motivation and ability) based on configurable metrics.
* **Reasoning Engine**: Uses decision rules to determine the appropriate action (e.g., trigger engagement, improve motivation, or enhance ability).
* **Trigger Generator**: Crafts personalized messages or notifications for user engagement.

## Getting Started

Here's a quick example of how to set up and run the Valthera agent using LangGraph React:

```python
import os
from langchain_openai import ChatOpenAI
from langchain_valthera.tools import ValtheraTool
from langgraph.prebuilt import create_react_agent

# Initialize your data aggregator and configurations (replace with your implementations)
data_aggregator = ...  # e.g., DataAggregator(connectors=your_connectors)
motivation_config = ...  # Your motivation scoring configuration
ability_config = ...  # Your ability scoring configuration
reasoning_engine = ...  # Your ReasoningEngine instance
trigger_generator = ...  # Your TriggerGenerator instance

# Instantiate the Valthera tool
valthera_tool = ValtheraTool(
    data_aggregator=data_aggregator,
    motivation_config=motivation_config,
    ability_config=ability_config,
    reasoning_engine=reasoning_engine,
    trigger_generator=trigger_generator
)

# Create a LangGraph agent
llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.0, openai_api_key=os.environ.get("OPENAI_API_KEY"))
tools = [valthera_tool]
agent = create_react_agent(llm, tools=tools)

# Define input for testing
inputs = {
    "messages": [("user", "Evaluate behavior for user_12345: Finish Onboarding")]
}

# Run the agent and print the responses
for response in agent.stream(inputs, stream_mode="values"):
    print(response)
```

## Customization

Developers can easily extend and customize langchain-valthera to fit their needs:
* **Connectors**: Add or modify data connectors to pull information from different sources.
* **Scoring Configurations**: Adjust weights and transformation functions to match your business logic.
* **Decision Rules**: Define custom rules that determine which engagement action to trigger.