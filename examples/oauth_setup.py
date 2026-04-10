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
