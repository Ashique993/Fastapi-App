# FastAPI User Visit Tracker

This project captures visitor details (timestamp, OS, browser, etc.) when they open the frontend page and stores them in a PostgreSQL database via Alembic migrations and a FastAPI backend. The frontend is served by Nginx, and the entire stack runs in Docker containers.

## Prerequisites

- Docker & Docker Compose installed
- Git installed

## Folder Structure

```
Fastapi App/
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── README
│   ├── alembic.ini
│   ├── crud.py
│   ├── database.py
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── start.sh
├── frontend/
│   ├── Dockerfile
│   └── index.html
└── docker-compose.yml
```

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/fastapi-visit-tracker.git
cd fastapi-visit-tracker
```

## 2. Build & Run

```bash
docker compose up --build
```

- This command will:
  1. Download base images and build the `backend` and `frontend` services
  2. Start PostgreSQL and initialize the database
  3. Run Alembic migrations to create the `user_visit` table
  4. Launch FastAPI on http://localhost:8000
  5. Serve the frontend on http://localhost:3000

## 3. Verify Installation

- **Frontend**: Open http://localhost:3000 → you should see **Hi**.
- **API Docs**: Navigate to http://localhost:8000/docs to explore and test the API.
- **Recent Visits**: Check stored visits:
  ```bash
  curl http://localhost:8000/
  ```

## 4. Key Endpoints

- `POST /`  – Track a new visit (used by frontend script)


## 5. Development Workflow

1. **Modify models** in `backend/models.py` and run:
   ```bash
   docker compose down
   rm backend/alembic/versions/*.py
   docker volume rm fastapiapp_pgdata
   docker compose up --build
   ```
2. **Write migrations**: Alembic will auto-generate scripts (`alembic revision --autogenerate`). Edits to `script.py.mako` ensure `import sqlmodel` is included automatically.
3. **Frontend changes**: Edit `frontend/index.html` for UI updates and rebuild.

## 6. Troubleshooting

- **ModuleNotFoundError in migrations**: Ensure `alembic/script.py.mako` includes `import sqlmodel`, and `env.py` adds the backend path to `sys.path`.
- **404 on root**: Confirm `frontend/index.html` served by Nginx and port mapping `3000:80` in `docker-compose.yml`.
- **No data stored**: Check browser developer console for payload errors and FastAPI logs.

---
Happy tracking!