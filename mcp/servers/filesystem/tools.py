from pathlib import Path

from mcp.gateway.registry import registry
from mcp.config.settings import settings


def _safe_path(path: str) -> Path:
    requested = Path(path).resolve()

    for root in settings.allowed_roots:
        allowed_root = Path(root).resolve()

        try:
            requested.relative_to(allowed_root)
            return requested
        except ValueError:
            continue

    raise PermissionError(
        "Filesystem access outside approved KARYA directories is blocked."
    )


def read_file(path: str) -> dict:

    safe_path = _safe_path(path)

    if not safe_path.exists():
        raise FileNotFoundError(path)

    if not safe_path.is_file():
        raise ValueError("Path is not a file.")

    content = safe_path.read_text(
        encoding="utf-8"
    )

    return {
        "path": str(safe_path),
        "content": content,
    }


def write_file(path: str, content: str) -> dict:

    safe_path = _safe_path(path)

    safe_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_path.write_text(
        content,
        encoding="utf-8",
    )

    return {
        "path": str(safe_path),
        "written": True,
    }


registry.register(
    name="read_file",
    server="filesystem",
    description="Read an approved local file",
    handler=read_file,
)

registry.register(
    name="write_file",
    server="filesystem",
    description="Write to approved local storage",
    handler=write_file,
)