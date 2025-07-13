# MySQL to PostgreSQL Migration Guide for AREN

This guide explains how to migrate the AREN database from MySQL to PostgreSQL.

## Prerequisites

1. PostgreSQL 13+ installed and running
2. Python 3.8+ with pip
3. Original MySQL database accessible

## Migration Process

### 1. Install Required Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- SQLAlchemy
- psycopg2-binary
- pandas
- mysql-connector-python

### 2. Run the Migration Script

The migration process is fully automated with the `setup_postgres.py` script:

```bash
python setup_postgres.py
```

This script will:
1. Check PostgreSQL installation
2. Create and initialize the PostgreSQL database
3. Migrate data from MySQL to PostgreSQL
4. Verify the PostgreSQL connection

### 3. Manual Steps (if needed)

If the automatic migration fails, you can run each step manually:

```bash
# Create PostgreSQL database
sudo -u postgres psql -c "CREATE DATABASE aren_conversations WITH TEMPLATE template0"

# Create PostgreSQL user
sudo -u postgres psql -c "CREATE USER aren WITH PASSWORD 'aren_password'"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aren_conversations TO aren"
sudo -u postgres psql -d aren_conversations -c "GRANT ALL ON SCHEMA public TO aren"

# Create tables
python create_tables.py

# Migrate data from MySQL to PostgreSQL
python migrate_mysql_to_postgres.py
```

## Database Configuration

The PostgreSQL database is configured with these default settings:
- Host: localhost
- Port: 5432
- User: aren
- Password: aren_password
- Database: aren_conversations

You can modify these settings in `utils/database.py` if needed.

## Verification

To verify the migration was successful:

1. Run AREN with the new PostgreSQL database:
```bash
python main.py
```

2. Check the logs for any database connection errors

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure PostgreSQL is running
   - Verify port 5432 is open
   - Check credentials in `utils/database.py`

2. **Missing Tables**
   - Run `python init_postgres_db.py` to create tables

3. **Data Migration Errors**
   - Check MySQL connection details in `migrate_mysql_to_postgres.py`
   - Ensure MySQL service is running

### Logs

Check the logs directory for detailed error messages:
```
logs/aren_*.log
```

## Rollback

To roll back to MySQL, edit `utils/database.py` and change the connection string back to MySQL:

```python
connection_string = (
    f"mysql+mysqlconnector://{db_user}:{db_password}@"
    f"{db_host}:{db_port}/{db_name}"
)
``` 