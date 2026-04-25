"""Integration tests for GraphQL authentication flows (CreateUser, Login, mutations that require auth)."""

import pytest

CREATE_USER_MUTATION = """
mutation CreateUser($username: String!, $email: String!, $password: String!) {
    createUser(username: $username, email: $email, password: $password) {
        ... on User {
            id
            email
            name
            isActive
        }
        ... on UserError {
            message
        }
    }
}
"""

LOGIN_MUTATION = """
mutation Login($email: String!, $password: String!) {
    login(email: $email, password: $password) {
        ... on AuthPayload {
            token
            user { id email name }
        }
        ... on UserError {
            message
        }
    }
}
"""

GET_ME_QUERY = """
query GetMe {
    getMe {
        ... on User {
            id
            email
            name
        }
        ... on UserError {
            message
        }
    }
}
"""


class TestCreateUser:
    def test_create_user_success(self, client):
        resp = client.post("/graphql", json={
            "query": CREATE_USER_MUTATION,
            "variables": {
                "username": "Test User",
                "email": "test@example.com",
                "password": "securePassword123",
            },
        })
        data = resp.json()
        assert "errors" not in data, data
        user = data["data"]["createUser"]
        assert user["id"] is not None
        assert user["email"] == "test@example.com"
        assert user["name"] == "Test User"
        assert user["isActive"] is True

    def test_create_user_duplicate_email(self, client):
        # Create the user first
        client.post("/graphql", json={
            "query": CREATE_USER_MUTATION,
            "variables": {
                "username": "User 1",
                "email": "duplicate@example.com",
                "password": "securePassword123",
            },
        })
        # Try creating again with same email
        resp = client.post("/graphql", json={
            "query": CREATE_USER_MUTATION,
            "variables": {
                "username": "User 2",
                "email": "duplicate@example.com",
                "password": "anotherPassword123",
            },
        })
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["createUser"]
        assert result["message"] is not None
        assert "already exists" in result["message"]

    def test_create_user_invalid_email(self, client):
        resp = client.post("/graphql", json={
            "query": CREATE_USER_MUTATION,
            "variables": {
                "username": "Bad Email",
                "email": "not-an-email",
                "password": "securePassword123",
            },
        })
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["createUser"]
        assert result["message"] is not None
        assert "Invalid email" in result["message"]

    def test_create_user_short_password(self, client):
        resp = client.post("/graphql", json={
            "query": CREATE_USER_MUTATION,
            "variables": {
                "username": "Short Pwd",
                "email": "shortpwd@example.com",
                "password": "1234567",
            },
        })
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["createUser"]
        assert result["message"] is not None
        assert "8 characters" in result["message"]


class TestLogin:
    def test_login_success(self, client):
        # Create user first
        client.post("/graphql", json={
            "query": CREATE_USER_MUTATION,
            "variables": {
                "username": "Login Test",
                "email": "login@example.com",
                "password": "securePassword123",
            },
        })
        # Login
        resp = client.post("/graphql", json={
            "query": LOGIN_MUTATION,
            "variables": {
                "email": "login@example.com",
                "password": "securePassword123",
            },
        })
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["login"]
        assert result["token"] is not None
        assert len(result["token"]) > 0
        assert result["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self, client):
        # Create user first
        client.post("/graphql", json={
            "query": CREATE_USER_MUTATION,
            "variables": {
                "username": "Wrong Pwd",
                "email": "wrongpwd@example.com",
                "password": "securePassword123",
            },
        })
        # Login with wrong password
        resp = client.post("/graphql", json={
            "query": LOGIN_MUTATION,
            "variables": {
                "email": "wrongpwd@example.com",
                "password": "wrongPassword",
            },
        })
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["login"]
        assert result["message"] is not None
        assert "Invalid email or password" in result["message"]

    def test_login_nonexistent_user(self, client):
        resp = client.post("/graphql", json={
            "query": LOGIN_MUTATION,
            "variables": {
                "email": "doesnotexist@example.com",
                "password": "securePassword123",
            },
        })
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["login"]
        assert result["message"] is not None
        assert "Invalid email or password" in result["message"]

    def test_login_with_remember_me(self, client):
        # Create user first
        client.post("/graphql", json={
            "query": CREATE_USER_MUTATION,
            "variables": {
                "username": "Remember Me",
                "email": "remember@example.com",
                "password": "securePassword123",
            },
        })
        # Login with remember_me
        resp = client.post("/graphql", json={
            "query": """
            mutation Login($email: String!, $password: String!) {
                login(email: $email, password: $password, rememberMe: true) {
                    ... on AuthPayload {
                        token
                        user { id email name }
                    }
                    ... on UserError {
                        message
                    }
                }
            }
            """,
            "variables": {
                "email": "remember@example.com",
                "password": "securePassword123",
            },
        })
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["login"]
        assert result["token"] is not None
        assert result["user"]["email"] == "remember@example.com"


class TestGetMe:
    def test_get_me_authenticated(self, client):
        # Create and login
        client.post("/graphql", json={
            "query": CREATE_USER_MUTATION,
            "variables": {
                "username": "Me User",
                "email": "me@example.com",
                "password": "securePassword123",
            },
        })
        login_resp = client.post("/graphql", json={
            "query": LOGIN_MUTATION,
            "variables": {"email": "me@example.com", "password": "securePassword123"},
        })
        token = login_resp.json()["data"]["login"]["token"]

        # Get myself
        resp = client.post("/graphql", json={
            "query": GET_ME_QUERY,
        }, headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["getMe"]
        assert result["email"] == "me@example.com"
        assert result["name"] == "Me User"

    def test_get_me_unauthenticated(self, client):
        resp = client.post("/graphql", json={
            "query": GET_ME_QUERY,
        })
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["getMe"]
        assert result["message"] is not None
