# Grocery List Service - Vercel Deployment Guide

## Architecture

This service follows standard FastAPI conventions for Vercel deployment:

- `app/main.py` - Main FastAPI application entry point (auto-detected by Vercel)
- `app/` - Application code (routes, models, CRUD, database)
- `requirements.txt` - Python dependencies for Vercel

**Note:** No `vercel.json` needed! Vercel automatically detects FastAPI apps in `app/main.py`.

## Local Development

```bash
# Install dependencies
poetry install

# Run locally
poetry run uvicorn app.main:app --port 8002 --reload
```

## Vercel Deployment

### Prerequisites

1. Install Vercel CLI: `npm i -g vercel`
2. Link your project: `vercel link`

### Environment Variables

Set these in your Vercel project settings:

```bash
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
SECRET_KEY=your-secret-key-here
FRONTEND_URL=https://your-frontend.vercel.app
```

Or add them via CLI:

```bash
vercel env add DATABASE_URL
vercel env add SECRET_KEY
vercel env add FRONTEND_URL
```

### Deploy

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

## Important Notes

- Vercel automatically detects FastAPI apps in `app/main.py` (no vercel.json needed!)
- Vercel uses serverless functions, so database connections should use connection pooling
- Environment variables are managed through Vercel dashboard or CLI
- CORS is configured to allow your frontend URL (set via FRONTEND_URL env var)
- The `.vercelignore` file ensures Vercel uses `requirements.txt` instead of Poetry

## Testing Deployment

Once deployed, test the health endpoint:

```bash
curl https://your-deployment.vercel.app/
```

Expected response:
```json
{"message": "Grocery List Service is running"}
```

## Troubleshooting

### "No fastapi entrypoint found"
- Ensure `app/main.py` exists and exports the FastAPI `app` instance
- The `app/` folder structure is standard for FastAPI projects
- Check that `requirements.txt` is in the root directory

### "No Python version specified in pyproject.toml"
- Ensure `pyproject.toml` and `poetry.lock` are in `.vercelignore`
- Vercel should use `requirements.txt` instead
- Python 3.12 will be used by default

### Database connection errors
- Verify DATABASE_URL is set correctly in Vercel environment variables
- Ensure your database accepts connections from Vercel's IP range
- For Neon/serverless databases, use pooled connection strings

### CORS errors
- Add your frontend URL to FRONTEND_URL environment variable
- Check that credentials are being sent correctly from frontend

## Alembic Migrations

Note: Alembic migrations are excluded from deployment (in `.vercelignore`).
Run migrations manually on your database before deploying:

```bash
# Locally with your production database
DATABASE_URL=your_production_db alembic upgrade head
```
