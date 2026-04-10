# Typer Companion

> Wizard-first orchestration for Typer. Give ambitious scripts step validation, context retention, and graceful recovery.

![Typer Companion hero](https://hyperdrift.io/content/images/blog/hd-scripting-orchestrated-dev-hero-v3a.webp)

`Typer Companion` is a small runtime for the moment when a clean Typer CLI stops being "just a command" and starts becoming a real operational flow.

It is built for scripts that need to:

- move through validated steps instead of one-shot execution
- remember context across a whole run
- reuse existing values instead of asking the operator twice
- handle retries without turning the script into branch soup
- stay readable for humans and legible for agents

This is the missing middle between Bash sprawl and internal platform overkill.

## Why it exists

Typer already gives Python CLIs a beautiful command surface.

What it does not try to own is the wizard runtime underneath more ambitious scripts:

- setup flows
- release flows
- cloud credential collection
- deployment checklists
- semi-manual operations that cross local and external systems

That is the problem space `Typer Companion` is designed for.

## Quick example

```python
import typer

from typer_companion import remember, retryable, step, wizard

app = typer.Typer(add_completion=False)


def validate_project(project_id: str) -> str:
    if not project_id.startswith("hyperdrift-"):
        raise ValueError("Project IDs must start with 'hyperdrift-'")
    return project_id


def enable_google_apis(project_id: str) -> None:
    print(f"Enabling APIs for {project_id}")


def check_launch_readiness() -> None:
    print("Launch readiness is clean")


@app.command()
@wizard("OAuth setup")
def setup() -> None:
    project_id = remember("gcp_project_id").prompt("GCP project ID")

    step("Validate project").run(validate_project, project_id)
    retryable("Enable Google APIs", attempts=3).run(enable_google_apis, project_id)
    step("Collect credentials").prompt_env(".env.local", "GOOGLE_CLIENT_ID")
    step("Launch readiness").run(check_launch_readiness)


if __name__ == "__main__":
    app()
```

## Core ideas

- `wizard()` gives the flow a clear operator-facing identity.
- `step()` turns progress into named checkpoints instead of ad hoc prints.
- `remember()` lets the runtime retain values across the current flow.
- `retryable()` makes recovery explicit instead of scattering loops across the script.
- `prompt_env()` treats existing config as reusable context, not just raw input.

## Positioning

`Typer Companion` is not trying to become a platform.

It is intentionally small:

- no hidden infrastructure assumptions
- no opinionated deployment model
- no giant workflow DSL

The goal is simple: make serious Typer scripts feel trustworthy when they start carrying operational weight.

## Status

Early and intentionally small. The first cut is focused on the primitives Hyperdrift needed in practice:

- step semantics
- remembered context
- retry handling
- env-backed prompting

## Install

```bash
pip install typer-companion
```

If your environment does not already include Typer, install it alongside the package:

```bash
pip install typer typer-companion
```

## Read the proposal

- Blog article: [Typer Companion: The Missing Wizard Layer for Ambitious Scripts](https://hyperdrift.io/blog/typer-companion-missing-wizard-layer)
- GitHub: [hyperdrift-io/typer-companion](https://github.com/hyperdrift-io/typer-companion)

## License

MIT
