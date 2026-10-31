import os
from dotenv import load_dotenv
import libsql

load_dotenv()

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")


def get_db_connection():
  # เชื่อมต่อตรงไปยัง Turso บน Cloud
  conn = libsql.connect(
      database=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN
  )
  return conn