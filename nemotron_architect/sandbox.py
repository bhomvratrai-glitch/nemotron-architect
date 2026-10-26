import os
import sys
import subprocess
import py_compile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    error_summary: Optional[str] = None

class CodeSandbox:
    """
    Hermetic local execution sandbox to test generated code and execute automated test suites.
    """
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(tempfile.mkdtemp(prefix="nemotron_run_"))
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_file(self, relative_path: str, content: str) -> Path:
        """
        Writes a source file into the sandbox hierarchy.
        """
        target = self.base_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def check_syntax(self, relative_path: str) -> ExecutionResult:
        """
        Validates Python AST/syntax using py_compile.
        """
        target = self.base_dir / relative_path
        try:
            py_compile.compile(str(target), doraise=True)
            return ExecutionResult(success=True, exit_code=0, stdout="Syntax OK", stderr="")
        except py_compile.PyCompileError as e:
            return ExecutionResult(
                success=False,
                exit_code=1,
                stdout="",
                stderr=str(e),
                error_summary="Syntax / Compilation Error"
            )

    def run_tests(self, test_file: Optional[str] = None, timeout: int = 15) -> ExecutionResult:
        """
        Executes pytest in the sandbox environment and captures all output.
        """
        cmd = [sys.executable, "-m", "pytest", "-v"]
        if test_file:
            cmd.append(test_file)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.base_dir) + (os.pathsep + env.get("PYTHONPATH", ""))

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            is_success = (proc.returncode == 0)
            return ExecutionResult(
                success=is_success,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                error_summary=None if is_success else "Test Suite Failure"
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Execution timed out after {timeout} seconds",
                error_summary="Timeout Error"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=1,
                stdout="",
                stderr=str(e),
                error_summary="Process Execution Exception"
            )

    def cleanup(self):
        """
        Cleans up temporary directory if necessary.
        """
        if self.base_dir.exists() and "nemotron_run_" in self.base_dir.name:
            shutil.rmtree(self.base_dir, ignore_errors=True)
