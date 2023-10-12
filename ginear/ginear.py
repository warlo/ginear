# /usr/bin/env python3
import os

from dotenv import load_dotenv

from ginear.queries import (
    create_issue,
    get_issues,
    get_project_ids_for_team,
    get_state_ids_for_team,
    get_team_ids,
    get_user_id,
)
from ginear.utils import DOTFILE_PATH, switch_branch, write_to_env

load_dotenv(dotenv_path=DOTFILE_PATH)


LINEAR_API_TOKEN = os.environ.get("LINEAR_API_TOKEN")

TEAM_ID = os.environ.get("TEAM_ID")

PROJECT_ID = os.environ.get("PROJECT_ID")

USER_ID = os.environ.get("USER_ID")

INITIAL_STATE_ID = os.environ.get("INITIAL_STATE_ID")


def create_issue_prompt() -> None:
    title = input("Title: ")
    description = input("Description: ")
    create_issue(title, description)


def attach_issue_prompt() -> None:
    from pyfzf.pyfzf import FzfPrompt

    issues = get_issues()
    fzf = FzfPrompt()
    selected_list = fzf.prompt(
        [
            "> Create new issue",
            *[
                f"[{issue['creator']['name'][:10]}] – {issue['title']}"
                for issue in issues
            ],
        ]
    )
    if selected_list:
        selected = selected_list[0]
        if selected == "> SKIP":
            print("Skipping ticket")
            return

        if selected == "> Create new issue":
            create_issue_prompt()
            return

        issue = next(
            issue for issue in issues if issue["title"] == selected.split(" – ")[1]
        )
        branch_name = issue["branchName"]
        switch_branch(branch_name)

    print("Selected:", selected)


def run_onboarding() -> None:
    from pyfzf.pyfzf import FzfPrompt

    if not LINEAR_API_TOKEN:
        import webbrowser

        webbrowser.open("https://linear.app/settings/api")
        linear_api_token = input(
            "Insert Personal API Key (https://linear.app/settings/api): "
        )
        write_to_env("LINEAR_API_TOKEN", linear_api_token)
        load_dotenv(dotenv_path=DOTFILE_PATH)

    user_id = USER_ID
    if not user_id:
        user = get_user_id()
        user_id = user["id"]
        if not user_id:
            raise ValueError("No user id")
        write_to_env("USER_ID", user_id)

    team_id = TEAM_ID
    if not team_id:
        team_ids = get_team_ids()
        fzf = FzfPrompt()
        selected_list = fzf.prompt(
            [
                *[f"[{team_id['name']}] – {team_id['id']}" for team_id in team_ids],
            ]
        )
        if not selected_list:
            raise ValueError("Missing team ids")

        team_id = selected_list[0].split(" – ")[1]
        if not team_id:
            raise ValueError("No team id")
        write_to_env("TEAM_ID", team_id)

    project_id = PROJECT_ID
    if not project_id:
        project_ids = get_project_ids_for_team(team_id)
        fzf = FzfPrompt()
        selected_list = fzf.prompt(
            [
                *[
                    f"[{project_id['name']}] – {project_id['id']}"
                    for project_id in project_ids
                ],
            ]
        )
        if not selected_list:
            raise ValueError("Missing projects")

        project_id = selected_list[0].split(" – ")[1]
        if not project_id:
            raise ValueError("No project id")
        write_to_env("PROJECT_ID", project_id)

    initial_issue_state = INITIAL_STATE_ID
    if not initial_issue_state:
        state_ids = get_state_ids_for_team(team_id)
        fzf = FzfPrompt()
        selected_list = fzf.prompt(
            [
                *[
                    f"[{initial_issue_state['name']}] – {initial_issue_state['id']}"
                    for initial_issue_state in state_ids
                ],
            ]
        )
        if not selected_list:
            raise ValueError("Missing states")
        initial_issue_state = selected_list[0].split(" – ")[1]
        if not initial_issue_state:
            raise ValueError("No initial issue state")
        write_to_env("INITIAL_STATE_ID", initial_issue_state)

    print("🍸 Onboarding success 🍸")


def run() -> None:
    if LINEAR_API_TOKEN and TEAM_ID and PROJECT_ID and USER_ID and INITIAL_STATE_ID:
        print("🍸 Ginear ticket 🍸")
        attach_issue_prompt()
    else:
        print("🍸 Initializing ginear 🍸")
        run_onboarding()


if __name__ == "__main__":
    run()
