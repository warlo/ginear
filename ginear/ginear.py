# /usr/bin/env python3
import os
import readline
from typing import Annotated, Any

import typer
from dotenv import load_dotenv

from ginear.queries import (
    create_issue,
    get_issues,
    get_project_ids_for_team,
    get_state_ids_for_team,
    get_team_ids,
    get_user_id,
)
from ginear.utils import (
    DOTFILE_PATH,
    append_or_remove_env_list,
    git_commit,
    switch_branch,
    write_to_env,
)

load_dotenv(dotenv_path=DOTFILE_PATH)
app = typer.Typer()

LINEAR_API_TOKEN = os.environ.get("LINEAR_API_TOKEN")

TEAM_ID = os.environ.get("TEAM_ID")

PROJECT_ID = os.environ.get("PROJECT_ID")

USER_ID = os.environ.get("USER_ID")

INITIAL_STATE_ID = os.environ.get("INITIAL_STATE_ID")


def get_fzf_string(issue: dict[str, Any], max_issue_title_length: int = 100) -> str:
    creator = issue["creator"] or {}
    return f"[{creator.get('name', '')[:10]}] – {issue['title'][:max_issue_title_length].ljust(max_issue_title_length)}[{issue['state']['name']}]"


def get_fzf_strings(issues: list[dict[str, Any]]) -> list[str]:
    max_issue_title_length = max([len(issue["title"]) for issue in issues])
    return [
        get_fzf_string(issue, max_issue_title_length=max_issue_title_length)
        for issue in issues
    ]


def attach_issue_prompt(
    *, search_query: str | None = None, project: bool = False
) -> None:
    from pyfzf.pyfzf import FzfPrompt

    issues = get_issues(search_query)
    fzf = FzfPrompt()
    selected_list = fzf.prompt(
        [
            "> Create new issue",
            "> Search for specific issue title",
            *get_fzf_strings(issues),
        ],
        fzf_options="--header 'Issue missing? Select \"> Search for specific issue\"'",
    )
    if selected_list:
        selected = selected_list[0]
        if selected == "> Search for specific issue title":
            search_query = typer.prompt("Search term")
            return attach_issue_prompt(search_query=search_query, project=project)

        if selected == "> Create new issue":
            return create(project=project)

        issue = next(
            issue for issue in issues if issue["title"] == selected.split(" – ")[1]
        )
        branch_name = issue["branchName"]
        switch_branch(branch_name)

        print("Selected:", selected)


def set_team() -> str:
    from pyfzf.pyfzf import FzfPrompt

    team_ids = get_team_ids()
    fzf = FzfPrompt()
    selected_list = fzf.prompt(
        [
            *[f"[{team_id['name']}] – {team_id['id']}" for team_id in team_ids],
        ],
        fzf_options="--header 'Set the team you wants issues to be created in'",
    )
    if not selected_list:
        print("Missing team ids")
        raise typer.Exit()

    team_id = selected_list[0].split(" – ")[1]
    if not team_id:
        print("No team id")
        raise typer.Exit()
    assert isinstance(team_id, str)
    write_to_env("TEAM_ID", team_id)
    return team_id


def get_project(team_id: str) -> None:
    from pyfzf.pyfzf import FzfPrompt

    project_ids = get_project_ids_for_team(team_id)
    fzf = FzfPrompt()
    selected_list = fzf.prompt(
        [f"[{project_id['name']}] – {project_id['id']}" for project_id in project_ids],
        fzf_options="--header 'Set the project you want your issues to be created in'",
    )
    if not selected_list:
        print("Missing projects")
        raise typer.Exit()

    project_id = selected_list[0].split(" – ")[1]
    if not project_id:
        print("No project id")
        raise typer.Exit()
    return project_id


def set_state(team_id: str) -> None:
    from pyfzf.pyfzf import FzfPrompt

    state_ids = get_state_ids_for_team(team_id)
    fzf = FzfPrompt()
    selected_list = fzf.prompt(
        [
            f"[{initial_issue_state['name']}] – {initial_issue_state['id']}"
            for initial_issue_state in state_ids
        ],
        fzf_options="--header 'Set the initial state you want your issues to be created with'",
    )
    if not selected_list:
        print("Missing states")
        raise typer.Exit()
    initial_issue_state = selected_list[0].split(" – ")[1]
    if not initial_issue_state:
        print("No initial issue state")
        raise typer.Exit()
    write_to_env("INITIAL_STATE_ID", initial_issue_state)


def append_or_remove_to_exclude_state(team_id: str) -> None:
    from pyfzf.pyfzf import FzfPrompt

    state_ids = get_state_ids_for_team(team_id)
    fzf = FzfPrompt()
    selected_list = fzf.prompt(
        [
            f"[{initial_issue_state['name']}] – {initial_issue_state['id']}"
            for initial_issue_state in state_ids
        ],
        fzf_options="--header 'Select the state you want to exclude when retrieving issues'",
    )
    if not selected_list:
        print("Missing states")
        raise typer.Exit()
    excluded_state = selected_list[0].split(" – ")[1]
    if not excluded_state:
        print("No state selected")
        raise typer.Exit()
    append_or_remove_env_list("EXCLUDED_STATES", excluded_state)


def run_onboarding(force: bool = False) -> None:
    if not LINEAR_API_TOKEN or force:
        import webbrowser

        webbrowser.open("https://linear.app/settings/api")
        linear_api_token = typer.prompt(
            "Insert Personal API Key (https://linear.app/settings/api)"
        )
        if not linear_api_token:
            print("Invalid API token")
            raise typer.Exit()

        write_to_env("LINEAR_API_TOKEN", linear_api_token)
        load_dotenv(dotenv_path=DOTFILE_PATH)

    user_id = USER_ID
    if not user_id or force:
        user = get_user_id()
        user_id = user["id"]
        if not user_id:
            print("No user id")
            raise typer.Exit()
        write_to_env("USER_ID", user_id)

    team_id = TEAM_ID
    if not team_id or force:
        team_id = set_team()

    project_id = PROJECT_ID
    if not project_id or force:
        project_id = get_project(team_id=team_id)
        write_to_env("PROJECT_ID", project_id)

    initial_issue_state = INITIAL_STATE_ID
    if not initial_issue_state or force:
        set_state(team_id=team_id)

    print("🍸 Onboarding success 🍸")


@app.command()
def project() -> None:
    """Set project_id"""
    if not TEAM_ID:
        print("Missing team_id")
        raise typer.Exit()

    project_id = get_project(TEAM_ID)
    write_to_env("PROJECT_ID", project_id)


@app.command()
def team() -> None:
    """Set team_id"""
    set_team()


@app.command()
def state() -> None:
    """Set initial_state of created issues"""

    if not TEAM_ID:
        print("Missing team_id")
        raise typer.Exit()

    set_state(TEAM_ID)


@app.command()
def exclude_state() -> None:
    """Add state to list of excluded states"""

    if not TEAM_ID:
        print("Missing team_id")
        raise typer.Exit()

    append_or_remove_to_exclude_state(TEAM_ID)


@app.command()
def create(
    project: Annotated[
        bool,
        typer.Option("-p"),
    ] = False
) -> None:
    """
    Create Linear ticket
    """

    selected_project_id = PROJECT_ID

    if project:
        selected_project_id = get_project(team_id=TEAM_ID)

    title = typer.prompt("Title")
    description = typer.prompt("Description", default="", show_default=False)
    create_issue(title=title, description=description, project_id=selected_project_id)


@app.command()
def init() -> None:
    """
    (Re)-run the onboarding to set the API key, team_id, project etc.
    """

    run_onboarding(force=True)


@app.command()
def description(disable: bool) -> None:
    """
    Toggle `Created with Ginear` in the issue description
    """

    write_to_env("ADD_DESCRIPTION_TEXT", str(disable))


@app.command()
def commit(
    message: Annotated[
        str, typer.Option("--message", "-m", prompt="Msg", help="git commit message")
    ],
    project: Annotated[
        bool,
        typer.Option("-p"),
    ] = False,
) -> None:
    """
    Create a Linear ticket, switch to its branch and commit to git
    """

    selected_project_id = PROJECT_ID

    if project:
        selected_project_id = get_project(team_id=TEAM_ID)

    create_issue(title=message, description="", project_id=selected_project_id)
    git_commit(message)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    project: Annotated[
        bool,
        typer.Option("-p"),
    ] = False,
) -> None:
    """
    Running `gin` will prompt to attach or create new ticket

    Runs onboarding if environment variables are not set
    """
    if ctx.invoked_subcommand:
        return

    if LINEAR_API_TOKEN and TEAM_ID and PROJECT_ID and USER_ID and INITIAL_STATE_ID:
        attach_issue_prompt(search_query=None, project=project)

    else:
        run_onboarding()


def run() -> None:
    app()


if __name__ == "__main__":
    app()
