import os
import asyncio
from flask import Flask, request, jsonify
from kernel_client import KernelClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
KERNEL_URL = os.getenv("KERNEL_URL", "http://localhost:8888")

app = Flask(__name__)

print(f"KERNEL_URL: {KERNEL_URL}")

# 异步执行代码
async def run_code(code: str, required_packages=None):
    async with KernelClient(KERNEL_URL) as client:
        # 如果传入了 required_packages，则尝试安装
        if required_packages:
            install_result = await asyncio.wait_for(
                client.install_packages(required_packages), timeout=15
            )
            if not install_result.success:
                return {"success": False, "error": install_result.error}

        # 执行代码
        result = await asyncio.wait_for(client.execute_code(code), timeout=30)
        if result.success:
            print(f"Output: {result.output}")
            return result
        else:
            print(result.output)
            return result

# /execute API
@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"success": False, "error": "Missing 'code' in request"}), 400

    code = data['code']
    required_packages = data.get('required_packages', None)
    # ✅ 格式化代码
    print(f"Formatted code (repr): {code}")

    try:
        result = asyncio.run(run_code(code, required_packages))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
