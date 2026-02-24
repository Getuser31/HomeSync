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

### Example Queries

You can browse the schema and test queries in the GraphQL Playground.

**Get all tasks:**

```graphql
query {
    getTasks {
        id
        title
        description
        isCompleted
    }
}
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
