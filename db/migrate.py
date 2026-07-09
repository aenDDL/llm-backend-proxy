import os

from dotenv import load_dotenv
from yoyo import get_backend, read_migrations

load_dotenv()

DATABASE_URL = os.environ["PG_MIGRATIONS"]

backend = get_backend(DATABASE_URL)
migrations = read_migrations("./migrations")

with backend.lock():
    backend.apply_migrations(backend.to_apply(migrations))
