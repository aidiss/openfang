# Pydantic AI

A comprehensive Python agent framework designed to make building production-grade applications with Generative AI less painful and more ergonomic. Built by the Pydantic team, Pydantic AI offers a FastAPI-like development experience for GenAI applications, featuring model-agnostic support for major LLM providers, seamless Pydantic Logfire integration for debugging and monitoring, type-safe design with powerful static type checking, Python-centric control flow, structured response validation using Pydantic models, optional dependency injection system for testable and maintainable code, streaming capabilities with immediate validation, and graph support for complex application flows.

## Package Information

- **Package Name**: pydantic-ai
- **Language**: Python
- **Installation**: `pip install pydantic-ai`
- **Requirements**: Python 3.9+

## Core Imports

```python
from pydantic_ai import Agent
```

Common imports for building agents:

```python
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models import OpenAIModel, AnthropicModel
```

For structured outputs:

```python
from pydantic_ai import Agent, StructuredDict
from pydantic import BaseModel
```

## Basic Usage

```python
from pydantic_ai import Agent
from pydantic_ai.models import OpenAIModel

# Create a simple agent
agent = Agent(
    model=OpenAIModel('gpt-4'),
    instructions='You are a helpful assistant.'
)

# Run the agent
result = agent.run_sync('What is the capital of France?')
print(result.data)
# Output: Paris

# Create an agent with structured output
from pydantic import BaseModel

class CityInfo(BaseModel):
    name: str
    country: str
    population: int

agent = Agent(
    model=OpenAIModel('gpt-4'),
    instructions='Extract city information.',
    output_type=CityInfo
)

result = agent.run_sync('Tell me about Tokyo')
print(result.data.name)  # Tokyo
print(result.data.population)  # 37,000,000
```

## Architecture

Pydantic AI is built around several key components that work together to provide a flexible and type-safe agent framework:

- **Agent**: The central class that orchestrates interactions between users, models, and tools
- **Models**: Abstraction layer supporting 10+ LLM providers (OpenAI, Anthropic, Google, etc.)
- **Tools**: Function-based capabilities that agents can call to perform actions
- **Messages**: Rich message system supporting text, images, audio, video, and documents
- **Output Types**: Flexible output handling including structured data, text, and tool-based outputs
- **Run Context**: Dependency injection system for testable and maintainable code
- **Streaming**: Real-time response processing with immediate validation

This architecture enables building production-grade AI applications with full type safety, comprehensive error handling, and seamless integration with the Python ecosystem.

## Capabilities

### Core Agent Framework

The foundational agent system for creating AI agents with typed dependencies, structured outputs, and comprehensive error handling. Includes the main Agent class, run management, and result handling.

```python { .api }
class Agent[AgentDepsT, OutputDataT]:
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
    ): ...

    def run_sync(
        self,
        user_prompt: str,
        *,
        message_history: list[ModelMessage] | None = None,
        deps: AgentDepsT = None,
        model_settings: ModelSettings | None = None
    ) -> AgentRunResult[OutputDataT]: ...

    async def run(
        self,
        user_prompt: str,
        *,
        message_history: list[ModelMessage] | None = None,
        deps: AgentDepsT = None,
        model_settings: ModelSettings | None = None
    ) -> AgentRunResult[OutputDataT]: ...
```

[Core Agent Framework](./agent.md)

### Model Integration

Comprehensive model abstraction supporting 10+ LLM providers including OpenAI, Anthropic, Google, Groq, Cohere, Mistral, and more. Provides unified interface with provider-specific optimizations and fallback capabilities.

```python { .api }
class OpenAIModel:
    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        openai_client: OpenAI | None = None,
        timeout: float | None = None
    ): ...

class AnthropicModel:
    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        anthropic_client: Anthropic | None = None,
        timeout: float | None = None
    ): ...

def infer_model(model: Model | KnownModelName) -> Model: ...
```

[Model Integration](./models.md)

### Tools and Function Calling

Flexible tool system enabling agents to call Python functions, access APIs, execute code, and perform web searches. Supports both built-in tools and custom function definitions with full type safety.

```python { .api }
class Tool[AgentDepsT]:
    def __init__(
        self,
        function: ToolFuncEither[AgentDepsT, Any],
        *,
        name: str | None = None,
        description: str | None = None,
        prepare: ToolPrepareFunc[AgentDepsT] | None = None
    ): ...

class RunContext[AgentDepsT]:
    deps: AgentDepsT
    retry: int
    tool_name: str

    def set_messages(self, messages: list[ModelMessage]) -> None: ...

class WebSearchTool:
    def __init__(
        self,
        *,
        max_results: int = 5,
        request_timeout: float = 10.0
    ): ...

class CodeExecutionTool:
    def __init__(
        self,
        *,
        timeout: float = 30.0,
        allowed_packages: list[str] | None = None
    ): ...
```

[Tools and Function Calling](./tools.md)

### Messages and Media

Rich message system supporting text, images, audio, video, documents, and binary content. Includes comprehensive streaming support and delta updates for real-time interactions.

```python { .api }
class ImageUrl:
    def __init__(
        self,
        url: str,
        *,
        alt: str | None = None,
        media_type: ImageMediaType | None = None
    ): ...

class AudioUrl:
    def __init__(
        self,
        url: str,
        *,
        media_type: AudioMediaType | None = None
    ): ...

class ModelRequest:
    parts: list[ModelRequestPart]
    kind: Literal['request']

class ModelResponse:
    parts: list[ModelResponsePart]
    timestamp: datetime
    kind: Literal['response']
```

[Messages and Media](./messages.md)

### Output Types and Validation

Flexible output handling supporting structured data validation using Pydantic models, text outputs, tool-based outputs, and native model outputs with comprehensive type safety.

```python { .api }
class ToolOutput[OutputDataT]:
    tools: list[Tool]
    defer: bool = False

class NativeOutput[OutputDataT]:
    ...

class PromptedOutput[OutputDataT]:
    ...

class TextOutput[OutputDataT]:
    converter: TextOutputFunc[OutputDataT] | None = None

def StructuredDict() -> type[dict[str, Any]]: ...
```

[Output Types and Validation](./output.md)

### Streaming and Async

Comprehensive streaming support for real-time interactions with immediate validation, delta updates, and event handling. Includes both async and sync streaming interfaces.

```python { .api }
class AgentStream[AgentDepsT, OutputDataT]:
    async def __anext__(self) -> AgentStreamEvent[AgentDepsT, OutputDataT]: ...
    
    async def get_final_result(self) -> FinalResult[OutputDataT]: ...

async def run_stream(
    self,
    user_prompt: str,
    *,
    message_history: list[ModelMessage] | None = None,
    deps: AgentDepsT = None,
    model_settings: ModelSettings | None = None
) -> AgentStream[AgentDepsT, OutputDataT]: ...
```

[Streaming and Async](./streaming.md)

### Settings and Configuration

Model settings, usage tracking, and configuration options for fine-tuning agent behavior, monitoring resource consumption, and setting usage limits.

```python { .api }
class ModelSettings(TypedDict, total=False):
    max_tokens: int
    temperature: float
    top_p: float
    timeout: float | Timeout
    parallel_tool_calls: bool
    seed: int
    presence_penalty: float
    frequency_penalty: float
    logit_bias: dict[str, int]
    stop_sequences: list[str]
    extra_headers: dict[str, str]
    extra_body: object

class RunUsage:
    request_count: int
    input_tokens: int | None
    output_tokens: int | None
    cache_creation_input_tokens: int | None
    cache_read_input_tokens: int | None
    total_tokens: int | None

class UsageLimits:
    request_limit: int | None = None
    input_token_limit: int | None = None
    output_token_limit: int | None = None
    total_token_limit: int | None = None
```

[Settings and Configuration](./settings.md)