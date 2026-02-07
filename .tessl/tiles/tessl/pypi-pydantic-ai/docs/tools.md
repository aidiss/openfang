# Tools and Function Calling

Flexible tool system enabling agents to call Python functions, access APIs, execute code, and perform web searches. Supports both built-in tools and custom function definitions with full type safety.

## Capabilities

### Tool Definition and Creation

Create custom tools from Python functions with automatic schema generation and type safety.

```python { .api }
class Tool[AgentDepsT]:
    """
    Tool implementation with typed dependencies.
    """
    def __init__(
        self,
        function: ToolFuncEither[AgentDepsT, Any],
        *,
        name: str | None = None,
        description: str | None = None,
        prepare: ToolPrepareFunc[AgentDepsT] | None = None
    ):
        """
        Create a tool from a function.
        
        Parameters:
        - function: Function to wrap as a tool
        - name: Override tool name (defaults to function name)
        - description: Override tool description (defaults to docstring)
        - prepare: Function to prepare tool before use
        """

def tool(
    function: ToolFuncEither[AgentDepsT, Any] | None = None,
    *,
    name: str | None = None,
    description: str | None = None,
    prepare: ToolPrepareFunc[AgentDepsT] | None = None
) -> Tool[AgentDepsT]:
    """
    Decorator to create a tool from a function.
    
    Parameters:
    - function: Function to wrap as a tool
    - name: Override tool name
    - description: Override tool description
    - prepare: Function to prepare tool before use
    
    Returns:
    Tool instance that can be used with agents
    """
```

### Run Context

Context object passed to tools providing access to dependencies and run metadata.

```python { .api }
class RunContext[AgentDepsT]:
    """
    Runtime context for tools and system prompt functions.
    """
    deps: AgentDepsT
    retry: int
    tool_name: str

    def set_messages(self, messages: list[ModelMessage]) -> None:
        """
        Set messages in the conversation history.
        
        Parameters:
        - messages: List of messages to add to conversation
        """
```

### Built-in Web Search Tool

Search the web and retrieve search results for agents.

```python { .api }
class WebSearchTool:
    """
    Web search functionality using DuckDuckGo.
    """
    def __init__(
        self,
        *,
        max_results: int = 5,
        request_timeout: float = 10.0
    ):
        """
        Initialize web search tool.
        
        Parameters:
        - max_results: Maximum number of search results to return
        - request_timeout: Request timeout in seconds
        """
    
    def search(
        self,
        query: str,
        *,
        user_location: WebSearchUserLocation | None = None
    ) -> list[dict[str, Any]]:
        """
        Search the web for the given query.
        
        Parameters:
        - query: Search query string
        - user_location: User location for localized results
        
        Returns:
        List of search result dictionaries with title, url, and snippet
        """

class WebSearchUserLocation(TypedDict):
    """Configuration for user location in web search."""
    country: str
    city: str | None
```

### Built-in Code Execution Tool

Execute Python code safely in a controlled environment.

```python { .api }
class CodeExecutionTool:
    """
    Code execution functionality with safety controls.
    """
    def __init__(
        self,
        *,
        timeout: float = 30.0,
        allowed_packages: list[str] | None = None
    ):
        """
        Initialize code execution tool.
        
        Parameters:
        - timeout: Maximum execution time in seconds
        - allowed_packages: List of allowed package imports (None = all allowed)
        """
    
    def execute(
        self,
        code: str,
        *,
        globals_dict: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Execute Python code and return results.
        
        Parameters:
        - code: Python code to execute
        - globals_dict: Global variables available to code
        
        Returns:
        Dictionary with 'result', 'output', and 'error' keys
        """
```

### Built-in URL Context Tool

Fetch and process content from URLs for agents.

```python { .api }
class UrlContextTool:
    """
    URL content access functionality.
    """
    def __init__(
        self,
        *,
        request_timeout: float = 10.0,
        max_content_length: int = 100000
    ):
        """
        Initialize URL context tool.
        
        Parameters:
        - request_timeout: Request timeout in seconds
        - max_content_length: Maximum content length to fetch
        """
    
    def fetch_url(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        Fetch content from a URL.
        
        Parameters:
        - url: URL to fetch content from
        
        Returns:
        Dictionary with content, title, and metadata
        """
```

### Tool Function Types

Type definitions for different kinds of tool functions.

```python { .api }
ToolFuncContext[AgentDepsT, ToolParams] = Callable[
    [RunContext[AgentDepsT], ToolParams],
    Awaitable[Any] | Any
]

ToolFuncPlain[ToolParams] = Callable[
    [ToolParams],
    Awaitable[Any] | Any
]

ToolFuncEither[AgentDepsT, ToolParams] = (
    ToolFuncContext[AgentDepsT, ToolParams] |
    ToolFuncPlain[ToolParams]
)

SystemPromptFunc[AgentDepsT] = Callable[
    [RunContext[AgentDepsT]],
    str | Awaitable[str]
]

ToolPrepareFunc[AgentDepsT] = Callable[
    [RunContext[AgentDepsT]],
    Any | Awaitable[Any]
]

ToolsPrepareFunc[AgentDepsT] = Callable[
    [RunContext[AgentDepsT]],
    list[Tool[AgentDepsT]] | Awaitable[list[Tool[AgentDepsT]]]
]
```

### Tool Schema Generation

Utilities for generating JSON schemas for tools.

```python { .api }
class GenerateToolJsonSchema:
    """JSON schema generator for tools."""
    
    def generate_schema(
        self,
        function: Callable,
        *,
        docstring_format: DocstringFormat = 'auto'
    ) -> ObjectJsonSchema:
        """
        Generate JSON schema for a tool function.
        
        Parameters:
        - function: Function to generate schema for
        - docstring_format: Format of function docstring
        
        Returns:
        JSON schema object describing the function
        """

ObjectJsonSchema = dict[str, Any]

class DocstringFormat(str, Enum):
    """Docstring format options."""
    GOOGLE = 'google'
    NUMPY = 'numpy'
    SPHINX = 'sphinx'
    AUTO = 'auto'
```

### Tool Definition Objects

Low-level tool definition objects for advanced use cases.

```python { .api }
class ToolDefinition:
    """
    Tool definition for models.
    """
    name: str
    description: str | None
    parameters_json_schema: ObjectJsonSchema
    outer_typed_dict_key: str | None

class ToolKind(str, Enum):
    """Tool types."""
    FUNCTION = 'function'
    OUTPUT = 'output'
    DEFERRED = 'deferred'
```

## Usage Examples

### Basic Function Tool

```python
from pydantic_ai import Agent, RunContext, tool

# Simple tool without dependencies
@tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    # In real implementation, call weather API
    return f"Weather in {location}: Sunny, 22°C"

agent = Agent(
    model='gpt-4',
    tools=[get_weather],
    system_prompt='You can help with weather queries.'
)

result = agent.run_sync('What is the weather in Paris?')
```

### Tool with Dependencies

```python
from pydantic_ai import Agent, RunContext, tool
from dataclasses import dataclass

@dataclass
class DatabaseDeps:
    database_url: str
    api_key: str

@tool
def get_user_info(ctx: RunContext[DatabaseDeps], user_id: int) -> str:
    """Get user information from database."""
    # Access dependencies through ctx.deps
    db_url = ctx.deps.database_url
    api_key = ctx.deps.api_key
    
    # Mock database query
    return f"User {user_id}: John Doe, email: john@example.com"

agent = Agent(
    model='gpt-4',
    tools=[get_user_info],
    deps_type=DatabaseDeps,
    system_prompt='You can help with user queries.'
)

deps = DatabaseDeps('postgresql://localhost', 'secret-key')
result = agent.run_sync('Get info for user 123', deps=deps)
```

### Built-in Tools Usage

```python
from pydantic_ai import Agent
from pydantic_ai.builtin_tools import WebSearchTool, CodeExecutionTool

# Agent with web search capability
search_tool = WebSearchTool(max_results=3)
agent = Agent(
    model='gpt-4',
    tools=[search_tool],
    system_prompt='You can search the web for current information.'
)

result = agent.run_sync('What are the latest Python releases?')

# Agent with code execution capability
code_tool = CodeExecutionTool(timeout=30.0)
agent = Agent(
    model='gpt-4',
    tools=[code_tool],
    system_prompt='You can execute Python code to solve problems.'
)

result = agent.run_sync('Calculate the factorial of 10')
```

### Multiple Tools

```python
from pydantic_ai import Agent, tool
from pydantic_ai.builtin_tools import WebSearchTool, CodeExecutionTool

@tool
def calculate_tax(income: float, tax_rate: float = 0.25) -> float:
    """Calculate tax amount based on income and tax rate."""
    return income * tax_rate

# Agent with multiple tools
agent = Agent(
    model='gpt-4',
    tools=[
        WebSearchTool(),
        CodeExecutionTool(),
        calculate_tax
    ],
    system_prompt='You are a financial assistant with web search and calculation capabilities.'
)

result = agent.run_sync(
    'Search for current tax rates and calculate tax on $50,000 income'
)
```

### Tool with Preparation

```python
from pydantic_ai import Agent, RunContext, tool

def prepare_database_connection(ctx: RunContext) -> dict:
    """Prepare database connection before tool use."""
    return {'connection': 'database-connection-object'}

@tool
def query_database(
    ctx: RunContext,
    query: str,
    prepared_data: dict = None
) -> str:
    """Query the database with prepared connection."""
    connection = prepared_data['connection']
    # Use connection to query database
    return f"Query result for: {query}"

database_tool = Tool(
    query_database,
    prepare=prepare_database_connection
)

agent = Agent(
    model='gpt-4',
    tools=[database_tool],
    system_prompt='You can query the database.'
)
```