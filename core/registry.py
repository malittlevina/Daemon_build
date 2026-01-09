from core.module import Module
import sqlite3
import json
import os

class Registry(Module):
    def __init__(self, kernel, db_path="config/registry.db"):
        super().__init__(kernel)
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def initialize(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self.kernel.log("Registry", f"Connected to {self.db_path}")

    def start(self):
        pass

    def stop(self):
        if self.conn:
            self.conn.close()

    def _create_tables(self):
        # Key-Value store for system settings
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def set(self, key, value):
        """Store a value (auto-serialized to JSON if needed)."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
            ''', (key, str(value)))
            self.conn.commit()
            return True
        except Exception as e:
            self.kernel.log("Registry", f"Error setting {key}: {e}", level="error")
            return False

    def get(self, key, default=None):
        """Retrieve a value (auto-deserialized from JSON if possible)."""
        try:
            self.cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = self.cursor.fetchone()
            if row:
                val = row[0]
                # Try to auto-parse JSON
                try:
                    return json.loads(val)
                except (json.JSONDecodeError, TypeError):
                    return val
            return default
        except Exception as e:
            self.kernel.log("Registry", f"Error getting {key}: {e}", level="error")
            return default

    def delete(self, key):
        self.cursor.execute('DELETE FROM settings WHERE key = ?', (key,))
        self.conn.commit()
