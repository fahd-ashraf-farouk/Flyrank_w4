# Supabase FastAPI Auth API

A production-ready RESTful API built with **FastAPI** and **Supabase Authentication**. This project demonstrates complete user authentication flows, token-based session management, protected routes with Dependency Injection, and interactive OpenAPI (Swagger) documentation.

---

## Features

- **User Authentication**: Sign up and Log in with email and password via Supabase.
- **Token Verification**: Verification of JWT Bearer Tokens for protected resources.
- **Reusable Security Middleware**: FastAPI Dependency Injection (`HTTPBearer`) enforcing auth checks.
- **Session Termination**: Secure logout endpoint terminating current session.
- **Interactive API Docs**: Built-in Swagger UI with Bearer Token Authorization support.

---

## Project Structure

```text
.
├── main.py            # FastAPI application routes and dependency logic
├── .env.example       # Example environment variables template
├── .gitignore         # Git ignore rules for sensitive files
├── swagger-docs.png   # Swagger UI preview screenshot
└── README.md          # Project documentation
```

---

## Environment Setup

### 1. Prerequisites
- Python 3.10+
- A Supabase Project ([supabase.com](https://supabase.com))

### 2. Installation
Clone the repository and install the required dependencies:

```bash
git clone [https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME

pip install fastapi uvicorn supabase python-dotenv pydantic[email]
```

### 3. Environment Variables
Create a `.env` file in the root directory (based on `.env.example`):

```env
SUPABASE_URL=[https://your-supabase-project-id.supabase.co](https://your-supabase-project-id.supabase.co)
SUPABASE_KEY=your-supabase-anon-key
PORT=3000
```

---

## Running the Application

Start the local development server:

```bash
python main.py
```

The server will start at `http://localhost:3000`.

---

## API Reference

| Endpoint | Method | Auth Required | Description |
| :--- | :---: | :---: | :--- |
| `/` | `GET` | No | Health check endpoint |
| `/public/info` | `GET` | No | Public endpoint returning open informational payload |
| `/auth/signup` | `POST` | No | Register a new user account |
| `/auth/login` | `POST` | No | Authenticate user and return Access & Refresh tokens |
| `/auth/logout` | `POST` | **Yes (Bearer)** | Invalidate current session token |
| `/protected/profile` | `GET` | **Yes (Bearer)** | Retrieve authenticated user metadata |
| `/protected/dashboard` | `GET` | **Yes (Bearer)** | Retrieve protected dashboard metrics |

---

## API Documentation & Testing (Swagger UI)

Access interactive documentation at `http://localhost:3000/docs`.

To test protected routes:
1. Execute `POST /auth/login` to obtain an `access_token`.
2. Click the **Authorize** button at the top right of the Swagger UI.
3. Paste your token into the **Value** field and click **Authorize**.
4. Test any protected route directly.

![Swagger UI Documentation](swagger-docs.png)