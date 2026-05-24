import os
import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager


class DatabaseTools:
    """Tools for database operations and management"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path
        self.connection = None
    
    @contextmanager
    def get_connection(self, db_path=None):
        """Context manager for database connections"""
        path = db_path or self.db_path
        if not path:
            raise ValueError("Database path not specified")
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_database(self, db_path):
        """Creates a new SQLite database"""
        conn = sqlite3.connect(db_path)
        conn.close()
        self.db_path = db_path
        return {'created': True, 'path': db_path}
    
    def create_table(self, table_name, columns, db_path=None):
        """Creates a table with specified columns"""
        columns_sql = ', '.join([f'{name} {dtype}' for name, dtype in columns.items()])
        sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})'
        with self.get_connection(db_path) as conn:
            conn.execute(sql)
            conn.commit()
        return {'table': table_name, 'created': True}
    
    def drop_table(self, table_name, db_path=None):
        """Drops a table"""
        sql = f'DROP TABLE IF EXISTS {table_name}'
        with self.get_connection(db_path) as conn:
            conn.execute(sql)
            conn.commit()
        return {'table': table_name, 'dropped': True}
    
    def insert(self, table_name, data, db_path=None):
        """Inserts a record into a table"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        with self.get_connection(db_path) as conn:
            cursor = conn.execute(sql, list(data.values()))
            conn.commit()
            return {'inserted': True, 'row_id': cursor.lastrowid}
    
    def insert_many(self, table_name, records, db_path=None):
        """Inserts multiple records"""
        if not records:
            return {'inserted': 0}
        columns = ', '.join(records[0].keys())
        placeholders = ', '.join(['?' for _ in records[0]])
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        values = [list(record.values()) for record in records]
        with self.get_connection(db_path) as conn:
            cursor = conn.executemany(sql, values)
            conn.commit()
            return {'inserted': cursor.rowcount}
    
    def select(self, table_name, columns=None, where=None, order_by=None, limit=None, db_path=None):
        """Selects records from a table"""
        cols = ', '.join(columns) if columns else '*'
        sql = f'SELECT {cols} FROM {table_name}'
        params = []
        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f'{key} = ?')
                params.append(value)
            sql += ' WHERE ' + ' AND '.join(conditions)
        if order_by:
            sql += f' ORDER BY {order_by}'
        if limit:
            sql += f' LIMIT {limit}'
        with self.get_connection(db_path) as conn:
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update(self, table_name, data, where, db_path=None):
        """Updates records in a table"""
        set_clause = ', '.join([f'{key} = ?' for key in data.keys()])
        where_clause = ' AND '.join([f'{key} = ?' for key in where.keys()])
        sql = f'UPDATE {table_name} SET {set_clause} WHERE {where_clause}'
        params = list(data.values()) + list(where.values())
        with self.get_connection(db_path) as conn:
            cursor = conn.execute(sql, params)
            conn.commit()
            return {'updated': cursor.rowcount}
    
    def delete(self, table_name, where, db_path=None):
        """Deletes records from a table"""
        where_clause = ' AND '.join([f'{key} = ?' for key in where.keys()])
        sql = f'DELETE FROM {table_name} WHERE {where_clause}'
        with self.get_connection(db_path) as conn:
            cursor = conn.execute(sql, list(where.values()))
            conn.commit()
            return {'deleted': cursor.rowcount}
    
    def execute_query(self, sql, params=None, db_path=None):
        """Executes a raw SQL query"""
        with self.get_connection(db_path) as conn:
            cursor = conn.execute(sql, params or [])
            if sql.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                conn.commit()
                return {'affected': cursor.rowcount}
    
    def get_tables(self, db_path=None):
        """Lists all tables in the database"""
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        with self.get_connection(db_path) as conn:
            cursor = conn.execute(sql)
            return [row[0] for row in cursor.fetchall()]
    
    def get_table_info(self, table_name, db_path=None):
        """Gets table schema information"""
        sql = f'PRAGMA table_info({table_name})'
        with self.get_connection(db_path) as conn:
            cursor = conn.execute(sql)
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'name': row[1],
                    'type': row[2],
                    'not_null': bool(row[3]),
                    'default': row[4],
                    'primary_key': bool(row[5])
                })
            return {'table': table_name, 'columns': columns}
    
    def get_table_count(self, table_name, where=None, db_path=None):
        """Gets record count for a table"""
        sql = f'SELECT COUNT(*) FROM {table_name}'
        params = []
        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f'{key} = ?')
                params.append(value)
            sql += ' WHERE ' + ' AND '.join(conditions)
        with self.get_connection(db_path) as conn:
            cursor = conn.execute(sql, params)
            return cursor.fetchone()[0]
    
    def backup_database(self, source_path, backup_path):
        """Creates a backup of a database"""
        import shutil
        shutil.copy2(source_path, backup_path)
        return {'backed_up': True, 'path': backup_path}
    
    def restore_database(self, backup_path, target_path):
        """Restores a database from backup"""
        import shutil
        shutil.copy2(backup_path, target_path)
        return {'restored': True, 'path': target_path}
    
    def export_to_json(self, table_name, output_path, db_path=None):
        """Exports table data to JSON"""
        data = self.select(table_name, db_path=db_path)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return {'exported': len(data), 'path': output_path}
    
    def import_from_json(self, table_name, input_path, db_path=None):
        """Imports data from JSON to table"""
        with open(input_path, 'r') as f:
            data = json.load(f)
        return self.insert_many(table_name, data, db_path)
    
    def export_to_csv(self, table_name, output_path, db_path=None):
        """Exports table data to CSV"""
        import csv
        data = self.select(table_name, db_path=db_path)
        if not data:
            return {'exported': 0}
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return {'exported': len(data), 'path': output_path}
    
    def import_from_csv(self, table_name, input_path, db_path=None):
        """Imports data from CSV to table"""
        import csv
        with open(input_path, 'r') as f:
            reader = csv.DictReader(f)
            records = list(reader)
        return self.insert_many(table_name, records, db_path)
    
    def create_index(self, table_name, columns, index_name=None, unique=False, db_path=None):
        """Creates an index on a table"""
        if index_name is None:
            index_name = f'idx_{table_name}_{"_".join(columns)}'
        unique_str = 'UNIQUE' if unique else ''
        cols = ', '.join(columns)
        sql = f'CREATE {unique_str} INDEX IF NOT EXISTS {index_name} ON {table_name} ({cols})'
        with self.get_connection(db_path) as conn:
            conn.execute(sql)
            conn.commit()
        return {'index': index_name, 'created': True}
    
    def get_indexes(self, table_name, db_path=None):
        """Gets all indexes for a table"""
        sql = f'PRAGMA index_list({table_name})'
        with self.get_connection(db_path) as conn:
            cursor = conn.execute(sql)
            indexes = []
            for row in cursor.fetchall():
                indexes.append({
                    'name': row[1],
                    'unique': bool(row[2])
                })
            return indexes
    
    def vacuum(self, db_path=None):
        """Optimizes the database"""
        with self.get_connection(db_path) as conn:
            conn.execute('VACUUM')
        return {'optimized': True}
    
    def get_database_size(self, db_path=None):
        """Gets the database file size"""
        path = db_path or self.db_path
        size = os.path.getsize(path)
        return {
            'bytes': size,
            'kb': round(size / 1024, 2),
            'mb': round(size / (1024 * 1024), 2)
        }
    
    def check_integrity(self, db_path=None):
        """Checks database integrity"""
        with self.get_connection(db_path) as conn:
            cursor = conn.execute('PRAGMA integrity_check')
            result = cursor.fetchone()[0]
            return {'intact': result == 'ok', 'result': result}
    
    def begin_transaction(self, db_path=None):
        """Begins a database transaction"""
        conn = sqlite3.connect(db_path or self.db_path)
        conn.execute('BEGIN')
        self.connection = conn
        return conn
    
    def commit_transaction(self):
        """Commits the current transaction"""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None
            return {'committed': True}
        return {'error': 'No active transaction'}
    
    def rollback_transaction(self):
        """Rollbacks the current transaction"""
        if self.connection:
            self.connection.rollback()
            self.connection.close()
            self.connection = None
            return {'rolled_back': True}
        return {'error': 'No active transaction'}
    
    def upsert(self, table_name, data, conflict_columns, db_path=None):
        """Inserts or updates on conflict"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        update_clause = ', '.join([f'{k} = excluded.{k}' for k in data.keys() if k not in conflict_columns])
        conflict = ', '.join(conflict_columns)
        sql = f'''INSERT INTO {table_name} ({columns}) VALUES ({placeholders})
                  ON CONFLICT({conflict}) DO UPDATE SET {update_clause}'''
        with self.get_connection(db_path) as conn:
            conn.execute(sql, list(data.values()))
            conn.commit()
            return {'upserted': True}
    
    def copy_table(self, source_table, target_table, db_path=None):
        """Copies a table to a new table"""
        sql = f'CREATE TABLE {target_table} AS SELECT * FROM {source_table}'
        with self.get_connection(db_path) as conn:
            conn.execute(sql)
            conn.commit()
            return {'copied': True, 'from': source_table, 'to': target_table}
    
    def truncate_table(self, table_name, db_path=None):
        """Removes all records from a table"""
        sql = f'DELETE FROM {table_name}'
        with self.get_connection(db_path) as conn:
            cursor = conn.execute(sql)
            conn.commit()
            return {'truncated': True, 'deleted': cursor.rowcount}
    
    def rename_table(self, old_name, new_name, db_path=None):
        """Renames a table"""
        sql = f'ALTER TABLE {old_name} RENAME TO {new_name}'
        with self.get_connection(db_path) as conn:
            conn.execute(sql)
            conn.commit()
            return {'renamed': True, 'from': old_name, 'to': new_name}
    
    def add_column(self, table_name, column_name, column_type, db_path=None):
        """Adds a column to a table"""
        sql = f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}'
        with self.get_connection(db_path) as conn:
            conn.execute(sql)
            conn.commit()
            return {'added': True, 'column': column_name}