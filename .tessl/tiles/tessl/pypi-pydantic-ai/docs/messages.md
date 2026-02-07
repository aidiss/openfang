# Messages and Media

Rich message system supporting text, images, audio, video, documents, and binary content. Includes comprehensive streaming support and delta updates for real-time interactions.

## Capabilities

### Message Structure

Core message types for agent-model communication.

```python { .api }
class ModelRequest:
    """
    Request message sent to a model.
    """
    parts: list[ModelRequestPart]
    kind: Literal['request']

class ModelResponse:
    """
    Response message received from a model.
    """
    parts: list[ModelResponsePart]
    timestamp: datetime
    kind: Literal['response']

ModelMessage = ModelRequest | ModelResponse

class ModelMessagesTypeAdapter:
    """
    Type adapter for serializing/deserializing model messages.
    """
    def validate_python(self, data: Any) -> list[ModelMessage]: ...
    def dump_python(self, messages: list[ModelMessage]) -> list[dict]: ...
```

### Request Message Parts

Parts that can be included in requests to models.

```python { .api }
class SystemPromptPart:
    """System prompt message part."""
    content: str
    kind: Literal['system-prompt']

class UserPromptPart:
    """User prompt message part."""
    content: str | list[UserContent]
    timestamp: datetime
    kind: Literal['user-prompt']

class ToolReturnPart:
    """Tool return message part."""
    tool_name: str
    content: Any
    tool_id: str | None
    timestamp: datetime
    kind: Literal['tool-return']

class BuiltinToolReturnPart:
    """Built-in tool return message part."""
    tool_name: str
    content: Any
    tool_id: str | None
    timestamp: datetime
    kind: Literal['builtin-tool-return']

class RetryPromptPart:
    """Retry prompt message part."""
    content: str
    tool_name: str | None
    tool_id: str | None
    timestamp: datetime
    kind: Literal['retry-prompt']

ModelRequestPart = (
    SystemPromptPart |
    UserPromptPart |
    ToolReturnPart |
    BuiltinToolReturnPart |
    RetryPromptPart
)
```

### Response Message Parts

Parts that can be included in responses from models.

```python { .api }
class TextPart:
    """Plain text response part."""
    content: str
    kind: Literal['text']

class ThinkingPart:
    """Thinking response part for reasoning models like o1."""
    content: str
    kind: Literal['thinking']

class ToolCallPart:
    """Tool call request part."""
    tool_name: str
    args: dict[str, Any]
    tool_id: str | None
    kind: Literal['tool-call']

class BuiltinToolCallPart:
    """Built-in tool call part."""
    tool_name: str
    args: dict[str, Any]
    tool_id: str | None
    kind: Literal['builtin-tool-call']

ModelResponsePart = (
    TextPart |
    ThinkingPart |
    ToolCallPart |
    BuiltinToolCallPart
)
```

### Media and File Types

Support for various media types and file content.

```python { .api }
class FileUrl:
    """Abstract base for URL-based files."""
    url: str

class ImageUrl(FileUrl):
    """Image file URL with format and media type."""
    def __init__(
        self,
        url: str,
        *,
        alt: str | None = None,
        media_type: ImageMediaType | None = None
    ):
        """
        Create image URL.
        
        Parameters:
        - url: URL to image file
        - alt: Alt text for accessibility
        - media_type: MIME type of image
        """

class AudioUrl(FileUrl):
    """Audio file URL with format and media type."""
    def __init__(
        self,
        url: str,
        *,
        media_type: AudioMediaType | None = None
    ):
        """
        Create audio URL.
        
        Parameters:
        - url: URL to audio file
        - media_type: MIME type of audio
        """

class VideoUrl(FileUrl):
    """Video file URL with format and media type."""
    def __init__(
        self,
        url: str,
        *,
        media_type: VideoMediaType | None = None
    ):
        """
        Create video URL.
        
        Parameters:
        - url: URL to video file
        - media_type: MIME type of video
        """

class DocumentUrl(FileUrl):
    """Document file URL with format."""
    def __init__(
        self,
        url: str,
        *,
        media_type: DocumentMediaType | None = None
    ):
        """
        Create document URL.
        
        Parameters:
        - url: URL to document file
        - media_type: MIME type of document
        """

class BinaryContent:
    """Binary file content with format and media type."""
    def __init__(
        self,
        data: bytes,
        media_type: str,
        *,
        filename: str | None = None
    ):
        """
        Create binary content.
        
        Parameters:
        - data: Binary file data
        - media_type: MIME type of content
        - filename: Optional filename
        """
```

### Media Type Definitions

Type definitions for supported media formats.

```python { .api }
AudioMediaType = Literal[
    'audio/mpeg',
    'audio/wav',
    'audio/ogg',
    'audio/mp4',
    'audio/webm',
    'audio/flac'
]

ImageMediaType = Literal[
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/svg+xml',
    'image/bmp'
]

VideoMediaType = Literal[
    'video/mp4',
    'video/webm',
    'video/ogg',
    'video/avi',
    'video/mov',
    'video/wmv'
]

DocumentMediaType = Literal[
    'application/pdf',
    'text/plain',
    'text/html',
    'text/markdown',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

AudioFormat = Literal['mp3', 'wav', 'ogg', 'mp4', 'webm', 'flac']
ImageFormat = Literal['jpeg', 'png', 'gif', 'webp', 'svg', 'bmp']
VideoFormat = Literal['mp4', 'webm', 'ogg', 'avi', 'mov', 'wmv']
DocumentFormat = Literal['pdf', 'txt', 'html', 'md', 'doc', 'docx']
```

### User Content Types

Types of content that can be included in user messages.

```python { .api }
UserContent = (
    str |
    ImageUrl |
    AudioUrl |
    VideoUrl |
    DocumentUrl |
    BinaryContent
)
```

### Tool Return Handling

Structured tool return objects for complex tool outputs.

```python { .api }
class ToolReturn:
    """
    Structured tool return with content.
    """
    def __init__(
        self,
        content: Any,
        *,
        metadata: dict[str, Any] | None = None
    ):
        """
        Create tool return.
        
        Parameters:
        - content: Return content from tool
        - metadata: Optional metadata about the return
        """
```

### Streaming Events

Event types for streaming responses and real-time updates.

```python { .api }
class PartStartEvent:
    """New part started event."""
    part: ModelResponsePart
    kind: Literal['part-start']

class PartDeltaEvent:
    """Part delta update event."""
    delta: ModelResponsePartDelta
    kind: Literal['part-delta']

class FinalResultEvent:
    """Final result ready event."""
    result: Any
    kind: Literal['final-result']

class FunctionToolCallEvent:
    """Function tool call event."""
    tool_name: str
    args: dict[str, Any]
    tool_id: str | None
    kind: Literal['function-tool-call']

class FunctionToolResultEvent:
    """Function tool result event."""
    tool_name: str
    result: Any
    tool_id: str | None
    kind: Literal['function-tool-result']

class BuiltinToolCallEvent:
    """Built-in tool call event."""
    tool_name: str
    args: dict[str, Any]
    tool_id: str | None
    kind: Literal['builtin-tool-call']

class BuiltinToolResultEvent:
    """Built-in tool result event."""
    tool_name: str
    result: Any
    tool_id: str | None
    kind: Literal['builtin-tool-result']

ModelResponseStreamEvent = (
    PartStartEvent |
    PartDeltaEvent
)

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

### Delta Types for Streaming

Delta update types for streaming responses.

```python { .api }
class TextPartDelta:
    """Text part delta update."""
    content: str
    kind: Literal['text']

class ThinkingPartDelta:
    """Thinking part delta update."""
    content: str
    kind: Literal['thinking']

class ToolCallPartDelta:
    """Tool call part delta update."""
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

## Usage Examples

### Basic Text Messages

```python
from pydantic_ai import Agent

agent = Agent(model='gpt-4', system_prompt='You are helpful.')

# Simple text interaction
result = agent.run_sync('Hello, how are you?')
print(result.data)
```

### Images in Messages

```python
from pydantic_ai import Agent, ImageUrl

agent = Agent(
    model='gpt-4-vision-preview',
    system_prompt='You can analyze images.'
)

# Send image with message
image = ImageUrl('https://example.com/image.jpg', alt='A sample image')
result = agent.run_sync(['Describe this image:', image])
print(result.data)
```

### Multiple Media Types

```python
from pydantic_ai import Agent, ImageUrl, AudioUrl, DocumentUrl

agent = Agent(
    model='gpt-4-turbo',
    system_prompt='You can process multiple media types.'
)

# Mix of text and media
content = [
    'Please analyze these files:',
    ImageUrl('https://example.com/chart.png'),
    AudioUrl('https://example.com/recording.mp3'),
    DocumentUrl('https://example.com/report.pdf')
]

result = agent.run_sync(content)
```

### Binary Content

```python
from pydantic_ai import Agent, BinaryContent

agent = Agent(model='gpt-4-vision-preview')

# Load image file as binary
with open('image.jpg', 'rb') as f:
    image_data = f.read()

binary_image = BinaryContent(
    data=image_data,
    media_type='image/jpeg',
    filename='image.jpg'
)

result = agent.run_sync(['Analyze this image:', binary_image])
```

### Message History

```python
from pydantic_ai import Agent
from pydantic_ai.messages import ModelRequest, UserPromptPart

agent = Agent(model='gpt-4')

# Create message history
message_history = [
    ModelRequest([
        UserPromptPart('What is the capital of France?')
    ])
]

# Continue conversation with history
result = agent.run_sync(
    'What about Germany?',
    message_history=message_history
)
```

### Streaming with Events

```python
from pydantic_ai import Agent

agent = Agent(model='gpt-4')

async def stream_example():
    stream = await agent.run_stream('Tell me a story')
    
    async for event in stream:
        if event.kind == 'part-delta':
            print(event.delta.content, end='', flush=True)
        elif event.kind == 'final-result':
            print(f"\n\nFinal result: {event.result}")
            break

# Run streaming example
import asyncio
asyncio.run(stream_example())
```