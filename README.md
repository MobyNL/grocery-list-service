# Grocery List Service

FastAPI backend service for managing grocery lists and items.

## Features

- **Grocery Lists**: Create multiple grocery lists (e.g., "Weekly Shopping", "Party Supplies")
- **Grocery Items**: Add items to lists with quantity, unit, category, and notes
- **Authentication**: JWT-based authentication integrated with user-service
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic for database schema management
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL database
- Poetry (optional, but recommended)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Or with Poetry:
```bash
poetry install
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Update the `.env` file with your database URL and JWT secret:
```
DATABASE_URL=postgresql://user:password@localhost:5432/grocery_db
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
FRONTEND_URL=http://localhost:4200
```

4. Run database migrations:
```bash
alembic upgrade head
```

### Running the Service

Development mode:
```bash
uvicorn app.main:app --reload --port 8002
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## API Endpoints

### Grocery Lists

- `GET /api/lists/` - Get all lists for current user
- `GET /api/lists/{list_id}` - Get a specific list with items
- `POST /api/lists/` - Create a new list
- `PUT /api/lists/{list_id}` - Update a list
- `DELETE /api/lists/{list_id}` - Delete a list

### Grocery Items

- `GET /api/items/list/{list_id}` - Get all items for a list
- `GET /api/items/{item_id}` - Get a specific item
- `POST /api/items/list/{list_id}` - Add item to a list
- `PUT /api/items/{item_id}` - Update an item
- `PATCH /api/items/{item_id}/purchased` - Mark item as purchased/unpurchased
- `DELETE /api/items/{item_id}` - Delete an item

### Other

- `GET /` - Root endpoint
- `GET /health` - Health check

## Database Schema

### Grocery Lists
- `id`: Primary key
- `name`: List name (required)
- `description`: Optional description
- `owner`: Username (from user-service)
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Grocery Items
- `id`: Primary key
- `grocery_list_id`: Foreign key to grocery_lists
- `name`: Item name (required)
- `quantity`: Numeric quantity (default: 1.0)
- `unit`: Unit of measurement (e.g., "kg", "lbs", "pieces")
- `category`: Item category (e.g., "Produce", "Dairy")
- `notes`: Additional notes
- `purchased`: Boolean flag
- `created_at`: Timestamp
- `updated_at`: Timestamp

## Authentication

All endpoints (except `/` and `/health`) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

The JWT token should be obtained from the user-service.

## Development

### Creating Database Migrations

After modifying models in `app/models.py`:

```bash
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

### Project Structure

```
grocery-list-service/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database connection
│   ├── crud.py           # Database operations
│   ├── auth.py           # JWT authentication
│   └── routes/
│       ├── lists.py      # List endpoints
│       └── items.py      # Item endpoints
├── alembic/              # Database migrations
├── pyproject.toml        # Poetry dependencies
├── requirements.txt      # Pip dependencies
└── .env                  # Environment variables
```

## License

MIT
