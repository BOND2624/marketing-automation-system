# Quick Database Inspection Commands

Use these commands from the project root (`final-year-project`) to inspect
PostgreSQL tables inside the Docker container.

> Prerequisite: Docker Desktop running.

## 1. Start the containers (one-time per session)

```
docker compose up -d
```

## 2. List all tables

```
docker compose exec postgres psql -U user -d marketing_cdp -c "\dt"
```

## 3. Describe a specific table (example: campaigns)

```
docker compose exec postgres psql -U user -d marketing_cdp -c "\d campaigns"
```

Replace `campaigns` with any table name from the previous list.

## 4. Preview the most recent campaigns

```
docker compose exec postgres psql -U user -d marketing_cdp -c "SELECT campaign_id, name, channel, status, created_at FROM campaigns ORDER BY campaign_id DESC LIMIT 5;"
```

## 5. Preview execution history for a campaign (change the ID)

```
docker compose exec postgres psql -U user -d marketing_cdp -c "SELECT execution_id, campaign_id, status, results, created_at FROM campaign_executions WHERE campaign_id = 11 ORDER BY execution_id DESC LIMIT 5;"
```

## 6. Exit the database shell (if you open interactive psql)

```
\q
```

## 7. Clear data (keep tables & schema)

Delete all rows from a table (example: `campaigns`):

```
docker compose exec postgres psql -U user -d marketing_cdp -c "DELETE FROM campaigns;"
```

Alternatively, truncate (faster, resets auto-increment IDs):

```
docker compose exec postgres psql -U user -d marketing_cdp -c "TRUNCATE TABLE campaigns RESTART IDENTITY;"
```

To clear multiple tables while respecting foreign keys (example keeps `users`):

```
docker compose exec postgres psql -U user -d marketing_cdp -c "TRUNCATE TABLE campaign_executions, campaigns, analytics_snapshots, channel_credentials, customer_events, customers RESTART IDENTITY CASCADE;"
```

Use `DELETE` when you want to keep IDs untouched; use `TRUNCATE ... RESTART IDENTITY` when you want to reset auto-increment counters.

That’s it—use these to inspect any table or data snapshot quickly.

