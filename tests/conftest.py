import os

# Ensure tests run in a test mode and use a local SQLite DB by default to avoid
# requiring a running PostgreSQL instance during unit tests on developers' machines.
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_db.sqlite")
