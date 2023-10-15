# /usr/bin/env python3
import json
import os
from typing import Any, cast

import requests
import typer
from dotenv import load_dotenv
from rich.progress import Progress, SpinnerColumn, TextColumn

from ginear.utils import DOTFILE_PATH, clear_env_key, switch_branch

load_dotenv(dotenv_path=DOTFILE_PATH)


TEAM_ID = os.environ.get("TEAM_ID")

PROJECT_ID = os.environ.get("PROJECT_ID")

USER_ID = os.environ.get("USER_ID")

INITIAL_STATE_ID = os.environ.get("INITIAL_STATE_ID")


def get_user_id() -> dict[str, Any]:
    query = """
    query Me {
        viewer {
            id
            name
            email
            teams {
                nodes {
                    id
                    name
                }
            }
        }
    }
    """

    request_data = {"query": query}

    result = call_linear_api(request_data)
    return cast(dict[str, Any], result["viewer"])


def get_team_ids() -> list[dict[str, Any]]:
    query = """
    query {
        teams(first: 250) {
            nodes {
                id
                name
            }
        }
    }
    """

    request_data = {"query": query}

    result = call_linear_api(request_data)
    return cast(list[dict[str, Any]], result["teams"]["nodes"])


def get_project_ids_for_team(team_id: str) -> list[dict[str, Any]]:
    query = """
    query GetProjectsInTeam($teamId: String!) {
        team(id: $teamId) {
            id
            name
            projects {
                nodes {
                    id
                    name
                }
            }
        }
    }
    """

    variables = {
        "teamId": team_id,
    }

    request_data = {"query": query, "variables": variables}

    result = call_linear_api(request_data)
    return cast(list[dict[str, Any]], result["team"]["projects"]["nodes"])


def get_state_ids_for_team(team_id: str) -> list[dict[str, Any]]:
    query = """
    query GetStatesAndPrioritiesInProject($teamId: String!) {
        team(id: $teamId) {
            id
            name
            states {
                nodes {
                    id
                    name
                }
            }
        }
    }
    """

    variables = {
        "teamId": team_id,
    }

    request_data = {"query": query, "variables": variables}

    result = call_linear_api(request_data)
    return cast(list[dict[str, Any]], result["team"]["states"]["nodes"])


def get_issues(titleQuery: str | None = None) -> list[dict[str, Any]]:
    query = """
    query ($teamId: String!, $filter: IssueFilter) {
        team (id: $teamId) {
            issues(first:250, filter:$filter) {
                edges {
                    node {
                        id
                        title
                        branchName
                        creator {
                            name
                        }
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
    }
    """

    variables = {
        "teamId": TEAM_ID,
        "filter": {"title": {"containsIgnoreCase": titleQuery}},
    }

    request_data = {"query": query, "variables": variables}
    result = call_linear_api(request_data)

    return [edge["node"] for edge in result["team"]["issues"]["edges"]]


def create_issue(title: str, description: str) -> None:
    mutation = """
    mutation IssueCreate($title: String!, $description: String!, $teamId: String!, $assigneeId: String!, $stateId: String!, $projectId: String!) {
    issueCreate(
        input: {
            title: $title
            description: $description
            teamId: $teamId
            assigneeId: $assigneeId
            stateId: $stateId
            projectId: $projectId
        }
    ) {
        success
            issue {
                id
                title
                branchName
                url
            }
        }
    }
    """

    mutation_variables = {
        "title": title,
        "description": description,
        "teamId": TEAM_ID,
        "assigneeId": USER_ID,
        "stateId": INITIAL_STATE_ID,
        "projectId": PROJECT_ID,
    }

    request_data = {"query": mutation, "variables": mutation_variables}
    result = call_linear_api(request_data)
    issue_create_response = result["issueCreate"]

    if issue_create_response["success"]:
        issue = issue_create_response["issue"]
        print(
            f"Issue created successfully. Title: {issue['title']}, Branch: {issue['branchName']}, URL: {issue['url']}"
        )
        switch_branch(issue["branchName"])
    else:
        print("Issue creation failed.")


def call_linear_api(request_data: dict[str, Any]) -> dict[str, Any]:
    LINEAR_API_TOKEN = os.environ.get("LINEAR_API_TOKEN")

    if not LINEAR_API_TOKEN:
        load_dotenv(dotenv_path=DOTFILE_PATH)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{LINEAR_API_TOKEN}",
    }

    api_endpoint = "https://api.linear.app/graphql"

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        progress.add_task(description="Pouring gin... 🍸", total=False)
        response = requests.post(
            api_endpoint, data=json.dumps(request_data), headers=headers
        )

    response_data = response.json()

    if "errors" in response_data:
        print(f"Error calling {api_endpoint}")
        print(response_data["errors"])
        try:
            if (
                response_data["errors"][0]["extensions"]["code"]
                == "AUTHENTICATION_ERROR"
            ):
                clear_env_key("LINEAR_API_TOKEN")
            print("Invalid API token")
            raise typer.Exit()
        except Exception:
            pass

        raise Exception("Unknown API error")

    result = response_data["data"]
    return cast(dict[str, Any], result)
