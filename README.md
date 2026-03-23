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

*Note: A `requirements.txt` or `pyproject.toml` was not found in the repository. You may need to install the following
manually:*

```bash
pip install fastapi strawberry-graphql[fastapi] sqlalchemy alembic psycopg2-binary uvicorn
```

*TODO: Add a proper dependency management file (requirements.txt or pyproject.toml).*

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

#### Tasks
| Mutation | Description |
|---|---|
| `createTask(...)` | Create a new task |
| `deleteTask(taskId)` | Delete a task |
| `completeTask(taskId, userId?)` | Mark a task as completed (`userId` optional, falls back to authenticated user) |
| `uncompletedTask(taskId, userId?)` | Mark a task as uncompleted (`userId` optional, falls back to authenticated user) |

#### Houses
| Mutation | Description |
|---|---|
| `createHouse(name)` | Create a new house |
| `removeUserFromHouse(userId, houseId)` | Remove a user from a house |

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

## 🔐 Environment Variables

The application uses the following environment variables (defaults are in `app/database.py` and `alembic.ini`):

| Variable       | Description                  | Default                                           |
|----------------|------------------------------|---------------------------------------------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://myuser:password@localhost/homesync` |

## 📜 License

[Add License Info - TODO]
