import aiohttp
import asyncio
from typing import Optional
from dataclasses import dataclass
import sys

@dataclass
class ExecutionResult:
    """Represents the result of code execution"""
    success: bool
    output: str
    error: Optional[str] = None

class KernelClient:
    """Client for interacting with Jupyter Kernel Gateway"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.server_url = self.base_url.replace("http://", "").replace("https://", "")
        self.session = None
        self.kernel_id = None
        self.ws = None
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()
    
    async def start(self):
        """Initialize the client and start a kernel"""
        self.session = aiohttp.ClientSession()
        
        # Start a new kernel
        async with self.session.post(f"{self.base_url}/api/kernels") as response:
            kernel_info = await response.json()
            self.kernel_id = kernel_info['id']
        
        # Connect to kernel WebSocket
        ws_url = f"ws://{self.server_url}/api/kernels/{self.kernel_id}/channels"
        self.ws = await self.session.ws_connect(ws_url)
    
    async def shutdown(self):
        """Clean up resources"""
        if self.ws:
            await self.ws.close()
        
        if self.kernel_id:
            await self.session.delete(f"{self.base_url}/api/kernels/{self.kernel_id}")
        
        if self.session:
            await self.session.close()
    
    async def execute_code(self, code: str, timeout: float = 30.0) -> ExecutionResult:
        """Execute code and return the result"""
        if not self.ws:
            raise RuntimeError("Client not started")
        
        # Send execute request
        msg_id = self._generate_msg_id()
        execute_request = {
            'header': {
                'msg_id': msg_id,
                'msg_type': 'execute_request'
            },
            'content': {
                'code': code,
                'silent': False,
                'store_history': True,
                'user_expressions': {},
                'allow_stdin': False
            },
            'parent_header': {},
            'metadata': {}
        }
        
        await self.ws.send_json(execute_request)
        
        # Collect output
        output = []
        error = None
        
        try:
            while True:
                msg = await asyncio.wait_for(self.ws.receive_json(), timeout)
                
                if msg['header']['msg_type'] == 'stream':
                    output.append(msg['content']['text'])
                elif msg['header']['msg_type'] == 'error':
                    error = '\n'.join(msg['content']['traceback'])
                    break
                elif msg['header']['msg_type'] == 'execute_reply':
                    if msg['content']['status'] == 'ok':
                        break
                    else:
                        error = f"Execution failed: {msg['content']}"
                        break
        
        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                output=''.join(output),
                error="Execution timed out"
            )
        
        return ExecutionResult(
            success=error is None,
            output=''.join(output),
            error=error
        )
    
    async def install_packages(self, packages: list) -> ExecutionResult:
        """Install third-party packages using pip."""
        if not self.ws:
            raise RuntimeError("Client not started")
        
        # 构建 pip install 命令
        packages_str = ' '.join(packages)
        code = f"!python -m pip install {packages_str}"
        
        # 执行安装命令
        return await self.execute_code(code)
    
    def _generate_msg_id(self) -> str:
        """Generate a unique message ID"""
        import uuid
        return str(uuid.uuid4())
