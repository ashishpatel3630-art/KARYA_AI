from pathlib import Path

from sandbox.executor import SandboxExecutor
from sandbox.limits import SandboxLimits
from sandbox.security import SandboxSecurity


def test_security_allows_safe_code():
    security = SandboxSecurity()

    result = security.validate(
        "x = 10 + 20\nprint(x)"
    )

    assert result.allowed is True


def test_security_blocks_os_import():
    security = SandboxSecurity()

    result = security.validate(
        "import os\nprint(os.listdir())"
    )

    assert result.allowed is False
    assert "Blocked import: os" in result.reason


def test_security_blocks_eval():
    security = SandboxSecurity()

    result = security.validate(
        'print(eval("2 + 2"))'
    )

    assert result.allowed is False
    assert "Blocked function call: eval" in result.reason


def test_security_blocks_open():
    security = SandboxSecurity()

    result = security.validate(
        'open("secret.txt")'
    )

    assert result.allowed is False
    assert "Blocked function call: open" in result.reason


def test_executor_runs_safe_python():
    executor = SandboxExecutor()

    result = executor.execute(
        "print(10 + 20)"
    )

    assert result.success is True
    assert result.output.strip() == "30"
    assert result.error is None
    assert result.timed_out is False


def test_executor_allows_math():
    executor = SandboxExecutor()

    result = executor.execute(
        "import math\nprint(math.sqrt(144))"
    )

    assert result.success is True
    assert result.output.strip() == "12.0"
    assert result.error is None


def test_executor_blocks_os():
    executor = SandboxExecutor()

    result = executor.execute(
        "import os\nprint(os.listdir())"
    )

    assert result.success is False
    assert result.error is not None
    assert "Blocked import: os" in result.error


def test_executor_blocks_eval():
    executor = SandboxExecutor()

    result = executor.execute(
        'print(eval("2 + 2"))'
    )

    assert result.success is False
    assert result.error is not None
    assert "Blocked function call: eval" in result.error


def test_executor_handles_runtime_error():
    executor = SandboxExecutor()

    result = executor.execute(
        "print(10 / 0)"
    )

    assert result.success is False
    assert result.error is not None
    assert "ZeroDivisionError" in result.error


def test_executor_timeout():
    limits = SandboxLimits(
        timeout_seconds=1.0,
        cpu_time_seconds=1,
    )

    executor = SandboxExecutor(limits=limits)

    result = executor.execute(
        "while True:\n"
        "    pass"
    )

    assert result.success is False
    assert result.timed_out is True
    assert result.error is not None
    assert "timeout" in result.error.lower()


def test_executor_output_limit():
    limits = SandboxLimits(
        max_output_chars=100,
    )

    executor = SandboxExecutor(limits=limits)

    result = executor.execute(
        "print('A' * 500)"
    )

    assert result.success is True
    assert len(result.output) <= 200
    assert "output truncated" in result.output.lower()


def test_executor_code_size_limit():
    limits = SandboxLimits(
        max_code_chars=20,
    )

    executor = SandboxExecutor(limits=limits)

    result = executor.execute(
        "print('this code is too long')"
    )

    assert result.success is False
    assert result.error is not None
    assert "Code exceeds sandbox limit" in result.error


def test_execute_file(tmp_path: Path):
    code_file = tmp_path / "test_script.py"

    code_file.write_text(
        "print(25 * 4)",
        encoding="utf-8",
    )

    executor = SandboxExecutor()

    result = executor.execute_file(
        str(code_file)
    )

    assert result.success is True
    assert result.output.strip() == "100"


def test_execute_file_missing():
    executor = SandboxExecutor()

    result = executor.execute_file(
        "/tmp/karya_nonexistent_script.py"
    )

    assert result.success is False
    assert result.error is not None
    assert "Code file not found" in result.error


def test_execute_file_requires_python_extension(tmp_path: Path):
    text_file = tmp_path / "script.txt"

    text_file.write_text(
        "print(123)",
        encoding="utf-8",
    )

    executor = SandboxExecutor()

    result = executor.execute_file(
        str(text_file)
    )

    assert result.success is False
    assert result.error is not None
    assert ".py extension" in result.error


def test_sandbox_result_helpers():
    executor = SandboxExecutor()

    result = executor.execute(
        "print('hello')"
    )

    assert result.is_empty() is False
    assert result.has_error() is False
    assert result.output_length() > 0
