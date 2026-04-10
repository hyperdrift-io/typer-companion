from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeVar

T = TypeVar("T")

_MEMORY: dict[str, Any] = {}


def wizard(title: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Attach a human-readable title to a Typer command flow."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        setattr(func, "__wizard_title__", title)
        return func

    return decorator


@dataclass(slots=True)
class Step:
    title: str

    def run(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        print(f"==> {self.title}")
        result = func(*args, **kwargs)
        print(f"    ok: {self.title}")
        return result

    def prompt_env(
        self,
        env_path: str | Path,
        key: str,
        *,
        label: str | None = None,
        secret: bool = False,
        required: bool = False,
        default: str = "",
    ) -> str:
        print(f"==> {self.title}")
        path = Path(env_path)
        current = _env_get(path, key) or default
        value = _prompt(label or key, current, secret=secret)

        if required and not value:
            raise ValueError(f"{key} is required")

        if value and value != current:
            _env_set(path, key, value)
            print(f"    wrote: {key}")
        elif value:
            print(f"    kept: {key}")

        return value


@dataclass(slots=True)
class RetryableStep:
    title: str
    attempts: int = 3
    delay_seconds: float = 0.0

    def run(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        last_error: Exception | None = None

        for attempt in range(1, self.attempts + 1):
            try:
                print(f"==> {self.title} [{attempt}/{self.attempts}]")
                result = func(*args, **kwargs)
                print(f"    ok: {self.title}")
                return result
            except Exception as exc:  # pragma: no cover - intentionally broad at the boundary
                last_error = exc
                print(f"    retry: {exc}")
                if attempt < self.attempts and self.delay_seconds > 0:
                    time.sleep(self.delay_seconds)

        assert last_error is not None
        raise last_error


@dataclass(slots=True)
class MemorySlot:
    key: str
    fallback: str = ""

    def get(self) -> str:
        value = _MEMORY.get(self.key, self.fallback)
        return "" if value is None else str(value)

    def set(self, value: str) -> str:
        _MEMORY[self.key] = value
        return value

    def prompt(self, label: str, *, default: str | None = None, secret: bool = False) -> str:
        value = _prompt(label, self.get() or (default or ""), secret=secret)
        return self.set(value)


def step(title: str) -> Step:
    return Step(title)


def retryable(title: str, *, attempts: int = 3, delay_seconds: float = 0.0) -> RetryableStep:
    return RetryableStep(title=title, attempts=attempts, delay_seconds=delay_seconds)


def remember(key: str, *, default: str = "") -> MemorySlot:
    return MemorySlot(key=key, fallback=default)


def _prompt(label: str, default: str = "", *, secret: bool = False) -> str:
    try:
        import typer  # type: ignore
    except ImportError as exc:  # pragma: no cover - boundary behavior
        raise RuntimeError("Typer Companion requires Typer at runtime for prompting.") from exc

    if secret:
        return typer.prompt(label, default=default, hide_input=True)
    return typer.prompt(label, default=default)


def _env_get(path: Path, key: str) -> str:
    if not path.exists():
        return ""

    prefix = f"{key}="
    for raw in path.read_text().splitlines():
        if raw.startswith(prefix):
            return raw.split("=", 1)[1]

    return ""


def _env_set(path: Path, key: str, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"{key}={value}\n")
        return

    prefix = f"{key}="
    lines = path.read_text().splitlines()
    updated: list[str] = []
    replaced = False

    for line in lines:
        if line.startswith(prefix):
            updated.append(f"{key}={value}")
            replaced = True
        else:
            updated.append(line)

    if not replaced:
        updated.append(f"{key}={value}")

    path.write_text("\n".join(updated) + "\n")
