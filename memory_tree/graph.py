from core.module import Module
import sqlite3
import os
import json

class KnowledgeGraph(Module):
    def __init__(self, kernel, db_path="memory_tree/knowledge.db"):
        super().__init__(kernel)
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def initialize(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_schema()
        self.kernel.log("KnowledgeGraph", f"Connected to {self.db_path}")

    def start(self):
        pass

    def stop(self):
        if self.conn:
            self.conn.close()

    def _create_schema(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS triples (
                subject TEXT,
                predicate TEXT,
                object TEXT,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(subject, predicate, object, context)
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_subject ON triples(subject)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_object ON triples(object)')
        self.conn.commit()

    def add_fact(self, subject, predicate, object, context="global"):
        """Store a semantic fact: (Sky, is, Blue)."""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO triples (subject, predicate, object, context)
                VALUES (?, ?, ?, ?)
            ''', (subject.lower(), predicate.lower(), object.lower(), context))
            self.conn.commit()
            self.kernel.log("KnowledgeGraph", f"Learned: {subject} {predicate} {object}")
            return True
        except Exception as e:
            self.kernel.log("KnowledgeGraph", f"Error adding fact: {e}", level="error")
            return False

    def query(self, subject=None, predicate=None, object=None):
        """Flexible query mechanism. None acts as wildcard."""
        query = "SELECT subject, predicate, object FROM triples WHERE 1=1"
        params = []
        
        if subject:
            query += " AND subject = ?"
            params.append(subject.lower())
        if predicate:
            query += " AND predicate = ?"
            params.append(predicate.lower())
        if object:
            query += " AND object = ?"
            params.append(object.lower())
            
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            self.kernel.log("KnowledgeGraph", f"Query error: {e}", level="error")
            return []

    def get_relations(self, entity):
        """Get all facts about an entity (as subject or object)."""
        incoming = self.query(object=entity)
        outgoing = self.query(subject=entity)
        return {"incoming": incoming, "outgoing": outgoing}
