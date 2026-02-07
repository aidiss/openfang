# Output Types and Validation

Flexible output handling supporting structured data validation using Pydantic models, text outputs, tool-based outputs, and native model outputs with comprehensive type safety.

## Capabilities

### Structured Output Types

Output configuration classes that determine how agent responses are processed and validated.

```python { .api }
class ToolOutput[OutputDataT]:
    """
    Tool-based output configuration where tools generate the final result.
    """
    def __init__(
        self,
        tools: list[Tool],
        *,
        defer: bool = False
    ):
        """
        Configure tool-based output.
        
        Parameters:
        - tools: List of tools that can generate output
        - defer: Whether to defer tool execution
        """

class NativeOutput[OutputDataT]:
    """
    Native structured output configuration using model's built-in structured output.
    """
    pass

class PromptedOutput[OutputDataT]:
    """
    Prompted output configuration where model is prompted to return structured data.
    """
    pass

class TextOutput[OutputDataT]:
    """
    Text output configuration with optional conversion function.
    """
    def __init__(
        self,
        converter: TextOutputFunc[OutputDataT] | None = None
    ):
        """
        Configure text output.
        
        Parameters:
        - converter: Optional function to convert text to desired type
        """
```

### Deferred Tool Calls

Container for managing deferred tool execution.

```python { .api }
class DeferredToolCalls:
    """
    Container for deferred tool calls that can be executed later.
    """
    def __init__(self, tool_calls: list[ToolCallPart]): ...
    
    def execute_all(
        self,
        deps: Any = None
    ) -> list[Any]:
        """
        Execute all deferred tool calls.
        
        Parameters:
        - deps: Dependencies to pass to tools
        
        Returns:
        List of tool execution results
        """
```

### Structured Dictionary Factory

Factory function for creating structured dictionary types.

```python { .api }
def StructuredDict() -> type[dict[str, Any]]:
    """
    Create structured dictionary type for flexible output handling.
    
    Returns:
    Dictionary type that can be used as result_type for agents
    """
```

### Output Type Aliases

Type definitions for various output configurations and functions.

```python { .api }
OutputMode = Literal['tools', 'json', 'str']

StructuredOutputMode = Literal['json', 'str']

OutputSpec[T_co] = (
    type[T_co] |
    ToolOutput[T_co] |
    NativeOutput[T_co] |
    PromptedOutput[T_co] |
    TextOutput[T_co]
)

OutputTypeOrFunction[T_co] = (
    OutputSpec[T_co] |
    Callable[[str], T_co]
)

TextOutputFunc[T_co] = Callable[[str], T_co]
```

### Output Processing

Internal types and functions for output processing (advanced usage).

```python { .api }
class OutputTypeWrapper[T]:
    """Internal wrapper for output type processing."""
    def __init__(
        self,
        output_type: OutputSpec[T],
        allow_text_output: bool = True
    ): ...
    
    def validate_output(self, data: Any) -> T: ...
    def get_output_mode(self) -> OutputMode: ...
```

## Usage Examples

### Basic Structured Output with Pydantic

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class WeatherInfo(BaseModel):
    location: str
    temperature: float
    condition: str
    humidity: int

# Agent with structured output
agent = Agent(
    model='gpt-4',
    system_prompt='Extract weather information from text.',
    result_type=WeatherInfo
)

result = agent.run_sync(
    'The weather in Paris is sunny, 22°C with 65% humidity'
)

print(result.data.location)     # "Paris"
print(result.data.temperature)  # 22.0
print(result.data.condition)    # "sunny"
print(result.data.humidity)     # 65
```

### Tool-Based Output

```python
from pydantic_ai import Agent, ToolOutput, tool

@tool
def calculate_result(numbers: list[float], operation: str) -> float:
    """Perform calculation on numbers."""
    if operation == 'sum':
        return sum(numbers)
    elif operation == 'average':
        return sum(numbers) / len(numbers)
    elif operation == 'max':
        return max(numbers)
    else:
        raise ValueError(f"Unknown operation: {operation}")

# Agent with tool-based output
agent = Agent(
    model='gpt-4',
    system_prompt='Use tools to calculate results.',
    result_type=ToolOutput([calculate_result])
)

result = agent.run_sync('Calculate the average of 10, 20, 30, 40')
print(result.data)  # 25.0
```

### Text Output with Conversion

```python
from pydantic_ai import Agent, TextOutput
import json

def parse_json_response(text: str) -> dict:
    """Parse JSON from model response."""
    # Extract JSON from text if needed
    start = text.find('{')
    end = text.rfind('}') + 1
    json_str = text[start:end]
    return json.loads(json_str)

# Agent with text output conversion
agent = Agent(
    model='gpt-4',
    system_prompt='Return responses as JSON.',
    result_type=TextOutput(parse_json_response)
)

result = agent.run_sync('Create a person object with name and age')
print(result.data)  # {'name': 'John Doe', 'age': 30}
```

### Structured Dictionary Output

```python
from pydantic_ai import Agent, StructuredDict

# Agent with flexible dictionary output
agent = Agent(
    model='gpt-4',
    system_prompt='Return structured data as a dictionary.',
    result_type=StructuredDict()
)

result = agent.run_sync('Create a product with name, price, and category')
print(result.data)  # {'name': 'Laptop', 'price': 999.99, 'category': 'Electronics'}
```

### Native vs Prompted Output

```python
from pydantic_ai import Agent, NativeOutput, PromptedOutput
from pydantic import BaseModel

class TaskInfo(BaseModel):
    title: str
    priority: int
    completed: bool

# Native structured output (uses model's built-in structured output)
native_agent = Agent(
    model='gpt-4',
    system_prompt='Create task information.',
    result_type=NativeOutput[TaskInfo]
)

# Prompted structured output (prompts model to return structured data)
prompted_agent = Agent(
    model='gpt-4', 
    system_prompt='Create task information.',
    result_type=PromptedOutput[TaskInfo]
)

# Both work similarly but use different underlying mechanisms
result1 = native_agent.run_sync('Create a high priority task for code review')
result2 = prompted_agent.run_sync('Create a high priority task for code review')

print(result1.data.title)      # "Code Review"
print(result1.data.priority)   # 3
print(result1.data.completed)  # False
```

### Deferred Tool Execution

```python
from pydantic_ai import Agent, ToolOutput, tool

@tool
def expensive_calculation(data: list[int]) -> int:
    """Perform expensive calculation."""
    # Simulate expensive operation
    return sum(x ** 2 for x in data)

# Agent with deferred tool execution
agent = Agent(
    model='gpt-4',
    system_prompt='Plan calculations but defer execution.',
    result_type=ToolOutput([expensive_calculation], defer=True)
)

result = agent.run_sync('Plan calculation for numbers 1 through 100')

# result.data is now DeferredToolCalls
if isinstance(result.data, DeferredToolCalls):
    # Execute when ready
    actual_results = result.data.execute_all()
    print(actual_results[0])  # Result of expensive calculation
```

### Complex Nested Output

```python
from pydantic_ai import Agent
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class Person(BaseModel):
    name: str
    age: int
    email: str
    addresses: List[Address]

class Company(BaseModel):
    name: str
    employees: List[Person]
    headquarters: Address

# Agent with complex nested output
agent = Agent(
    model='gpt-4',
    system_prompt='Extract company information.',
    result_type=Company
)

result = agent.run_sync('''
Create a company called TechCorp with headquarters in San Francisco.
Include 2 employees: John (30, john@techcorp.com) and Jane (28, jane@techcorp.com).
''')

print(result.data.name)  # "TechCorp"
print(len(result.data.employees))  # 2
print(result.data.employees[0].name)  # "John"
print(result.data.headquarters.city)  # "San Francisco"
```

### Custom Validation

```python
from pydantic_ai import Agent
from pydantic import BaseModel, validator

class ValidatedOutput(BaseModel):
    score: float
    grade: str
    
    @validator('score')
    def score_must_be_valid(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Score must be between 0 and 100')
        return v
    
    @validator('grade')
    def grade_must_match_score(cls, v, values):
        score = values.get('score', 0)
        expected_grades = {
            (90, 100): 'A',
            (80, 89): 'B', 
            (70, 79): 'C',
            (60, 69): 'D',
            (0, 59): 'F'
        }
        
        for (min_score, max_score), expected_grade in expected_grades.items():
            if min_score <= score <= max_score:
                if v != expected_grade:
                    raise ValueError(f'Grade {v} does not match score {score}')
                break
        return v

# Agent with custom validation
agent = Agent(
    model='gpt-4',
    system_prompt='Grade student performance.',
    result_type=ValidatedOutput
)

result = agent.run_sync('Student scored 85 points on the exam')
print(result.data.score)  # 85.0
print(result.data.grade)  # "B"
```