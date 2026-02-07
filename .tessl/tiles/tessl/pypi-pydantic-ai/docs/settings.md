# Settings and Configuration

Model settings, usage tracking, and configuration options for fine-tuning agent behavior, monitoring resource consumption, and setting usage limits.

## Capabilities

### Model Settings

Comprehensive model configuration options for controlling generation behavior.

```python { .api }
class ModelSettings(TypedDict, total=False):
    """
    Configuration options for model behavior.
    All fields are optional and can be used to override default settings.
    """
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

def merge_model_settings(
    *settings: ModelSettings | None
) -> ModelSettings:
    """
    Merge multiple model settings configurations.
    
    Parameters:
    - settings: Variable number of ModelSettings to merge
    
    Returns:
    Merged ModelSettings with later settings overriding earlier ones
    """
```

### Usage Tracking

Comprehensive usage metrics and tracking for monitoring resource consumption.

```python { .api }
class RequestUsage:
    """
    Usage metrics for a single model request.
    """
    input_tokens: int | None
    output_tokens: int | None
    cache_creation_input_tokens: int | None
    cache_read_input_tokens: int | None
    audio_input_tokens: int | None
    audio_output_tokens: int | None
    audio_cache_creation_input_tokens: int | None
    audio_cache_read_input_tokens: int | None

    @property
    def total_tokens(self) -> int | None:
        """Total tokens used in this request."""

    def details(self) -> dict[str, int]:
        """Get detailed usage breakdown as dictionary."""

class RunUsage:
    """
    Usage metrics for an entire agent run.
    """
    request_count: int
    input_tokens: int | None
    output_tokens: int | None
    cache_creation_input_tokens: int | None
    cache_read_input_tokens: int | None
    audio_input_tokens: int | None
    audio_output_tokens: int | None
    audio_cache_creation_input_tokens: int | None
    audio_cache_read_input_tokens: int | None

    @property
    def total_tokens(self) -> int | None:
        """Total tokens used across all requests in run."""

    def details(self) -> dict[str, int | None]:
        """Get detailed usage breakdown as dictionary."""

    def __add__(self, other: RunUsage) -> RunUsage:
        """Add two RunUsage objects together."""

# Deprecated alias for backwards compatibility
Usage = RunUsage
```

### Usage Limits

Configuration for setting and enforcing usage limits.

```python { .api }
class UsageLimits:
    """
    Configuration for usage limits and quotas.
    """
    def __init__(
        self,
        *,
        request_limit: int | None = None,
        input_token_limit: int | None = None,
        output_token_limit: int | None = None,
        total_token_limit: int | None = None
    ):
        """
        Set usage limits for agent runs.
        
        Parameters:
        - request_limit: Maximum number of requests allowed
        - input_token_limit: Maximum input tokens allowed
        - output_token_limit: Maximum output tokens allowed
        - total_token_limit: Maximum total tokens allowed
        """

    def check_before_request(self, current_usage: RunUsage) -> None:
        """
        Check if a new request would exceed limits.
        
        Parameters:
        - current_usage: Current usage metrics
        
        Raises:
        UsageLimitExceeded: If limits would be exceeded
        """

    def check_after_request(
        self,
        current_usage: RunUsage,
        request_usage: RequestUsage
    ) -> None:
        """
        Check if usage limits have been exceeded after a request.
        
        Parameters:
        - current_usage: Current total usage
        - request_usage: Usage from the latest request
        
        Raises:
        UsageLimitExceeded: If limits have been exceeded
        """
```

### Timeout Configuration

Timeout handling for model requests.

```python { .api }
class Timeout:
    """
    Timeout configuration for model requests.
    """
    def __init__(
        self,
        *,
        connect: float | None = None,
        read: float | None = None,
        write: float | None = None,
        pool: float | None = None
    ):
        """
        Configure request timeouts.
        
        Parameters:
        - connect: Connection timeout in seconds
        - read: Read timeout in seconds
        - write: Write timeout in seconds
        - pool: Pool timeout in seconds
        """
```

### Instrumentation Settings

OpenTelemetry instrumentation configuration for monitoring and debugging.

```python { .api }
class InstrumentationSettings:
    """
    OpenTelemetry instrumentation configuration.
    """
    def __init__(
        self,
        *,
        capture_request_body: bool = True,
        capture_response_body: bool = True,
        capture_tool_calls: bool = True,
        capture_usage: bool = True,
        capture_model_name: bool = True
    ):
        """
        Configure OpenTelemetry instrumentation.
        
        Parameters:
        - capture_request_body: Whether to capture request bodies
        - capture_response_body: Whether to capture response bodies
        - capture_tool_calls: Whether to capture tool call details
        - capture_usage: Whether to capture usage metrics
        - capture_model_name: Whether to capture model names
        """
```

## Model Settings Details

### Core Generation Parameters

```python
# Temperature: Controls randomness (0.0 = deterministic, 2.0 = very random)
settings = ModelSettings(temperature=0.7)

# Max tokens: Maximum tokens to generate
settings = ModelSettings(max_tokens=1000)

# Top-p: Nucleus sampling parameter (0.1 = conservative, 1.0 = full vocabulary)
settings = ModelSettings(top_p=0.9)

# Seed: For reproducible outputs
settings = ModelSettings(seed=42)
```

### Advanced Parameters

```python
# Penalties: Control repetition (-2.0 to 2.0)
settings = ModelSettings(
    presence_penalty=0.5,    # Reduce likelihood of repeating topics
    frequency_penalty=0.3    # Reduce likelihood of repeating tokens
)

# Stop sequences: Strings that stop generation
settings = ModelSettings(stop_sequences=["END", "\n\n---"])

# Logit bias: Adjust token probabilities
settings = ModelSettings(
    logit_bias={
        "50256": -100,  # Strongly discourage specific token
        "1234": 20      # Strongly encourage specific token
    }
)
```

### Request Configuration

```python
# Timeout configuration
settings = ModelSettings(
    timeout=Timeout(
        connect=10.0,
        read=30.0,
        write=10.0
    )
)

# Tool calling configuration
settings = ModelSettings(parallel_tool_calls=True)

# Custom headers and body
settings = ModelSettings(
    extra_headers={"Custom-Header": "value"},
    extra_body={"custom_param": "value"}
)
```

## Usage Examples

### Basic Model Settings

```python
from pydantic_ai import Agent, ModelSettings

# Agent with custom model settings
settings = ModelSettings(
    temperature=0.2,        # More deterministic
    max_tokens=500,         # Limit response length
    top_p=0.9              # Slightly focused sampling
)

agent = Agent(
    model='gpt-4',
    system_prompt='You are a precise technical assistant.',
    model_settings=settings
)

result = agent.run_sync('Explain quantum computing')
```

### Runtime Model Settings Override

```python
from pydantic_ai import Agent, ModelSettings

agent = Agent(model='gpt-4')

# Override settings for specific run
creative_settings = ModelSettings(
    temperature=1.2,        # More creative
    top_p=0.95,            # Broader vocabulary
    max_tokens=1000
)

result = agent.run_sync(
    'Write a creative story',
    model_settings=creative_settings
)
```

### Usage Tracking

```python
from pydantic_ai import Agent

agent = Agent(model='gpt-4')
result = agent.run_sync('Hello, world!')

# Access usage information
usage = result.usage
print(f"Requests made: {usage.request_count}")
print(f"Input tokens: {usage.input_tokens}")
print(f"Output tokens: {usage.output_tokens}")
print(f"Total tokens: {usage.total_tokens}")

# Get detailed breakdown
details = usage.details()
print(f"Usage details: {details}")
```

### Usage Limits

```python
from pydantic_ai import Agent, UsageLimits
from pydantic_ai.exceptions import UsageLimitExceeded

# Set usage limits
limits = UsageLimits(
    request_limit=10,
    total_token_limit=5000
)

agent = Agent(
    model='gpt-4',
    usage_limits=limits
)

try:
    result = agent.run_sync('Generate a very long response')
    print(f"Tokens used: {result.usage.total_tokens}")
except UsageLimitExceeded as e:
    print(f"Usage limit exceeded: {e}")
```

### Merging Model Settings

```python
from pydantic_ai import Agent, ModelSettings, merge_model_settings

# Base settings
base_settings = ModelSettings(
    temperature=0.7,
    max_tokens=1000
)

# Override specific settings
override_settings = ModelSettings(
    temperature=0.2,  # Override temperature
    seed=42          # Add seed
)

# Merge settings
final_settings = merge_model_settings(base_settings, override_settings)
# Result: temperature=0.2, max_tokens=1000, seed=42

agent = Agent(
    model='gpt-4',
    model_settings=final_settings
)
```

### Custom Timeouts

```python
from pydantic_ai import Agent, ModelSettings, Timeout

# Custom timeout configuration
timeout_config = Timeout(
    connect=5.0,    # 5 seconds to connect
    read=60.0,      # 60 seconds to read response
    write=10.0      # 10 seconds to write request
)

settings = ModelSettings(timeout=timeout_config)

agent = Agent(
    model='gpt-4',
    model_settings=settings
)

# This agent will use the custom timeout settings
result = agent.run_sync('Generate a detailed explanation')
```

### Instrumentation Configuration

```python
from pydantic_ai import Agent, InstrumentationSettings

# Configure instrumentation
instrumentation = InstrumentationSettings(
    capture_request_body=True,
    capture_response_body=True,
    capture_tool_calls=True,
    capture_usage=True
)

agent = Agent(
    model='gpt-4',
    instrumented=instrumentation
)

# Agent will capture detailed telemetry data
result = agent.run_sync('Hello, world!')
```

### Production Configuration

```python
from pydantic_ai import Agent, ModelSettings, UsageLimits, Timeout

# Production-ready configuration
production_settings = ModelSettings(
    temperature=0.3,        # Consistent responses
    max_tokens=2000,        # Reasonable limit
    timeout=Timeout(
        connect=10.0,
        read=120.0          # Allow longer responses
    ),
    parallel_tool_calls=True,
    extra_headers={
        "User-Agent": "MyApp/1.0",
        "X-Request-ID": "unique-id"
    }
)

usage_limits = UsageLimits(
    request_limit=100,      # Max 100 requests per run
    total_token_limit=50000 # Max 50k tokens per run
)

agent = Agent(
    model='gpt-4',
    model_settings=production_settings,
    usage_limits=usage_limits,
    system_prompt='You are a production assistant.',
    retries=3               # Retry on failures
)

result = agent.run_sync('Process this user request')
print(f"Cost: ${result.cost:.4f}" if result.cost else "Cost not available")
```