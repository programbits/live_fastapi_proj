# FastAPI Blog API

A small FastAPI blog API using SQLite. No PostgreSQL installation or database setup is required for local development.

## Run locally (Windows)

1. Extract this folder and open a terminal inside it.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies and start the app:

   ```powershell
   python -m pip install -r requirements.txt
   uvicorn main:app --reload
   ```

4. Open `http://127.0.0.1:8000/docs`.

On the first start, `blog.db` is created automatically in this folder. Local demo login:

- Username: `admin`
- Password: `admin123`

Change these by setting `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `SECRET_KEY` environment variables before running the app if you expose your local server to other people. Do not use the local demo password in production.

## Deploy on Render with persistent storage

The included `render.yaml` configures the web service, SQLite database path, generated admin password, generated JWT secret, and a persistent disk. To apply all of it automatically:

1. Push this project folder to a GitHub repository.
2. In Render, choose **New → Blueprint** (not just a generic Web Service) and select that repository.
3. Review and create the resources. This configuration uses a **paid Starter web service** because Render persistent disks are only available on paid services.
4. When the deploy is live, open the service's **Environment** page and copy the generated `ADMIN_PASSWORD`. The username is `admin`. Do not share the generated password publicly.
5. Your API is available at the Render service URL; add `/docs` to try the endpoints.

The database is stored at `/var/data/blog.db` on the persistent disk and survives deploys/restarts. Do not replace this with a free Render web service if you need the SQLite database to persist: the free service filesystem is ephemeral. The person using the API URL does not need to install PostgreSQL or configure a database.

## API endpoints

| Method | Endpoint | Auth required? | Purpose |
|---|---|---:|---|
| GET | `/` | No | API information |
| GET | `/health` | No | Health check |
| POST | `/login` | Username/password | Get a bearer token |
| POST | `/blogs` | Yes | Create a blog |
| GET | `/blogs` | No | List blogs, paginate, search by title |
| GET | `/blogs/{blog_id}` | No | Get one blog |
| PUT | `/blogs/{blog_id}` | Yes | Update a blog |
| DELETE | `/blogs/{blog_id}` | Yes | Delete a blog |

In Swagger (`/docs`), use **Authorize** and enter the username/password to authorize protected endpoints. Blog reads are public; blog write operations require a valid bearer token.

## Configuration

- `DATABASE_URL`: defaults to `sqlite:///./blog.db` locally.
- `ADMIN_USERNAME`: defaults to `admin` locally.
- `ADMIN_PASSWORD`: defaults to `admin123` locally only.
- `SECRET_KEY`: a local development fallback is provided; Render generates a secret automatically.

The SQLite file is intentionally excluded from Git so each local install starts with its own database.
