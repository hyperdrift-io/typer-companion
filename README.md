# Typer Companion

> Wizard-first orchestration for Typer: step validation, remembered context, and graceful recovery for ambitious scripts.

**Typer Companion** is the small, **generic** runtime for when a clean Typer CLI stops being “just a command” and becomes a real operational flow—without pulling in anyone’s mono-repo or infra opinions.

- **Public OSS:** [`hyperdrift-io/typer-companion`](https://github.com/hyperdrift-io/typer-companion) · `pip install typer-companion`
- **Design article:** [The missing wizard layer](https://hyperdrift.io/blog/typer-companion-missing-wizard-layer) (Hyperdrift field note; same thesis, **Companion** as the installable package)

Hyperdrift also maintains an **internal** scripting module (`typerx`) with Rich-backed logging and org-specific paths—that layer is **private** and not the right default for the wider Python community. **Use Typer Companion** when you want the wizard pattern in your own repo.

## Why it exists

Typer nails commands and help text. It does not try to own **multi-step flows**: validated stages, remembered answers, retries after flakey APIs, and env-backed prompts. Companion fills that gap—**thin**, no workflow DSL, no hidden platform assumptions.

## Install

```bash
pip install typer-companion
# Typer is a peer dependency in many setups:
pip install typer typer-companion
```

## Quick example

```python
import typer
from pathlib import Path
from typer_companion import remember, retryable, step, wizard

app = typer.Typer(add_completion=False)


def validate_project(project_id: str) -> str:
    if not project_id.startswith("acme-"):
        raise ValueError("project_id must start with acme-")
    return project_id


def call_upstream(project_id: str) -> None:
    pass  # your API call


@app.command()
@wizard("Setup")
def setup() -> None:
    project_id = remember("project_id").prompt("Project ID")

    step("Validate").run(validate_project, project_id)
    retryable("Sync", attempts=3).run(call_upstream, project_id)
    step("Credentials").prompt_env(Path(".env"), "API_KEY")
```

## Core ideas

- **`wizard()`** — operator-facing name for the flow.
- **`step()`** — named checkpoint with `.run()` or `.prompt_env()`.
- **`remember()`** — in-memory context for the current run.
- **`retryable()`** — explicit bounded retries instead of scattered loops.

## License

MIT
