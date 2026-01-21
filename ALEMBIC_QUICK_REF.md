# Alembic Quick Reference

## Using Named Sections (Recommended)

### Test Database Commands
```bash
# Create new migration
poetry run alembic -n test revision --autogenerate -m "add new column"

# Apply all migrations
poetry run alembic -n test upgrade head

# Rollback one migration
poetry run alembic -n test downgrade -1

# Show current version
poetry run alembic -n test current

# Show history
poetry run alembic -n test history
```

### Production Database Commands
```bash
# First: Set DATABASE_URL in .env or export it
# DATABASE_URL=postgresql://neondb_owner:...

# Apply all migrations
poetry run alembic -n prod upgrade head

# Rollback one migration
poetry run alembic -n prod downgrade -1

# Show current version
poetry run alembic -n prod current
```

## Alternative: Using Wrapper Scripts

### Test Database Commands (Windows)
```bash
# Create new migration
alembic-test.bat revision --autogenerate -m "add new column"

# Apply all migrations
alembic-test.bat upgrade head

# Rollback one migration
alembic-test.bat downgrade -1

# Show current version
alembic-test.bat current

# Show history
alembic-test.bat history
```

## Production Database Commands (Windows)
```bash
# Apply all migrations (with confirmation prompt)
alembic-prod.bat upgrade head

# Rollback one migration (with confirmation prompt)
alembic-prod.bat downgrade -1
```

## Important Notes

1. **Test Database**: Located at `./grocery_test.db` (SQLite file)
2. **Production Database**: Neon PostgreSQL (configured in `.env.prod`)
3. **Always test migrations on SQLite first** before running on production
4. **Production script asks for confirmation** to prevent accidents
5. **Never commit** `.env` or `.env.prod` files

## Workflow

1. Create migration: `alembic-test.bat revision --autogenerate -m "description"`
2. Review the generated migration file in `alembic/versions/`
3. Test on SQLite: `alembic-test.bat upgrade head`
4. Test your application with the SQLite database
5. When ready for production: `alembic-prod.bat upgrade head`
