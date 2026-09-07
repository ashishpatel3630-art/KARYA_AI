from dataclasses import dataclass


@dataclass(frozen=True)
class SandboxLimits:
    """
    Resource limits for KARYA sandbox execution.

    These limits are intentionally conservative for local
    agent-generated Python execution.
    """

    # Maximum wall-clock execution time.
    timeout_seconds: float = 5.0

    # Maximum CPU time available to the child process.
    cpu_time_seconds: int = 5

    # Maximum memory requested for the child process.
    memory_mb: int = 256

    # Maximum generated output.
    max_output_chars: int = 20_000

    # Maximum Python source code size.
    max_code_chars: int = 50_000

    # Maximum file size a sandbox process may create.
    max_file_size_mb: int = 10

    # Maximum number of open file descriptors.
    max_open_files: int = 32

    # Maximum number of processes.
    max_processes: int = 1

    def __post_init__(self) -> None:
        """Validate all configured limits."""

        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")

        if self.cpu_time_seconds <= 0:
            raise ValueError("cpu_time_seconds must be greater than zero.")

        if self.memory_mb <= 0:
            raise ValueError("memory_mb must be greater than zero.")

        if self.max_output_chars <= 0:
            raise ValueError("max_output_chars must be greater than zero.")

        if self.max_code_chars <= 0:
            raise ValueError("max_code_chars must be greater than zero.")

        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be greater than zero.")

        if self.max_open_files <= 0:
            raise ValueError("max_open_files must be greater than zero.")

        if self.max_processes <= 0:
            raise ValueError("max_processes must be greater than zero.")

    @property
    def memory_bytes(self) -> int:
        """Return memory limit in bytes."""
        return self.memory_mb * 1024 * 1024

    @property
    def max_file_size_bytes(self) -> int:
        """Return maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    def validate_code_size(self, code: str) -> None:
        """
        Validate the size of Python source code.
        """

        if not isinstance(code, str):
            raise TypeError("code must be a string.")

        if not code.strip():
            raise ValueError("code cannot be empty.")

        if len(code) > self.max_code_chars:
            raise ValueError(
                f"Code exceeds sandbox limit of "
                f"{self.max_code_chars} characters."
            )

    def truncate_output(self, output: str) -> str:
        """
        Limit captured output to the configured maximum size.
        """

        if not isinstance(output, str):
            output = str(output)

        if len(output) <= self.max_output_chars:
            return output

        truncated = output[: self.max_output_chars]

        return (
            truncated
            + "\n\n"
            + "[Sandbox output truncated: "
            + f"maximum {self.max_output_chars} characters]"
        )