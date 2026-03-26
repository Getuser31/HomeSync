# HomeSync Backend

HomeSync is a backend service for managing home-related tasks, users, and house coordination. It provides a GraphQL API
built with FastAPI and Strawberry, backed by a PostgreSQL database.

## 🛠 Tech Stack

- **Language:** Python 3.13+
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **GraphQL:** [Strawberry](https://strawberry.rocks/)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Database:** [PostgreSQL](https://www.postgresql.org/)
- **Infrastructure:** Docker (for database)

## 📋 Requirements

- Python 3.13 or higher
- Docker and Docker Compose
- Virtualenv (recommended)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd HomeSync
```

### 2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Database

The database is managed via Docker Compose.

```bash
docker-compose up -d
```

### 5. Run Migrations

Apply the latest database migrations using Alembic.

```bash
alembic upgrade head
```

### 6. Run the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

## 📡 API Usage

The application provides a GraphQL interface at:

- **GraphQL Playground:** `http://127.0.0.1:8000/graphql`
- **Root Endpoint:** `http://127.0.0.1:8000/` (returns a "Hello World" message)

### Queries

| Query | Description |
|---|---|
| `getTasks` | Get all tasks |
| `getTaskById(id)` | Get a task by ID |
| `getMe` | Get the authenticated user |
| `getAllUsers` | Get all users |
| `getHouseByInviteCode(inviteCode)` | Find a house by invite code |
| `getHouseByUser` | Get houses for the authenticated user |
| `getHouseById(id)` | Get a house by ID |
| `getTaskRecurrences` | Get all task recurrence types |
| `getRoles` | Get all available roles |

### Mutations

#### Users
| Mutation | Description |
|---|---|
| `createUser(username, email, password)` | Register a new user |
| `login(email, password)` | Authenticate and receive a JWT token |
| `updateUserRole(userId, houseId, roleId)` | Update a user's role in a house |
| `createDummyUserForHouse(houseId, username)` | Create an inactive placeholder user for a house |

#### Tasks
| Mutation | Description |
|---|---|
| `createTask(title, taskRecurrenceId, houseId, description?, weight?, userId?)` | Create a new task (admin only) |
| `deleteTask(taskId)` | Delete a task (admin only) |
| `assignTaskToUser(taskId, userId)` | Assign a task to a user (admin only) |
| `removeUserFromTask(taskId, userId)` | Remove a user from a task (admin only) |
| `completeTask(taskId, userId?)` | Mark a task as completed (`userId` optional, falls back to authenticated user) |
| `uncompletedTask(taskId, userId?)` | Mark a task as uncompleted (`userId` optional, falls back to authenticated user) |

#### Houses
| Mutation | Description |
|---|---|
| `createHouse(name)` | Create a new house (creator is assigned admin role) |
| `joinHouseByInvitationCode(inviteCode)` | Join a house using an invite code (assigned member role) |
| `addUserToHouse(userId, houseId)` | Add a user to a house (admin only) |
| `removeUserFromHouse(userId, houseId)` | Remove a user from a house (admin only) |
| `removeHouse(houseId)` | Delete a house and all its data (admin only) |

### Roles

Users can be assigned roles within a house (e.g. `admin`, `member`). The last admin of a house cannot be removed or demoted.

### Authentication

Most queries and mutations require a Bearer token in the `Authorization` header, obtained via the `login` mutation:

```
Authorization: Bearer <token>
```

## 📂 Project Structure

```text
├── alembic/              # Database migration scripts
├── alembic.ini           # Alembic configuration
├── app/
│   ├── graphql/          # Strawberry GraphQL schema, types, queries, and mutations
│   ├── services/         # Business logic services
│   ├── database.py       # SQLAlchemy engine and session setup
│   └── models.py         # SQLAlchemy database models
├── Dockerfile            # Database Docker image configuration
├── docker-compose.yml    # Docker services orchestration
├── main.py               # FastAPI application entry point
└── test_main.http        # HTTP test requests for IDEs
```

## 🧪 Testing

There is a `test_main.http` file available for testing the REST endpoints using IDEs that support `.http` files (like
WebStorm or PyCharm with the HTTP Client plugin).

*TODO: Implement automated unit and integration tests.*

## 🚢 CI/CD

A GitHub Actions workflow (`.github/workflows/backend-deploy.yml`) automatically deploys the backend on pushes to `main`.

## 🔐 Environment Variables

The application uses the following environment variables. Copy `.env.example` to `.env` and fill in the values:

| Variable       | Description                  | Default                                           |
|----------------|------------------------------|---------------------------------------------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://myuser:password@localhost/homesync` |
| `SECRET_KEY`   | JWT signing secret           | —                                                 |

## 📜 License

[Add License Info - TODO]
