"""Integration tests for House-related GraphQL mutations and queries."""

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

GET_HOUSE_BY_USER_QUERY = """
query GetHouseByUser {
    getHouseByUser {
        id
        name
        inviteCode
        users { id email name }
        currentUserRole { id name }
    }
}
"""

GET_HOUSE_BY_INVITE_CODE_QUERY = """
query GetHouseByInviteCode($inviteCode: String!) {
    getHouseByInviteCode(inviteCode: $inviteCode) {
        id
        name
        inviteCode
    }
}
"""


def _seed_roles(db_session):
    """Seed the roles table."""
    from app.models import Role
    db_session.add(Role(name="admin"))
    db_session.add(Role(name="user"))
    db_session.commit()


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


class TestCreateHouse:
    def test_create_house_success(self, client, db_session):
        _seed_roles(db_session)
        token = _create_user_and_login(client, "Home Owner", "owner@example.com")
        resp = client.post("/graphql", json={
            "query": CREATE_HOUSE_MUTATION,
            "variables": {"name": "My Family House"},
        }, headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["createHouse"]
        assert result["id"] is not None
        assert result["name"] == "My Family House"
        assert result["inviteCode"] is not None

    def test_create_house_unauthenticated(self, client):
        resp = client.post("/graphql", json={
            "query": CREATE_HOUSE_MUTATION,
            "variables": {"name": "No Auth House"},
        })
        data = resp.json()
        # Should return 401 since not in PUBLIC_OPERATIONS
        assert "errors" in data
        assert any("Not authenticated" in str(e) for e in data["errors"])


class TestGetHouseByUser:
    def test_get_house_by_user_success(self, client, db_session):
        _seed_roles(db_session)
        token = _create_user_and_login(client, "User A", "usera@example.com")
        # Create a house
        client.post("/graphql", json={
            "query": CREATE_HOUSE_MUTATION,
            "variables": {"name": "User A House"},
        }, headers={"Authorization": f"Bearer {token}"})

        # Retrieve houses
        resp = client.post("/graphql", json={
            "query": GET_HOUSE_BY_USER_QUERY,
        }, headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert "errors" not in data, data
        houses = data["data"]["getHouseByUser"]
        assert isinstance(houses, list)
        assert len(houses) == 1
        assert houses[0]["name"] == "User A House"

    def test_get_house_by_user_no_houses(self, client, db_session):
        _seed_roles(db_session)
        token = _create_user_and_login(client, "Lonely", "lonely@example.com")
        resp = client.post("/graphql", json={
            "query": GET_HOUSE_BY_USER_QUERY,
        }, headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert "errors" not in data, data
        houses = data["data"]["getHouseByUser"]
        assert isinstance(houses, list)
        assert len(houses) == 0

    def test_get_house_by_user_unauthenticated(self, client):
        resp = client.post("/graphql", json={
            "query": GET_HOUSE_BY_USER_QUERY,
        })
        data = resp.json()
        # getHouseByUser without auth returns None (resolver handles gracefully)
        assert "errors" not in data, data
        assert data["data"]["getHouseByUser"] is None


class TestGetHouseByInviteCode:
    def test_get_house_by_invite_code(self, client, db_session):
        _seed_roles(db_session)
        token = _create_user_and_login(client, "Code Owner", "code@example.com")
        # Create house to get invite code
        create_resp = client.post("/graphql", json={
            "query": CREATE_HOUSE_MUTATION,
            "variables": {"name": "Code House"},
        }, headers={"Authorization": f"Bearer {token}"})
        invite_code = create_resp.json()["data"]["createHouse"]["inviteCode"]

        # Fetch by invite code (no auth required — public operation)
        resp = client.post("/graphql", json={
            "query": GET_HOUSE_BY_INVITE_CODE_QUERY,
            "variables": {"inviteCode": invite_code},
        })
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["getHouseByInviteCode"]
        assert result is not None
        assert result["name"] == "Code House"
        assert result["inviteCode"] == invite_code

    def test_get_house_by_invite_code_not_found(self, client):
        resp = client.post("/graphql", json={
            "query": GET_HOUSE_BY_INVITE_CODE_QUERY,
            "variables": {"inviteCode": "NONEXISTENT"},
        })
        data = resp.json()
        assert "errors" not in data, data
        assert data["data"]["getHouseByInviteCode"] is None


class TestJoinHouse:
    def test_join_house_by_invite_code(self, client, db_session):
        _seed_roles(db_session)
        # User A creates a house
        token_a = _create_user_and_login(client, "User A", "joina@example.com")
        create_resp = client.post("/graphql", json={
            "query": CREATE_HOUSE_MUTATION,
            "variables": {"name": "Joinable House"},
        }, headers={"Authorization": f"Bearer {token_a}"})
        invite_code = create_resp.json()["data"]["createHouse"]["inviteCode"]

        # User B joins the house
        token_b = _create_user_and_login(client, "User B", "joinb@example.com")
        resp = client.post("/graphql", json={
            "query": """
            mutation JoinHouse($inviteCode: String!) {
                joinHouseByInvitationCode(inviteCode: $inviteCode) {
                    ... on House { id name inviteCode }
                    ... on HouseError { message }
                }
            }
            """,
            "variables": {"inviteCode": invite_code},
        }, headers={"Authorization": f"Bearer {token_b}"})
        data = resp.json()
        assert "errors" not in data, data
        result = data["data"]["joinHouseByInvitationCode"]
        assert result["id"] is not None
        assert result["name"] == "Joinable House"

        # Verify User B can now see the house
        houses_resp = client.post("/graphql", json={
            "query": GET_HOUSE_BY_USER_QUERY,
        }, headers={"Authorization": f"Bearer {token_b}"})
        houses_data = houses_resp.json()
        house_names = [h["name"] for h in houses_data["data"]["getHouseByUser"]]
        assert "Joinable House" in house_names
