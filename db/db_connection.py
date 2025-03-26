import os
import psycopg2
import psycopg2.extras

class DBConnection:
    def __init__(self):
        conn_str = os.environ.get("BETS_DB_CONN_STR")
        self.conn = psycopg2.connect(conn_str)

    def get_cursor(self, commit=False):
        """
        Returns a database cursor.
        If commit=True, changes will be committed automatically.
        """
        return self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def commit(self):
        """Commits the current transaction."""
        try:
            self.conn.commit()
        except Exception as e:
            print(f"Error committing transaction: {e}")
            self.conn.rollback()  # Ensures rollback if commit fails

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Allows using 'with' statements for automatic resource management."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Handles exceptions and ensures the connection is properly closed."""
        if exc_type is not None:
            self.conn.rollback()  # Rollback in case of an error
        self.conn.close()
