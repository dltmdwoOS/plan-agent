# execute_code_local.py
import subprocess, tempfile, os, textwrap, sys, ast
from agent.tool_registry import common_tool_registry
from agent.utils import load_locale_const

const = load_locale_const()

@common_tool_registry(
    name_or_callable="execute_code",
    description=const.EXECUTE_CODE_CONST['desc']
)
def execute_code(code: str, timeout: int = 5) -> str:
    FORBIDDEN = {
        "import os", "import sys", "subprocess", "socket",
        "__import__", "open(", "eval(", "exec("
    }
    lowered = code.replace(" ", "").lower()
    if any(bad in lowered for bad in FORBIDDEN):
        return const.EXECUTE_CODE_CONST['tabu_import']

    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(n.name in {"os", "sys", "subprocess", "socket"} for n in node.names):
                    return const.EXECUTE_CODE_CONST['forbidden_module']
    except Exception:
        return const.EXECUTE_CODE_CONST['parsing_failed']

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
        return output or const.EXECUTE_CODE_CONST['no_output']
    except subprocess.TimeoutExpired:
        return const.EXECUTE_CODE_CONST['timeout'].format(timeout=timeout)
    finally:
        os.remove(script_path)
