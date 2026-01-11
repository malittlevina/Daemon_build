# interop/api_server.py
"""
API Server - REST API for remote ThothOS access

Provides HTTP endpoints for:
- Chat and completion
- Tool execution
- Memory operations
- System status and control
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import threading
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import traceback


@dataclass
class APIResponse:
    """Standard API response."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_json(self) -> str:
        return json.dumps({
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp
        })


class ThothAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for ThothOS API."""
    
    # Reference to API server (set by APIServer)
    api_server = None
    
    def log_message(self, format, *args):
        """Override to use custom logging."""
        if self.api_server and self.api_server.verbose:
            print(f"[API] {args[0]}")
    
    def send_json_response(self, response: APIResponse, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(response.to_json().encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        try:
            if path == "/":
                self._handle_root()
            elif path == "/health":
                self._handle_health()
            elif path == "/status":
                self._handle_status()
            elif path == "/tools":
                self._handle_list_tools()
            elif path == "/modules":
                self._handle_list_modules()
            elif path == "/memory":
                self._handle_memory_query(query)
            else:
                self.send_json_response(
                    APIResponse(success=False, error=f"Unknown endpoint: {path}"),
                    status=404
                )
        except Exception as e:
            self.send_json_response(
                APIResponse(success=False, error=str(e)),
                status=500
            )
    
    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length else "{}"
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json_response(
                APIResponse(success=False, error="Invalid JSON"),
                status=400
            )
            return
        
        try:
            if path == "/chat":
                self._handle_chat(data)
            elif path == "/complete":
                self._handle_complete(data)
            elif path == "/think":
                self._handle_think(data)
            elif path == "/tools/execute":
                self._handle_execute_tool(data)
            elif path == "/plan":
                self._handle_plan(data)
            elif path == "/memory/store":
                self._handle_memory_store(data)
            elif path == "/reflect":
                self._handle_reflect()
            else:
                self.send_json_response(
                    APIResponse(success=False, error=f"Unknown endpoint: {path}"),
                    status=404
                )
        except Exception as e:
            traceback.print_exc()
            self.send_json_response(
                APIResponse(success=False, error=str(e)),
                status=500
            )
    
    def _handle_root(self):
        """Handle root endpoint."""
        self.send_json_response(APIResponse(
            success=True,
            data={
                "name": "ThothOS API",
                "version": "2.0",
                "endpoints": [
                    {"path": "/health", "method": "GET", "description": "Health check"},
                    {"path": "/status", "method": "GET", "description": "System status"},
                    {"path": "/chat", "method": "POST", "description": "Chat with daemon"},
                    {"path": "/complete", "method": "POST", "description": "LLM completion"},
                    {"path": "/think", "method": "POST", "description": "Unimind reasoning"},
                    {"path": "/tools", "method": "GET", "description": "List tools"},
                    {"path": "/tools/execute", "method": "POST", "description": "Execute tool"},
                    {"path": "/plan", "method": "POST", "description": "Create execution plan"},
                    {"path": "/modules", "method": "GET", "description": "List modules"},
                    {"path": "/memory", "method": "GET", "description": "Query memory"},
                    {"path": "/memory/store", "method": "POST", "description": "Store memory"},
                    {"path": "/reflect", "method": "POST", "description": "Trigger reflection"}
                ]
            }
        ))
    
    def _handle_health(self):
        """Handle health check."""
        self.send_json_response(APIResponse(
            success=True,
            data={"status": "healthy", "uptime": self.api_server.get_uptime()}
        ))
    
    def _handle_status(self):
        """Handle status request."""
        kernel = self.api_server.kernel
        if kernel:
            status = kernel.get_status()
        else:
            status = {"state": "no_kernel", "modules": {}}
        
        self.send_json_response(APIResponse(success=True, data=status))
    
    def _handle_list_tools(self):
        """List available tools."""
        from interop.tool_framework import get_registry
        
        registry = get_registry()
        tools = registry.list_tools()
        
        self.send_json_response(APIResponse(
            success=True,
            data=[
                {
                    "name": t.name,
                    "description": t.description,
                    "category": t.category,
                    "parameters": [
                        {"name": p.name, "type": p.param_type.value, "required": p.required}
                        for p in t.parameters
                    ]
                }
                for t in tools
            ]
        ))
    
    def _handle_execute_tool(self, data: Dict):
        """Execute a tool."""
        from interop.tool_framework import execute_tool
        
        tool_name = data.get("tool")
        arguments = data.get("arguments", {})
        
        if not tool_name:
            self.send_json_response(
                APIResponse(success=False, error="Missing 'tool' field"),
                status=400
            )
            return
        
        result = execute_tool(tool_name, arguments)
        
        self.send_json_response(APIResponse(
            success=result.success,
            data=result.result,
            error=result.error
        ))
    
    def _handle_chat(self, data: Dict):
        """Handle chat request."""
        message = data.get("message", "")
        provider = data.get("provider")
        
        if not message:
            self.send_json_response(
                APIResponse(success=False, error="Missing 'message' field"),
                status=400
            )
            return
        
        # Try to use LLM if available
        try:
            from interop.llm_providers import chat
            response = chat(message, provider=provider)
        except Exception:
            # Fallback to NLU
            if self.api_server.kernel:
                nlu = self.api_server.kernel.get_module("nlu")
                if nlu and hasattr(nlu, 'interpret'):
                    response = nlu.interpret(message) or "No response"
                else:
                    response = f"Received: {message}"
            else:
                response = f"Echo: {message}"
        
        self.send_json_response(APIResponse(success=True, data={"response": response}))
    
    def _handle_complete(self, data: Dict):
        """Handle LLM completion request."""
        from interop.llm_providers import complete, CompletionRequest, Message
        
        messages = data.get("messages", [])
        model = data.get("model")
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 1024)
        provider = data.get("provider")
        
        request = CompletionRequest(
            messages=[Message(role=m["role"], content=m["content"]) for m in messages],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        response = complete(request, provider=provider)
        
        self.send_json_response(APIResponse(
            success=response.finish_reason != "error",
            data={
                "content": response.content,
                "model": response.model,
                "finish_reason": response.finish_reason,
                "usage": response.usage,
                "latency_ms": response.latency_ms
            },
            error=response.content if response.finish_reason == "error" else None
        ))
    
    def _handle_think(self, data: Dict):
        """Handle Unimind thinking request."""
        prompt = data.get("prompt", "")
        mode = data.get("mode")
        
        if not prompt:
            self.send_json_response(
                APIResponse(success=False, error="Missing 'prompt' field"),
                status=400
            )
            return
        
        kernel = self.api_server.kernel
        if kernel:
            unimind = kernel.get_module("unimind")
            if unimind and hasattr(unimind, 'think'):
                if mode:
                    from unimind.core import CognitiveMode
                    try:
                        unimind.set_mode(CognitiveMode[mode.upper()])
                    except KeyError:
                        pass
                
                result = unimind.think(prompt)
                self.send_json_response(APIResponse(success=True, data=result))
                return
        
        self.send_json_response(
            APIResponse(success=False, error="Unimind not available"),
            status=503
        )
    
    def _handle_plan(self, data: Dict):
        """Handle planning request."""
        goal = data.get("goal", "")
        context = data.get("context", {})
        
        if not goal:
            self.send_json_response(
                APIResponse(success=False, error="Missing 'goal' field"),
                status=400
            )
            return
        
        kernel = self.api_server.kernel
        if kernel:
            planner = kernel.get_module("lam_planner")
            if planner and hasattr(planner, 'create_plan'):
                plan = planner.create_plan(goal, context)
                self.send_json_response(APIResponse(
                    success=True,
                    data={
                        "plan_id": plan.plan_id,
                        "goal": plan.goal,
                        "actions": [a.to_dict() for a in plan.actions]
                    }
                ))
                return
        
        self.send_json_response(
            APIResponse(success=False, error="Planner not available"),
            status=503
        )
    
    def _handle_list_modules(self):
        """List registered modules."""
        kernel = self.api_server.kernel
        if kernel:
            modules = kernel.registry.list_modules()
            module_info = {}
            for name in modules:
                info = kernel.registry.get_info(name)
                if info:
                    module_info[name] = {
                        "state": info.state.value,
                        "error_count": info.error_count
                    }
            
            self.send_json_response(APIResponse(success=True, data=module_info))
        else:
            self.send_json_response(
                APIResponse(success=False, error="No kernel available"),
                status=503
            )
    
    def _handle_memory_query(self, query: Dict):
        """Query memory system."""
        search_query = query.get("q", [""])[0]
        limit = int(query.get("limit", ["10"])[0])
        
        kernel = self.api_server.kernel
        if kernel:
            memory = kernel.get_module("memory_logger")
            if memory:
                events = memory.get_latest_events(limit)
                self.send_json_response(APIResponse(success=True, data=events))
                return
        
        self.send_json_response(APIResponse(success=True, data=[]))
    
    def _handle_memory_store(self, data: Dict):
        """Store in memory."""
        content = data.get("content", "")
        memory_type = data.get("type", "observation")
        context = data.get("context")
        
        kernel = self.api_server.kernel
        if kernel:
            memory = kernel.get_module("memory_logger")
            if memory and hasattr(memory, 'log_event'):
                memory.log_event(memory_type, content, context)
                self.send_json_response(APIResponse(success=True, data={"stored": True}))
                return
        
        self.send_json_response(
            APIResponse(success=False, error="Memory system not available"),
            status=503
        )
    
    def _handle_reflect(self):
        """Trigger system reflection."""
        kernel = self.api_server.kernel
        if kernel:
            reflection = kernel.reflect()
            self.send_json_response(APIResponse(success=True, data=reflection))
        else:
            self.send_json_response(
                APIResponse(success=False, error="No kernel available"),
                status=503
            )


class APIServer:
    """
    ThothOS REST API Server.
    
    Provides HTTP interface for remote access to daemon functionality.
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        kernel=None,
        verbose: bool = True
    ):
        self.host = host
        self.port = port
        self.kernel = kernel
        self.verbose = verbose
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._start_time: Optional[datetime] = None
        self._running = False
    
    def start(self):
        """Start the API server."""
        if self._running:
            return
        
        # Set handler reference to server
        ThothAPIHandler.api_server = self
        
        try:
            self._server = HTTPServer((self.host, self.port), ThothAPIHandler)
            self._start_time = datetime.utcnow()
            self._running = True
            
            self._thread = threading.Thread(target=self._serve, daemon=True)
            self._thread.start()
            
            print(f"[APIServer] Started on http://{self.host}:{self.port}")
            
        except socket.error as e:
            print(f"[APIServer] Failed to start: {e}")
            raise
    
    def stop(self):
        """Stop the API server."""
        if self._server:
            self._running = False
            self._server.shutdown()
            self._server = None
            print("[APIServer] Stopped.")
    
    def _serve(self):
        """Server loop."""
        while self._running:
            self._server.handle_request()
    
    def get_uptime(self) -> float:
        """Get server uptime in seconds."""
        if self._start_time:
            return (datetime.utcnow() - self._start_time).total_seconds()
        return 0
    
    def set_kernel(self, kernel):
        """Set the kernel reference."""
        self.kernel = kernel


def create_server(
    host: str = "0.0.0.0",
    port: int = 8080,
    kernel=None
) -> APIServer:
    """Create and return an API server instance."""
    return APIServer(host=host, port=port, kernel=kernel)
