import sqlite3
from pathlib import Path
import os
import json

class Database:
    def __init__(self, db_path='db/docs.db'):

        self.db_path = Path(__file__).parent / db_path
        
        db_dir = self.db_path.parent
        if not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                user TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS attributes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                attr_key TEXT,
                attr_value TEXT
            )
        ''')
        
        self.conn.commit()
        
        
    def add_doc(self, filename,user):
        curs = self.conn.execute(
            """INSERT INTO documents (filename,user) VALUES (?)""",
            (filename,user)
        )
        
        self.conn.commit()
        print("succesfuly saved document ")
        return curs.lastrowid
    
    
    def save_attributes(self, doc_id, attrs):

        for key, value in attrs.items():
            if value is None:
                continue
            

            if isinstance(value, list):
                value = json.dumps(value)
            

            if isinstance(value, dict):
                value = json.dumps(value)
                
            self.conn.execute(
                """INSERT INTO attributes (document_id, attr_key, attr_value) VALUES (?, ?, ?)""",
                (doc_id, key, value)
            )
            
        self.conn.commit()
        
        
    def get_document(self, doc_id):

        doc = self.conn.execute(
            """SELECT * FROM documents WHERE id = ?""", 
            (doc_id,)
        ).fetchone()
        
        attrs = self.conn.execute(
            """SELECT attr_key, attr_value FROM attributes WHERE document_id = ?""", (doc_id,)
        ).fetchall()
        attrs = {}
        for row in attrs:
            key = row['attr_key']
            value = row['attr_value']
            
            # Пытаемся распарсить JSON обратно в список/словарь
            if key in ['parties', 'additional_data']:
                try:
                    value = json.loads(value)
                except:
                    pass
            
            attrs[key] = value
        return {
            'id': doc[0],
            'file_name': doc[1],
            'status': doc[3],
            'attributes': dict(attrs)
        }

    def get_docs_by_user(self, user):
        cur = self.conn.execute(
            """SELECT id, filename, upload_date FROM documents WHERE user = ?""",
            (user,)
        ).fetchall()
        
        return cur
    
    def get_all_docs(self):
        cur = self.conn.execute(
            """SELECT id, filename, upload_date FROM documents"""
        ).fetchall()
        
        return cur
    
    def get_attributes(self, doc_id):
        cur = self.conn.execute(
            """SELECT attr_key, attr_value FROM attributes WHERE document_id = ?""",
            (doc_id,)
        ).fetchall()
        
        return cur