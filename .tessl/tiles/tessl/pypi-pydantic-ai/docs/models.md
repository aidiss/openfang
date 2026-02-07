# Model Integration

Comprehensive model abstraction supporting 10+ LLM providers including OpenAI, Anthropic, Google, Groq, Cohere, Mistral, and more. Provides unified interface with provider-specific optimizations and fallback capabilities.

## Capabilities

### OpenAI Models

Integration with OpenAI's GPT models including GPT-4, GPT-3.5-turbo, and other OpenAI models.

```python { .api }
class OpenAIModel:
    """
    OpenAI model integration supporting GPT-4, GPT-3.5-turbo, and other OpenAI models.
    """
    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        openai_client: OpenAI | None = None,
        timeout: float | None = None
    ):
        """
        Initialize OpenAI model.
        
        Parameters:
        - model_name: OpenAI model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
        - api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        - base_url: Custom base URL for OpenAI API
        - openai_client: Pre-configured OpenAI client instance
        - timeout: Request timeout in seconds
        """
```

### Anthropic Models

Integration with Anthropic's Claude models including Claude-3.5, Claude-3, and other Anthropic models.

```python { .api }
class AnthropicModel:
    """
    Anthropic model integration supporting Claude-3.5, Claude-3, and other Anthropic models.
    """
    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        anthropic_client: Anthropic | None = None,
        timeout: float | None = None
    ):
        """
        Initialize Anthropic model.
        
        Parameters:
        - model_name: Anthropic model name (e.g., 'claude-3-5-sonnet-20241022')
        - api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        - base_url: Custom base URL for Anthropic API
        - anthropic_client: Pre-configured Anthropic client instance
        - timeout: Request timeout in seconds
        """
```

### Google Models

Integration with Google's Gemini and other Google AI models.

```python { .api }
class GeminiModel:
    """
    Google Gemini model integration.
    """
    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        timeout: float | None = None
    ):
        """
        Initialize Gemini model.
        
        Parameters:
        - model_name: Gemini model name (e.g., 'gemini-1.5-pro')
        - api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        - timeout: Request timeout in seconds
        """

class GoogleModel:
    """
    Google AI model integration for Vertex AI and other Google models.
    """
    def __init__(
        self,
        model_name: str,
        *,
        project_id: str | None = None,
        location: str = 'us-central1',
        credentials: dict | None = None,
        timeout: float | None = None
    ):
        """
        Initialize Google AI model.
        
        Parameters:
        - model_name: Google model name
        - project_id: Google Cloud project ID
        - location: Google Cloud region
        - credentials: Service account credentials
        - timeout: Request timeout in seconds
        """
```

### Other Model Providers

Support for additional LLM providers with consistent interface.

```python { .api }
class GroqModel:
    """
    Groq model integration for fast inference.
    """
    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        timeout: float | None = None
    ): ...

class CohereModel:
    """
    Cohere model integration.
    """
    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        timeout: float | None = None
    ): ...

class MistralModel:
    """
    Mistral AI model integration.
    """
    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        timeout: float | None = None
    ): ...

class HuggingFaceModel:
    """
    HuggingFace model integration.
    """
    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None
    ): ...
```

### AWS Bedrock Integration

Integration with AWS Bedrock for accessing various models through AWS infrastructure.

```python { .api }
class BedrockModel:
    """
    AWS Bedrock model integration.
    """
    def __init__(
        self,
        model_name: str,
        *,
        region: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
        profile: str | None = None,
        timeout: float | None = None
    ):
        """
        Initialize Bedrock model.
        
        Parameters:
        - model_name: Bedrock model ID
        - region: AWS region
        - aws_access_key_id: AWS access key
        - aws_secret_access_key: AWS secret key
        - aws_session_token: AWS session token
        - profile: AWS profile name
        - timeout: Request timeout in seconds
        """
```

### Model Abstractions

Core model interface and utilities for working with models.

```python { .api }
class Model:
    """
    Abstract model interface that all model implementations must follow.
    """
    def name(self) -> str: ...
    
    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None = None
    ) -> ModelResponse: ...
    
    async def request_stream(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None = None
    ) -> StreamedResponse: ...

class StreamedResponse:
    """
    Streamed model response for real-time processing.
    """
    async def __aiter__(self) -> AsyncIterator[ModelResponseStreamEvent]: ...
    
    async def get_final_response(self) -> ModelResponse: ...

class InstrumentedModel:
    """
    Model wrapper with OpenTelemetry instrumentation.
    """
    def __init__(
        self,
        model: Model,
        settings: InstrumentationSettings
    ): ...
```

### Model Utilities

Helper functions for working with models and model names.

```python { .api }
def infer_model(model: Model | KnownModelName) -> Model:
    """
    Infer model instance from string name or return existing model.
    
    Parameters:
    - model: Model instance or known model name string
    
    Returns:
    Model instance ready for use
    """

def instrument_model(
    model: Model,
    settings: InstrumentationSettings | None = None
) -> InstrumentedModel:
    """
    Add OpenTelemetry instrumentation to a model.
    
    Parameters:
    - model: Model to instrument
    - settings: Instrumentation configuration
    
    Returns:
    Instrumented model wrapper
    """
```

### Fallback Models

Model that automatically falls back to alternative models on failure.

```python { .api }
class FallbackModel:
    """
    Model that falls back to alternative models on failure.
    """
    def __init__(
        self,
        models: list[Model],
        *,
        max_retries: int = 3
    ):
        """
        Initialize fallback model.
        
        Parameters:
        - models: List of models to try in order
        - max_retries: Maximum retry attempts per model
        """
```

### Test Models

Models designed for testing and development.

```python { .api }
class TestModel:
    """
    Test model implementation for testing and development.
    """
    def __init__(
        self,
        *,
        custom_result_text: str | None = None,
        custom_result_tool_calls: list[ToolCallPart] | None = None,
        custom_result_structured: Any = None
    ):
        """
        Initialize test model with predefined responses.
        
        Parameters:
        - custom_result_text: Fixed text response
        - custom_result_tool_calls: Fixed tool calls to make
        - custom_result_structured: Fixed structured response
        """

class FunctionModel:
    """
    Function-based model for custom logic during testing.
    """
    def __init__(
        self,
        function: Callable[[list[ModelMessage]], ModelResponse | str],
        *,
        stream_function: Callable | None = None
    ):
        """
        Initialize function model.
        
        Parameters:
        - function: Function that processes messages and returns response
        - stream_function: Optional function for streaming responses
        """
```

### Known Model Names

Type alias for all supported model name strings.

```python { .api }
KnownModelName = Literal[
    # OpenAI models
    'gpt-4o',
    'gpt-4o-mini',
    'gpt-4-turbo',
    'gpt-4',
    'gpt-3.5-turbo',
    'o1-preview',
    'o1-mini',
    
    # Anthropic models
    'claude-3-5-sonnet-20241022',
    'claude-3-5-haiku-20241022',
    'claude-3-opus-20240229',
    'claude-3-sonnet-20240229',
    'claude-3-haiku-20240307',
    
    # Google models
    'gemini-1.5-pro',
    'gemini-1.5-flash',
    'gemini-1.0-pro',
    
    # And many more...
]
```

## Usage Examples

### Basic Model Usage

```python
from pydantic_ai import Agent
from pydantic_ai.models import OpenAIModel, AnthropicModel

# Using OpenAI
openai_agent = Agent(
    model=OpenAIModel('gpt-4'),
    system_prompt='You are a helpful assistant.'
)

# Using Anthropic
anthropic_agent = Agent(
    model=AnthropicModel('claude-3-5-sonnet-20241022'),
    system_prompt='You are a helpful assistant.'
)

# Using model name directly (auto-inferred)
agent = Agent(
    model='gpt-4',
    system_prompt='You are a helpful assistant.'
)
```

### Model with Custom Configuration

```python
from pydantic_ai.models import OpenAIModel

# Custom OpenAI configuration
model = OpenAIModel(
    'gpt-4',
    api_key='your-api-key',  # pragma: allowlist secret
    base_url='https://custom-endpoint.com/v1',
    timeout=30.0
)

agent = Agent(model=model, system_prompt='Custom configured agent.')
```

### Fallback Model Configuration

```python
from pydantic_ai.models import FallbackModel, OpenAIModel, AnthropicModel

# Create fallback model that tries OpenAI first, then Anthropic
fallback_model = FallbackModel([
    OpenAIModel('gpt-4'),
    AnthropicModel('claude-3-5-sonnet-20241022')
])

agent = Agent(
    model=fallback_model,
    system_prompt='Resilient agent with fallback.'
)
```

### Testing with Test Models

```python
from pydantic_ai.models import TestModel

# Test model with fixed response
test_model = TestModel(custom_result_text='Fixed test response')

agent = Agent(model=test_model, system_prompt='Test agent.')
result = agent.run_sync('Any input')
print(result.data)  # "Fixed test response"
```