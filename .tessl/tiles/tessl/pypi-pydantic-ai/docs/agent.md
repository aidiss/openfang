# Core Agent Framework

The foundational agent system for creating AI agents with typed dependencies, structured outputs, and comprehensive error handling. The Agent class is the central component that orchestrates interactions between users, models, and tools.

## Capabilities

### Agent Creation and Configuration

Create agents with flexible configuration options including model selection, system prompts, result types, tools, and dependency injection.

```python { .api }
class Agent[AgentDepsT, OutputDataT]:
    """
    Main agent class for building AI agents.
    
    Type Parameters:
    - AgentDepsT: Type of dependencies passed to tools and system prompt functions
    - OutputDataT: Type of the agent's output data
    """
    def __init__(
        self,
        model: Model | KnownModelName | str | None = None,
        *,
        output_type: OutputSpec[OutputDataT] = str,
        instructions: str | SystemPromptFunc[AgentDepsT] | Sequence[str | SystemPromptFunc[AgentDepsT]] | None = None,
        system_prompt: str | Sequence[str] = (),
        deps_type: type[AgentDepsT] = NoneType,
        name: str | None = None,
        model_settings: ModelSettings | None = None,
        retries: int = 1,
        output_retries: int | None = None,
        tools: Sequence[Tool[AgentDepsT] | ToolFuncEither[AgentDepsT, ...]] = (),
        builtin_tools: Sequence[AbstractBuiltinTool] = (),
        prepare_tools: ToolsPrepareFunc[AgentDepsT] | None = None,
        prepare_output_tools: ToolsPrepareFunc[AgentDepsT] | None = None,
        toolsets: Sequence[AbstractToolset[AgentDepsT] | ToolsetFunc[AgentDepsT]] | None = None,
        defer_model_check: bool = False
    ):
        """
        Initialize an agent.
        
        Parameters:
        - model: Model instance, known model name, or string (can be None)
        - output_type: Expected output specification (replaces result_type)
        - instructions: Main instruction string or function (replaces system_prompt as primary)
        - system_prompt: Additional system prompt strings
        - deps_type: Type of dependencies for type checking
        - name: Optional name for the agent
        - model_settings: Default model settings
        - retries: Number of retries on failure
        - output_retries: Number of retries for output validation
        - tools: Sequence of tools available to the agent
        - builtin_tools: Sequence of built-in tools
        - prepare_tools: Function to prepare tools before use
        - prepare_output_tools: Function to prepare output tools
        - toolsets: Sequence of toolsets for advanced tool management
        - defer_model_check: Whether to defer model validation
        """
```

### Synchronous Execution

Run agents synchronously for simple use cases and testing.

```python { .api }
def run_sync(
    self,
    user_prompt: str,
    *,
    message_history: list[ModelMessage] | None = None,
    deps: AgentDepsT = None,
    model_settings: ModelSettings | None = None
) -> AgentRunResult[OutputDataT]:
    """
    Run the agent synchronously.
    
    Parameters:
    - user_prompt: User's input message
    - message_history: Previous conversation messages
    - deps: Dependencies to pass to tools and system prompt
    - model_settings: Model settings for this run
    
    Returns:
    AgentRunResult containing the agent's response and metadata
    """
```

### Asynchronous Execution

Run agents asynchronously for production applications and concurrent operations.

```python { .api }
async def run(
    self,
    user_prompt: str,
    *,
    message_history: list[ModelMessage] | None = None,
    deps: AgentDepsT = None,
    model_settings: ModelSettings | None = None
) -> AgentRunResult[OutputDataT]:
    """
    Run the agent asynchronously.
    
    Parameters:
    - user_prompt: User's input message
    - message_history: Previous conversation messages
    - deps: Dependencies to pass to tools and system prompt
    - model_settings: Model settings for this run
    
    Returns:
    AgentRunResult containing the agent's response and metadata
    """
```

### Agent Run Management

Stateful agent runs that can be iterated over for step-by-step execution.

```python { .api }
class AgentRun[AgentDepsT, OutputDataT]:
    """
    Stateful, async-iterable run of an agent.
    """
    def __init__(
        self,
        agent: AbstractAgent[AgentDepsT, OutputDataT],
        user_prompt: str,
        *,
        message_history: list[ModelMessage] | None = None,
        deps: AgentDepsT = None,
        model_settings: ModelSettings | None = None
    ): ...

    async def __anext__(self) -> None:
        """Advance the run by one step."""

    async def final_result(self) -> AgentRunResult[OutputDataT]:
        """Get the final result after completion."""
```

### Result Handling

Comprehensive result objects containing agent responses, usage metrics, and execution metadata.

```python { .api }
class AgentRunResult[OutputDataT]:
    """
    Result from completed agent run.
    """
    data: OutputDataT
    usage: RunUsage
    messages: list[ModelMessage]
    cost: float | None
    timestamp: datetime

    def is_complete(self) -> bool:
        """Check if the run completed successfully."""

    def new_messages(self) -> list[ModelMessage]:
        """Get only new messages from this run."""
```

### Agent Variants

Specialized agent implementations for specific use cases.

```python { .api }
class WrapperAgent[AgentDepsT, OutputDataT]:
    """
    Agent wrapper implementation for extending functionality.
    """
    def __init__(
        self,
        wrapped_agent: AbstractAgent[AgentDepsT, OutputDataT]
    ): ...

class AbstractAgent[AgentDepsT, OutputDataT]:
    """
    Abstract base class for all agent implementations.
    """
    def model_name(self) -> str: ...
    def deps_type(self) -> type[AgentDepsT]: ...
    def result_type(self) -> type[OutputDataT]: ...
```

### Message Capture

Utilities for capturing and analyzing agent run messages for debugging and monitoring.

```python { .api }
def capture_run_messages(
    agent: Agent[AgentDepsT, OutputDataT],
    user_prompt: str,
    *,
    deps: AgentDepsT = None,
    model_settings: ModelSettings | None = None
) -> list[ModelMessage]:
    """
    Capture messages from an agent run for debugging.
    
    Parameters:
    - agent: Agent to run
    - user_prompt: User's input message
    - deps: Dependencies to pass to the agent
    - model_settings: Model settings for the run
    
    Returns:
    List of all messages from the agent run
    """
```

### End Strategies

Configuration for handling tool calls when a final result is found.

```python { .api }
class EndStrategy(str, Enum):
    """
    Strategy for handling tool calls when final result found.
    """
    EARLY = 'early'  # End immediately when result found
    EXHAUST_TOOLS = 'exhaust_tools'  # Complete all pending tool calls
```

## Usage Examples

### Basic Agent

```python
from pydantic_ai import Agent
from pydantic_ai.models import OpenAIModel

# Create a simple agent
agent = Agent(
    model=OpenAIModel('gpt-4'),
    system_prompt='You are a helpful math tutor.'
)

# Run synchronously
result = agent.run_sync('What is 15 * 23?')
print(result.data)  # "345"
```

### Agent with Dependencies

```python
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass

@dataclass
class DatabaseDeps:
    database_url: str
    api_key: str

def get_user_info(ctx: RunContext[DatabaseDeps], user_id: int) -> str:
    # Access dependencies through ctx.deps
    db_url = ctx.deps.database_url
    api_key = ctx.deps.api_key
    # Fetch user info from database
    return f"User {user_id} info from {db_url}"

agent = Agent(
    model=OpenAIModel('gpt-4'),
    system_prompt='You help with user queries.',
    tools=[get_user_info],
    deps_type=DatabaseDeps
)

deps = DatabaseDeps('postgresql://...', 'secret-key')
result = agent.run_sync('Get info for user 123', deps=deps)
```

### Structured Output Agent

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class WeatherInfo(BaseModel):
    location: str
    temperature: float
    condition: str
    humidity: int

agent = Agent(
    model=OpenAIModel('gpt-4'),
    system_prompt='Extract weather information.',
    result_type=WeatherInfo
)

result = agent.run_sync('The weather in Paris is sunny, 22°C with 65% humidity')
print(result.data.location)  # "Paris"
print(result.data.temperature)  # 22.0
```