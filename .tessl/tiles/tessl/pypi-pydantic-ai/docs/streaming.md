# Streaming and Async

Comprehensive streaming support for real-time interactions with immediate validation, delta updates, and event handling. Includes both async and sync streaming interfaces.

## Capabilities

### Agent Streaming

Stream agent responses in real-time with comprehensive event handling.

```python { .api }
class AgentStream[AgentDepsT, OutputDataT]:
    """
    Agent stream interface for real-time response processing.
    """
    async def __anext__(self) -> AgentStreamEvent[AgentDepsT, OutputDataT]:
        """
        Get next event from the stream.
        
        Returns:
        Next stream event (part delta, tool call, result, etc.)
        """
    
    async def get_final_result(self) -> FinalResult[OutputDataT]:
        """
        Get the final result after stream completion.
        
        Returns:
        Final result with complete data and metadata
        """

async def run_stream(
    self,
    user_prompt: str,
    *,
    message_history: list[ModelMessage] | None = None,
    deps: AgentDepsT = None,
    model_settings: ModelSettings | None = None
) -> AgentStream[AgentDepsT, OutputDataT]:
    """
    Run agent with streaming response.
    
    Parameters:
    - user_prompt: User's input message
    - message_history: Previous conversation messages
    - deps: Dependencies to pass to tools and system prompt
    - model_settings: Model settings for this run
    
    Returns:
    Async iterable stream of agent events
    """
```

### Streaming Results

Result objects for streaming operations.

```python { .api }
class StreamedRunResult[AgentDepsT, OutputDataT]:
    """
    Result from a streamed agent run.
    """
    def __init__(
        self,
        stream: AgentStream[AgentDepsT, OutputDataT],
        agent: AbstractAgent[AgentDepsT, OutputDataT]
    ): ...
    
    async def stream_events(self) -> AsyncIterator[AgentStreamEvent]: ...
    async def get_final_result(self) -> FinalResult[OutputDataT]: ...

class FinalResult[OutputDataT]:
    """
    Final result marker containing complete response data.
    """
    data: OutputDataT
    usage: RunUsage
    messages: list[ModelMessage]
    cost: float | None
```

### Model-Level Streaming

Direct model streaming interfaces for low-level control.

```python { .api }
class StreamedResponse:
    """
    Streamed model response for real-time processing.
    """
    async def __aiter__(self) -> AsyncIterator[ModelResponseStreamEvent]:
        """Iterate over streaming response events."""
    
    async def get_final_response(self) -> ModelResponse:
        """Get complete response after streaming finishes."""

class StreamedResponseSync:
    """
    Synchronous streamed response for non-async contexts.
    """
    def __iter__(self) -> Iterator[ModelResponseStreamEvent]:
        """Iterate over streaming response events synchronously."""
    
    def get_final_response(self) -> ModelResponse:
        """Get complete response after streaming finishes."""
```

### Direct Model Streaming Functions

Functions for direct model interaction with streaming.

```python { .api }
async def model_request_stream(
    model: Model,
    messages: list[ModelMessage],
    *,
    model_settings: ModelSettings | None = None
) -> StreamedResponse:
    """
    Make streaming request directly to model.
    
    Parameters:
    - model: Model to request from
    - messages: Conversation messages
    - model_settings: Model configuration
    
    Returns:
    Streaming response with real-time updates
    """

def model_request_stream_sync(
    model: Model,
    messages: list[ModelMessage],
    *,
    model_settings: ModelSettings | None = None
) -> StreamedResponseSync:
    """
    Make streaming request directly to model synchronously.
    
    Parameters:
    - model: Model to request from
    - messages: Conversation messages
    - model_settings: Model configuration
    
    Returns:
    Synchronous streaming response
    """
```

### Stream Event Types

Comprehensive event types for different streaming scenarios.

```python { .api }
class PartStartEvent:
    """Event fired when a new response part starts."""
    part: ModelResponsePart
    kind: Literal['part-start']

class PartDeltaEvent:
    """Event fired for incremental updates to response parts."""
    delta: ModelResponsePartDelta
    kind: Literal['part-delta']

class FinalResultEvent:
    """Event fired when final result is ready."""
    result: Any
    kind: Literal['final-result']

class FunctionToolCallEvent:
    """Event fired when function tool is called."""
    tool_name: str
    args: dict[str, Any]
    tool_id: str | None
    kind: Literal['function-tool-call']

class FunctionToolResultEvent:
    """Event fired when function tool returns result."""
    tool_name: str
    result: Any
    tool_id: str | None
    kind: Literal['function-tool-result']

class BuiltinToolCallEvent:
    """Event fired when built-in tool is called."""
    tool_name: str
    args: dict[str, Any]
    tool_id: str | None
    kind: Literal['builtin-tool-call']

class BuiltinToolResultEvent:
    """Event fired when built-in tool returns result."""
    tool_name: str
    result: Any
    tool_id: str | None
    kind: Literal['builtin-tool-result']

ModelResponseStreamEvent = PartStartEvent | PartDeltaEvent

HandleResponseEvent = (
    FunctionToolCallEvent |
    FunctionToolResultEvent |
    BuiltinToolCallEvent |
    BuiltinToolResultEvent
)

AgentStreamEvent = (
    ModelResponseStreamEvent |
    HandleResponseEvent |
    FinalResultEvent
)
```

### Delta Types

Delta update types for incremental streaming updates.

```python { .api }
class TextPartDelta:
    """Incremental text content update."""
    content: str
    kind: Literal['text']

class ThinkingPartDelta:
    """Incremental thinking content update (for reasoning models)."""
    content: str
    kind: Literal['thinking']

class ToolCallPartDelta:
    """Incremental tool call update."""
    tool_name: str | None
    args: dict[str, Any] | None
    tool_id: str | None
    kind: Literal['tool-call']

ModelResponsePartDelta = (
    TextPartDelta |
    ThinkingPartDelta |
    ToolCallPartDelta
)
```

### Stream Event Handlers

Event handler interfaces for processing streaming events.

```python { .api }
class EventStreamHandler[AgentDepsT]:
    """
    Handler for streaming events during agent execution.
    """
    async def on_model_request(
        self,
        messages: list[ModelMessage]
    ) -> None:
        """Called when model request is about to be made."""
    
    async def on_model_response_start(self) -> None:
        """Called when model response starts streaming."""
    
    async def on_model_response_part(
        self,
        part: ModelResponsePart
    ) -> None:
        """Called for each response part."""
    
    async def on_tool_call(
        self,
        tool_name: str,
        args: dict[str, Any]
    ) -> None:
        """Called when tool is about to be called."""
    
    async def on_tool_result(
        self,
        tool_name: str,
        result: Any
    ) -> None:
        """Called when tool returns result."""
```

## Usage Examples

### Basic Agent Streaming

```python
import asyncio
from pydantic_ai import Agent

agent = Agent(
    model='gpt-4',
    system_prompt='You are a helpful assistant.'
)

async def stream_response():
    stream = await agent.run_stream('Tell me a story about a robot')
    
    async for event in stream:
        if event.kind == 'part-delta' and event.delta.kind == 'text':
            # Print each text chunk as it arrives
            print(event.delta.content, end='', flush=True)
        elif event.kind == 'final-result':
            print(f"\n\nFinal result ready: {len(event.result)} characters")
            break

asyncio.run(stream_response())
```

### Streaming with Tool Calls

```python
import asyncio
from pydantic_ai import Agent, tool

@tool
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: Sunny, 22°C"

agent = Agent(
    model='gpt-4',
    tools=[get_weather],
    system_prompt='You can check weather using tools.'
)

async def stream_with_tools():
    stream = await agent.run_stream('What is the weather in Paris?')
    
    async for event in stream:
        if event.kind == 'part-delta':
            print(event.delta.content, end='', flush=True)
        elif event.kind == 'function-tool-call':
            print(f"\n[Calling tool: {event.tool_name}({event.args})]")
        elif event.kind == 'function-tool-result':
            print(f"[Tool result: {event.result}]")
        elif event.kind == 'final-result':
            print(f"\n\nComplete response: {event.result}")
            break

asyncio.run(stream_with_tools())
```

### Direct Model Streaming

```python
import asyncio
from pydantic_ai.models import OpenAIModel
from pydantic_ai.direct import model_request_stream
from pydantic_ai.messages import ModelRequest, UserPromptPart

async def direct_stream():
    model = OpenAIModel('gpt-4')
    messages = [ModelRequest([UserPromptPart('Count to 10')])]
    
    stream = await model_request_stream(model, messages)
    
    async for event in stream:
        if event.kind == 'part-delta' and event.delta.kind == 'text':
            print(event.delta.content, end='', flush=True)
    
    final_response = await stream.get_final_response()
    print(f"\n\nFinal response has {len(final_response.parts)} parts")

asyncio.run(direct_stream())
```

### Synchronous Streaming

```python
from pydantic_ai.models import OpenAIModel
from pydantic_ai.direct import model_request_stream_sync
from pydantic_ai.messages import ModelRequest, UserPromptPart

def sync_stream():
    model = OpenAIModel('gpt-4')
    messages = [ModelRequest([UserPromptPart('Write a haiku')])]
    
    stream = model_request_stream_sync(model, messages)
    
    for event in stream:
        if event.kind == 'part-delta' and event.delta.kind == 'text':
            print(event.delta.content, end='', flush=True)
    
    final_response = stream.get_final_response()
    print(f"\n\nComplete haiku received")

sync_stream()
```

### Streaming with Structured Output

```python
import asyncio
from pydantic_ai import Agent
from pydantic import BaseModel

class StoryInfo(BaseModel):
    title: str
    characters: list[str]
    setting: str
    plot_summary: str

agent = Agent(
    model='gpt-4',
    system_prompt='Create story information.',
    result_type=StoryInfo
)

async def stream_structured():
    stream = await agent.run_stream('Create a sci-fi story about time travel')
    
    text_content = ""
    async for event in stream:
        if event.kind == 'part-delta' and event.delta.kind == 'text':
            text_content += event.delta.content
            print(event.delta.content, end='', flush=True)
        elif event.kind == 'final-result':
            print(f"\n\nStructured result:")
            print(f"Title: {event.result.title}")
            print(f"Characters: {', '.join(event.result.characters)}")
            print(f"Setting: {event.result.setting}")
            break

asyncio.run(stream_structured())
```

### Advanced Event Handling

```python
import asyncio
from pydantic_ai import Agent, tool

@tool
def search_database(query: str) -> list[dict]:
    """Search database for information."""
    return [{"id": 1, "title": "Result 1"}, {"id": 2, "title": "Result 2"}]

agent = Agent(
    model='gpt-4',
    tools=[search_database],
    system_prompt='You can search for information.'
)

async def handle_all_events():
    stream = await agent.run_stream('Search for Python tutorials')
    
    tool_calls_made = 0
    text_chunks_received = 0
    
    async for event in stream:
        if event.kind == 'part-start':
            print(f"New part started: {event.part.kind}")
        elif event.kind == 'part-delta':
            text_chunks_received += 1
            if event.delta.kind == 'text':
                print(event.delta.content, end='', flush=True)
        elif event.kind == 'function-tool-call':
            tool_calls_made += 1
            print(f"\n[Tool call #{tool_calls_made}: {event.tool_name}]")
        elif event.kind == 'function-tool-result':
            print(f"[Got {len(event.result)} results]")
        elif event.kind == 'final-result':
            print(f"\n\nStream completed:")
            print(f"- Text chunks: {text_chunks_received}")
            print(f"- Tool calls: {tool_calls_made}")
            print(f"- Final result length: {len(event.result)}")
            break

asyncio.run(handle_all_events())
```

### Stream Error Handling

```python
import asyncio
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError, AgentRunError

agent = Agent(model='gpt-4')

async def stream_with_error_handling():
    try:
        stream = await agent.run_stream('Generate a very long response')
        
        async for event in stream:
            if event.kind == 'part-delta':
                print(event.delta.content, end='', flush=True)
            elif event.kind == 'final-result':
                print(f"\n\nSuccess! Result: {event.result[:100]}...")
                break
    
    except ModelHTTPError as e:
        print(f"Model HTTP error: {e}")
    except AgentRunError as e:
        print(f"Agent run error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(stream_with_error_handling())
```