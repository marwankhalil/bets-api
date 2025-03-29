import os
import psycopg2
import psycopg2.extras

class DBConnection:
    def __init__(self):
        conn_str = os.environ.get("BETS_DB_CONN_STR")
        self.conn = psycopg2.connect(conn_str)
        self.conn.autocommit = True  # Enable auto-commit mode

    def get_cursor(self):
        """
        Returns a database cursor.
        All changes will be committed automatically.
        """
        return self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Allows using 'with' statements for automatic resource management."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Handles exceptions and ensures the connection is properly closed."""
        self.conn.close()
