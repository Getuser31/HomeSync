"""Integration tests for Task-related GraphQL mutations and queries."""

import pytest

CREATE_USER_MUTATION = """
mutation CreateUser($username: String!, $email: String!, $password: String!) {
    createUser(username: $username, email: $email, password: $password) {
        ... on User { id email name isActive }
        ... on UserError { message }
    }
}
"""

LOGIN_MUTATION = """
mutation Login($email: String!, $password: String!) {
    login(email: $email, password: $password) {
        ... on AuthPayload { token user { id email name } }
        ... on UserError { message }
    }
}
"""

CREATE_HOUSE_MUTATION = """
mutation CreateHouse($name: String!) {
    createHouse(name: $name) {
        ... on House { id name inviteCode }
        ... on HouseError { message }
    }
}
"""

CREATE_TASK_MUTATION = """
mutation CreateTask($title: String!, $taskRecurrenceId: Int!, $houseId: Int!, $description: String, $weight: Int) {
    createTask(
        title: $title
        taskRecurrenceId: $taskRecurrenceId
        houseId: $houseId
        description: $description
        weight: $weight
    ) {
        ... on Task { id title description weight }
        ... on UserError { message }
    }
}
"""

GET_TASKS_QUERY = """
query GetTasks {
    getTasks {
        id
        title
        description
        house { id name }
    }
}
"""

GET_TASK_BY_ID_QUERY = """
query GetTaskById($taskId: Int!) {
    getTaskById(taskId: $taskId) {
        id
        title
        description
        weight
        house { id name }
    }
}
"""

GET_RECURRENCES_QUERY = """
query GetRecurrences {
    getTaskRecurrences {
        id
        name
        frequencyDays
    }
}
"""


def _create_user_and_login(client, username: str, email: str, password: str = "securePassword123"):
    """Helper: create a user and return their auth token."""
    client.post("/graphql", json={
        "query": CREATE_USER_MUTATION,
        "variables": {"username": username, "email": email, "password": password},
    })
    resp = client.post("/graphql", json={
        "query": LOGIN_MUTATION,
        "variables": {"email": email, "password": password},
    })
    return resp.json()["data"]["login"]["token"]


def _create_house(client, token, name="Test House"):
    """Helper: create a house and return its id and invite_code."""
    resp = client.post("/graphql", json={
        "query": CREATE_HOUSE_MUTATION,
        "variables": {"name": name},
    }, headers={"Authorization": f"Bearer {token}"})
    data = resp.json()["data"]["createHouse"]
    return data["id"], data["inviteCode"]


def _seed_recurrences(db_session):
    """Seed the task_recurrences table with standard values."""
    from app.models import TaskRecurrence

    recurrences = [
        TaskRecurrence(name="Daily", frequency_days=1),
        TaskRecurrence(name="Weekly", frequency_days=7),
        TaskRecurrence(name="Monthly", frequency_days=30),
        TaskRecurrence(name="Yearly", frequency_days=365),
    ]
    for r in recurrences:
        db_session.add(r)
    db_session.commit()


def _seed_role(db_session):
    """Seed the roles table."""
    from app.models import Role

    db_session.add(Role(name="admin"))
    db_session.add(Role(name="user"))
    db_session.commit()


class TestCreateTask:
    def test_create_task_success(self, client, db_session):
        """Full flow: create user -> login -> create house -> create task."""
        _seed_recurrences(db_session)
        _seed_role(db_session)

        token = _create_user_and_login(client, "Task Master", "taskmaster@example.com")
        house_id, _ = _create_house(client, token, "Task House")

        resp = client.post("/graphql", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {
                "title": "Clean kitchen",
                "taskRecurrenceId": 1,
                "houseId": house_id,
                "description": "Wipe counters and mop floor",
                "weight": 5,
            },
        }, headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["createTask"]
        assert result["id"] is not None
        assert result["title"] == "Clean kitchen"
        assert result["description"] == "Wipe counters and mop floor"
        assert result["weight"] == 5

    def test_create_task_without_auth(self, client, db_session):
        _seed_recurrences(db_session)
        _seed_role(db_session)

        resp = client.post("/graphql", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {
                "title": "No auth task",
                "taskRecurrenceId": 1,
                "houseId": 1,
            },
        })
        data = resp.json()
        assert "errors" in data


class TestGetTasks:
    def test_get_tasks(self, client, db_session):
        _seed_recurrences(db_session)
        _seed_role(db_session)

        token = _create_user_and_login(client, "Viewer", "viewer@example.com")
        house_id, _ = _create_house(client, token)

        # Create a task
        client.post("/graphql", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {
                "title": "Visible Task",
                "taskRecurrenceId": 1,
                "houseId": house_id,
                "weight": 3,
            },
        }, headers={"Authorization": f"Bearer {token}"})

        # Get all tasks (requires auth)
        resp = client.post("/graphql", json={
            "query": GET_TASKS_QUERY,
        }, headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert "errors" not in data, data
        tasks = data["data"]["getTasks"]
        assert isinstance(tasks, list)
        titles = [t["title"] for t in tasks]
        assert "Visible Task" in titles


class TestDeleteTask:
    def test_delete_task(self, client, db_session):
        _seed_recurrences(db_session)
        _seed_role(db_session)

        token = _create_user_and_login(client, "Deleter", "deleter@example.com")
        house_id, _ = _create_house(client, token)

        # Create a task (must provide weight since it's non-nullable)
        create_resp = client.post("/graphql", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {
                "title": "Delete Me",
                "taskRecurrenceId": 1,
                "houseId": house_id,
                "weight": 2,
            },
        }, headers={"Authorization": f"Bearer {token}"})
        task_id = create_resp.json()["data"]["createTask"]["id"]

        # Delete it
        resp = client.post("/graphql", json={
            "query": """
            mutation DeleteTask($taskId: Int!) {
                deleteTask(taskId: $taskId) {
                    ... on DeleteTaskSuccess { success }
                    ... on TaskError { message }
                }
            }
            """,
            "variables": {"taskId": task_id},
        }, headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert "errors" not in data, data
        assert data["data"]["deleteTask"]["success"] is True


class TestGetRecurrences:
    def test_get_task_recurrences(self, client, db_session):
        _seed_recurrences(db_session)
        _seed_role(db_session)

        token = _create_user_and_login(client, "Recurrence", "recur@example.com")

        resp = client.post("/graphql", json={
            "query": GET_RECURRENCES_QUERY,
        }, headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert "errors" not in data, data
        recurrences = data["data"]["getTaskRecurrences"]
        assert isinstance(recurrences, list)
        names = [r["name"] for r in recurrences]
        assert "Daily" in names
        assert "Weekly" in names
        assert "Monthly" in names
