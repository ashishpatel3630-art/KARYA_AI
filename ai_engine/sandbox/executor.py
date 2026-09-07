from __future__ import annotations

import io
import os
import signal
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path

from .limits import SandboxLimits
from .security import SandboxSecurity


@dataclass
class SandboxResult:
    """Result returned by sandbox execution."""

    success: bool
    output: str = ""
    error: str | None = None
    timed_out: bool = False
    exit_code: int | None = None


_RUNNER_CODE = r'''
from __future__ import annotations

import io
import sys
from contextlib import redirect_stderr, redirect_stdout


def apply_resource_limits(
    cpu_time_seconds: int,
    memory_bytes: int,
    max_open_files: int,
    max_processes: int,
    max_file_size_bytes: int,
) -> None:
    """Apply operating-system resource limits."""

    try:
        import resource
    except ImportError:
        return

    # CPU time
    try:
        resource.setrlimit(
            resource.RLIMIT_CPU,
            (
                cpu_time_seconds,
                cpu_time_seconds + 1,
            ),
        )
    except (
        AttributeError,
        OSError,
        ValueError,
    ):
        pass

    # Virtual memory
    try:
        resource.setrlimit(
            resource.RLIMIT_AS,
            (
                memory_bytes,
                memory_bytes,
            ),
        )
    except (
        AttributeError,
        OSError,
        ValueError,
    ):
        pass

    # Open file descriptors
    try:
        resource.setrlimit(
            resource.RLIMIT_NOFILE,
            (
                max_open_files,
                max_open_files,
            ),
        )
    except (
        AttributeError,
        OSError,
        ValueError,
    ):
        pass

    # Maximum file size
    try:
        resource.setrlimit(
            resource.RLIMIT_FSIZE,
            (
                max_file_size_bytes,
                max_file_size_bytes,
            ),
        )
    except (
        AttributeError,
        OSError,
        ValueError,
    ):
        pass

    # Maximum processes
    try:
        resource.setrlimit(
            resource.RLIMIT_NPROC,
            (
                max_processes,
                max_processes,
            ),
        )
    except (
        AttributeError,
        OSError,
        ValueError,
    ):
        pass


def main() -> int:
    """
    Execute the sandbox payload.
    """

    if len(sys.argv) != 7:
        print(
            "Invalid sandbox runner arguments.",
            file=sys.stderr,
        )
        return 2

    payload_path = sys.argv[1]

    cpu_time_seconds = int(sys.argv[2])
    memory_bytes = int(sys.argv[3])
    max_open_files = int(sys.argv[4])
    max_processes = int(sys.argv[5])
    max_file_size_bytes = int(sys.argv[6])

    # Apply OS-level limits before executing user code.
    apply_resource_limits(
        cpu_time_seconds=cpu_time_seconds,
        memory_bytes=memory_bytes,
        max_open_files=max_open_files,
        max_processes=max_processes,
        max_file_size_bytes=max_file_size_bytes,
    )

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    execution_globals = {
        "__name__": "__sandbox__",
        "__package__": None,
        "__file__": payload_path,
        "__builtins__": __builtins__,
    }

    try:
        with open(
            payload_path,
            "r",
            encoding="utf-8",
        ) as file:
            code = file.read()

        compiled_code = compile(
            code,
            "<karya-sandbox>",
            "exec",
        )

        with redirect_stdout(
            stdout_buffer
        ), redirect_stderr(
            stderr_buffer
        ):
            exec(
                compiled_code,
                execution_globals,
                execution_globals,
            )

        stdout = stdout_buffer.getvalue()
        stderr = stderr_buffer.getvalue()

        if stderr:
            stdout = (
                f"{stdout}\n{stderr}"
                if stdout
                else stderr
            )

        print(
            stdout,
            end="",
        )

        return 0

    except BaseException as exc:
        print(
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
'''


class SandboxExecutor:
    """
    Secure execution layer for KARYA Python tools.

    Execution happens inside a separate Python subprocess.

    Security flow:

        Python code
             ↓
        AST validation
             ↓
        temporary isolated directory
             ↓
        isolated Python subprocess
             ↓
        OS resource limits
             ↓
        execution
             ↓
        SandboxResult
    """

    def __init__(
        self,
        security: SandboxSecurity | None = None,
        limits: SandboxLimits | None = None,
    ) -> None:
        self.security = security or SandboxSecurity()
        self.limits = limits or SandboxLimits()

    def validate(self, code: str):
        """
        Validate Python code without executing it.
        """

        self.limits.validate_code_size(code)

        return self.security.validate(code)

    def execute(
        self,
        code: str,
    ) -> SandboxResult:
        """
        Validate and execute Python code inside
        an isolated subprocess.
        """

        if not isinstance(code, str):
            return SandboxResult(
                success=False,
                error="code must be a string.",
            )

        code = code.strip()

        if not code:
            return SandboxResult(
                success=False,
                error="code cannot be empty.",
            )

        try:
            self.limits.validate_code_size(code)

        except (
            TypeError,
            ValueError,
        ) as exc:
            return SandboxResult(
                success=False,
                error=str(exc),
            )

        # -------------------------------------------------
        # Security validation
        # -------------------------------------------------

        try:
            security_result = self.security.validate(
                code
            )

        except Exception as exc:
            return SandboxResult(
                success=False,
                error=(
                    "Security validation failed: "
                    f"{exc}"
                ),
            )

        if not security_result.allowed:
            return SandboxResult(
                success=False,
                error=security_result.reason,
            )

        process: subprocess.Popen[str] | None = None

        try:
            with tempfile.TemporaryDirectory(
                prefix="karya_sandbox_"
            ) as temp_dir:

                temp_path = Path(temp_dir)

                payload_path = (
                    temp_path / "payload.py"
                )

                runner_path = (
                    temp_path / "runner.py"
                )

                payload_path.write_text(
                    code,
                    encoding="utf-8",
                )

                runner_path.write_text(
                    _RUNNER_CODE,
                    encoding="utf-8",
                )

                # -------------------------------------------------
                # Launch isolated Python interpreter
                # -------------------------------------------------

                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-I",
                        "-u",
                        str(runner_path),
                        str(payload_path),
                        str(
                            self.limits.cpu_time_seconds
                        ),
                        str(
                            self.limits.memory_bytes
                        ),
                        str(
                            self.limits.max_open_files
                        ),
                        str(
                            self.limits.max_processes
                        ),
                        str(
                            self.limits.max_file_size_bytes
                        ),
                    ],
                    cwd=temp_dir,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env={
                        "PYTHONNOUSERSITE": "1",
                        "PYTHONDONTWRITEBYTECODE": "1",
                        "PYTHONIOENCODING": "utf-8",
                    },
                    start_new_session=True,
                )

                # Give the subprocess a small grace period
                # beyond the configured wall-clock limit.
                wall_timeout = (
                    float(
                        self.limits.timeout_seconds
                    )
                    + 1.0
                )

                try:
                    stdout, stderr = (
                        process.communicate(
                            timeout=wall_timeout
                        )
                    )

                except subprocess.TimeoutExpired:
                    self._terminate_process(
                        process
                    )

                    stdout, stderr = (
                        process.communicate()
                    )

                    return SandboxResult(
                        success=False,
                        output=self.limits.truncate_output(
                            stdout
                        ),
                        error=(
                            "Sandbox execution exceeded "
                            f"the "
                            f"{self.limits.timeout_seconds} "
                            "second timeout."
                        ),
                        timed_out=True,
                        exit_code=process.returncode,
                    )

                output = (
                    self.limits.truncate_output(
                        stdout
                    )
                )

                error_output = (
                    self.limits.truncate_output(
                        stderr
                    )
                )

                exit_code = process.returncode

                # -------------------------------------------------
                # Successful execution
                # -------------------------------------------------

                if exit_code == 0:
                    return SandboxResult(
                        success=True,
                        output=output,
                        error=None,
                        timed_out=False,
                        exit_code=0,
                    )

                # -------------------------------------------------
                # CPU timeout
                # -------------------------------------------------

                if self._is_cpu_timeout(
                    exit_code
                ):
                    return SandboxResult(
                        success=False,
                        output=output,
                        error=(
                            "Sandbox CPU time limit "
                            f"of "
                            f"{self.limits.cpu_time_seconds} "
                            "seconds was exceeded."
                        ),
                        timed_out=True,
                        exit_code=exit_code,
                    )

                # -------------------------------------------------
                # Other subprocess failure
                # -------------------------------------------------

                error = (
                    error_output.strip()
                    or "Sandbox process failed."
                )

                return SandboxResult(
                    success=False,
                    output=output,
                    error=error,
                    timed_out=False,
                    exit_code=exit_code,
                )

        except Exception as exc:
            if (
                process is not None
                and process.poll() is None
            ):
                self._terminate_process(
                    process
                )

            return SandboxResult(
                success=False,
                output="",
                error=(
                    "Sandbox execution failed: "
                    f"{exc}"
                ),
                timed_out=False,
                exit_code=(
                    process.returncode
                    if process is not None
                    else None
                ),
            )

    @staticmethod
    def _terminate_process(
        process: subprocess.Popen[str],
    ) -> None:
        """
        Kill the complete sandbox process group.
        """

        if process.poll() is not None:
            return

        try:
            if os.name == "posix":
                os.killpg(
                    process.pid,
                    signal.SIGKILL,
                )
            else:
                process.kill()

        except (
            ProcessLookupError,
            PermissionError,
            OSError,
        ):
            try:
                process.kill()
            except (
                ProcessLookupError,
                OSError,
            ):
                pass

    @staticmethod
    def _is_cpu_timeout(
        exit_code: int | None,
    ) -> bool:
        """
        Detect CPU-limit termination.
        """

        if exit_code is None:
            return False

        if exit_code < 0:
            try:
                return (
                    -exit_code
                    in {
                        signal.SIGXCPU,
                        signal.SIGKILL,
                    }
                )

            except AttributeError:
                return (
                    -exit_code
                    == signal.SIGKILL
                )

        return False


__all__ = [
    "SandboxExecutor",
    "SandboxResult",
]