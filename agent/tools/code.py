# execute_code_local.py
import subprocess, tempfile, os, textwrap, sys, ast
from agent.tool_registry import common_tool_registry

@common_tool_registry(
    name_or_callable="execute_code",
    description="""
    Executes the given code in the local Python environment.  
    Useful for quick tests or 'fast code snippet validation'.
    (※ Not for production use, security isolation is limited.)

    Args:
        code (str): Python code string to execute. If you never use output functions like `print`, nothing will be output or returned.
                    e.g., "for i in range(3): print(i)"
        timeout (int): Maximum execution time (seconds). If not specified by the user, the default is 5 seconds.

    Returns:
        str: Execution result string combining stdout and stderr.  
             If there is no output, returns "✅ Execution complete (no output)".  
             If forbidden modules are detected or a timeout occurs, a message explaining the reason is returned.
    """
)
def execute_code(code: str, timeout: int = 5) -> str:
    FORBIDDEN = {
        "import os", "import sys", "subprocess", "socket",
        "__import__", "open(", "eval(", "exec("
    }
    lowered = code.replace(" ", "").lower()
    if any(bad in lowered for bad in FORBIDDEN):
        return "❌ Execution denied due to forbidden modules/functions."

    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(n.name in {"os", "sys", "subprocess", "socket"} for n in node.names):
                    return "❌ Forbidden module import detected → Execution denied"
    except Exception:
        return "❌ Code parsing failed"

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(textwrap.dedent(code))
        script_path = f.name

    cmd = [sys.executable, script_path]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = (proc.stdout + proc.stderr)[:4000]
        return output or "✅ Execution complete (no output)"
    except subprocess.TimeoutExpired:
        return f"⏰ Execution time limit exceeded ({timeout} seconds)."
    finally:
        os.remove(script_path)
