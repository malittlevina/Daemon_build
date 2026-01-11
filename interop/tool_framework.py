# interop/tool_framework.py
"""
Tool Framework - Extensible tool/function calling system

Provides:
- Tool registration and discovery
- Parameter validation
- Execution sandboxing
- Result formatting
- MCP-compatible interface
"""

from typing import Dict, Any, List, Optional, Callable, Type, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import inspect
import threading
import traceback


class ParameterType(Enum):
    """Supported parameter types."""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    param_type: ParameterType
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    items_type: Optional[ParameterType] = None  # For arrays
    properties: Optional[Dict[str, 'ToolParameter']] = None  # For objects


@dataclass
class ToolDefinition:
    """Complete definition of a tool."""
    name: str
    description: str
    parameters: List[ToolParameter]
    handler: Callable
    category: str = "general"
    requires_confirmation: bool = False
    timeout_seconds: float = 30.0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.param_type.value,
                "description": param.description
            }
            
            if param.enum:
                prop["enum"] = param.enum
            
            if param.param_type == ParameterType.ARRAY and param.items_type:
                prop["items"] = {"type": param.items_type.value}
            
            properties[param.name] = prop
            
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def to_mcp_schema(self) -> Dict[str, Any]:
        """Convert to MCP (Model Context Protocol) schema."""
        input_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param in self.parameters:
            input_schema["properties"][param.name] = {
                "type": param.param_type.value,
                "description": param.description
            }
            if param.required:
                input_schema["required"].append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": input_schema
        }


@dataclass
class ToolResult:
    """Result of a tool execution."""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool_name,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms
        }


class Tool:
    """Decorator for creating tools from functions."""
    
    def __init__(
        self,
        name: str = None,
        description: str = None,
        category: str = "general",
        requires_confirmation: bool = False,
        timeout_seconds: float = 30.0
    ):
        self.name = name
        self.description = description
        self.category = category
        self.requires_confirmation = requires_confirmation
        self.timeout_seconds = timeout_seconds
    
    def __call__(self, func: Callable) -> ToolDefinition:
        """Create ToolDefinition from decorated function."""
        name = self.name or func.__name__
        description = self.description or func.__doc__ or f"Execute {name}"
        
        # Extract parameters from function signature
        sig = inspect.signature(func)
        type_hints = getattr(func, '__annotations__', {})
        
        parameters = []
        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue
            
            # Determine type
            hint = type_hints.get(param_name, str)
            param_type = self._python_type_to_param_type(hint)
            
            # Check if required
            has_default = param.default != inspect.Parameter.empty
            
            parameters.append(ToolParameter(
                name=param_name,
                param_type=param_type,
                description=f"Parameter: {param_name}",
                required=not has_default,
                default=param.default if has_default else None
            ))
        
        return ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            handler=func,
            category=self.category,
            requires_confirmation=self.requires_confirmation,
            timeout_seconds=self.timeout_seconds
        )
    
    def _python_type_to_param_type(self, python_type: Type) -> ParameterType:
        """Convert Python type to ParameterType."""
        type_map = {
            str: ParameterType.STRING,
            int: ParameterType.INTEGER,
            float: ParameterType.NUMBER,
            bool: ParameterType.BOOLEAN,
            list: ParameterType.ARRAY,
            dict: ParameterType.OBJECT
        }
        
        # Handle Optional and other typing constructs
        origin = getattr(python_type, '__origin__', None)
        if origin is list:
            return ParameterType.ARRAY
        if origin is dict:
            return ParameterType.OBJECT
        
        return type_map.get(python_type, ParameterType.STRING)


class ToolRegistry:
    """
    Central registry for tools.
    
    Features:
    - Tool registration and discovery
    - Execution with validation
    - Execution history
    - Category-based organization
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._categories: Dict[str, List[str]] = {}
        self._execution_history: List[ToolResult] = []
        self._lock = threading.RLock()
        self._max_history = 500
        
        # Built-in tools
        self._register_builtin_tools()
    
    def register(self, tool: ToolDefinition) -> bool:
        """Register a tool."""
        with self._lock:
            self._tools[tool.name] = tool
            
            if tool.category not in self._categories:
                self._categories[tool.category] = []
            
            if tool.name not in self._categories[tool.category]:
                self._categories[tool.category].append(tool.name)
        
        print(f"[ToolRegistry] Registered tool: {tool.name} ({tool.category})")
        return True
    
    def register_function(
        self,
        func: Callable,
        name: str = None,
        description: str = None,
        **kwargs
    ) -> ToolDefinition:
        """Register a function as a tool."""
        decorator = Tool(name=name, description=description, **kwargs)
        tool = decorator(func)
        self.register(tool)
        return tool
    
    def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        with self._lock:
            if name in self._tools:
                tool = self._tools.pop(name)
                if tool.category in self._categories:
                    self._categories[tool.category] = [
                        t for t in self._categories[tool.category] if t != name
                    ]
                return True
            return False
    
    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(
        self,
        category: str = None,
        enabled_only: bool = True
    ) -> List[ToolDefinition]:
        """List available tools."""
        with self._lock:
            tools = list(self._tools.values())
            
            if category:
                tools = [t for t in tools if t.category == category]
            
            if enabled_only:
                tools = [t for t in tools if t.enabled]
            
            return tools
    
    def list_categories(self) -> List[str]:
        """List tool categories."""
        return list(self._categories.keys())
    
    def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        validate: bool = True
    ) -> ToolResult:
        """Execute a tool with given arguments."""
        import time
        
        start_time = time.time()
        
        # Get tool
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Tool not found: {tool_name}"
            )
        
        if not tool.enabled:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Tool is disabled: {tool_name}"
            )
        
        # Validate arguments
        if validate:
            validation_error = self._validate_arguments(tool, arguments)
            if validation_error:
                return ToolResult(
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=validation_error
                )
        
        # Execute with timeout
        try:
            # Apply defaults
            for param in tool.parameters:
                if param.name not in arguments and param.default is not None:
                    arguments[param.name] = param.default
            
            result = tool.handler(**arguments)
            
            execution_time = (time.time() - start_time) * 1000
            
            tool_result = ToolResult(
                tool_name=tool_name,
                success=True,
                result=result,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            tool_result = ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"{type(e).__name__}: {str(e)}",
                execution_time_ms=execution_time
            )
        
        # Record in history
        with self._lock:
            self._execution_history.append(tool_result)
            if len(self._execution_history) > self._max_history:
                self._execution_history = self._execution_history[-self._max_history:]
        
        return tool_result
    
    def _validate_arguments(
        self,
        tool: ToolDefinition,
        arguments: Dict[str, Any]
    ) -> Optional[str]:
        """Validate arguments against tool definition."""
        for param in tool.parameters:
            if param.required and param.name not in arguments:
                return f"Missing required parameter: {param.name}"
            
            if param.name in arguments:
                value = arguments[param.name]
                
                # Type checking
                if param.param_type == ParameterType.STRING and not isinstance(value, str):
                    return f"Parameter {param.name} must be a string"
                if param.param_type == ParameterType.INTEGER and not isinstance(value, int):
                    return f"Parameter {param.name} must be an integer"
                if param.param_type == ParameterType.NUMBER and not isinstance(value, (int, float)):
                    return f"Parameter {param.name} must be a number"
                if param.param_type == ParameterType.BOOLEAN and not isinstance(value, bool):
                    return f"Parameter {param.name} must be a boolean"
                if param.param_type == ParameterType.ARRAY and not isinstance(value, list):
                    return f"Parameter {param.name} must be an array"
                if param.param_type == ParameterType.OBJECT and not isinstance(value, dict):
                    return f"Parameter {param.name} must be an object"
                
                # Enum checking
                if param.enum and value not in param.enum:
                    return f"Parameter {param.name} must be one of: {param.enum}"
        
        return None
    
    def get_schemas(self, format: str = "openai") -> List[Dict[str, Any]]:
        """Get tool schemas in specified format."""
        tools = self.list_tools(enabled_only=True)
        
        if format == "openai":
            return [t.to_openai_schema() for t in tools]
        elif format == "mcp":
            return [t.to_mcp_schema() for t in tools]
        else:
            return [
                {
                    "name": t.name,
                    "description": t.description,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.param_type.value,
                            "required": p.required
                        }
                        for p in t.parameters
                    ]
                }
                for t in tools
            ]
    
    def get_execution_history(self, limit: int = 50) -> List[ToolResult]:
        """Get recent execution history."""
        with self._lock:
            return self._execution_history[-limit:]
    
    def _register_builtin_tools(self):
        """Register built-in tools."""
        
        @Tool(name="get_time", description="Get the current date and time", category="system")
        def get_time() -> str:
            return datetime.utcnow().isoformat()
        
        @Tool(name="calculate", description="Perform a mathematical calculation", category="math")
        def calculate(expression: str) -> float:
            # Safe evaluation of math expressions
            allowed = set("0123456789+-*/.() ")
            if not all(c in allowed for c in expression):
                raise ValueError("Invalid characters in expression")
            return eval(expression)
        
        @Tool(name="echo", description="Echo back the input", category="utility")
        def echo(message: str) -> str:
            return message
        
        self.register(get_time)
        self.register(calculate)
        self.register(echo)


# Global registry instance
_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _registry


def register_tool(func: Callable = None, **kwargs):
    """Decorator to register a function as a tool."""
    def decorator(f):
        return _registry.register_function(f, **kwargs)
    
    if func is not None:
        return decorator(func)
    return decorator


def execute_tool(name: str, arguments: Dict[str, Any]) -> ToolResult:
    """Execute a tool from the global registry."""
    return _registry.execute(name, arguments)
