import sqlite3
import threading
from datetime import datetime, timedelta
import os
import uuid

class TrackerDB:
    """Handles database operations for the Time Tracker."""

    def __init__(self, db_path):
        """Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        """Get a thread-local database connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize the database schema."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Create tasks table (stores unique task names)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Check for status column
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'status' not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'active'")

        # Create sessions table (stores time logs)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()

    def start_session(self, task_name, category=None):
        """Start a new session for a task. Creates task if it doesn't exist.

        Args:
            task_name: Name of the task
            category: Optional category
        
        Returns:
            Dictionary with session_id, task_id, task_name, start_time
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            # Upsert task
            cursor.execute('INSERT OR IGNORE INTO tasks (name, category, status) VALUES (?, ?, ?)', (task_name, category, 'active'))
            cursor.execute("UPDATE tasks SET last_used_at = CURRENT_TIMESTAMP, status = 'active' WHERE name = ?", (task_name,))
            
            cursor.execute('SELECT id, name FROM tasks WHERE name = ?', (task_name,))
            task = cursor.fetchone()
            task_id = task['id']
            
            # Explicitly use isoformat for storage to avoid ambiguity
            start_time = datetime.now()
            cursor.execute('INSERT INTO sessions (task_id, start_time) VALUES (?, ?)', (task_id, start_time.isoformat()))
            session_id = cursor.lastrowid
            
            conn.commit()
            
            return {
                'id': session_id,
                'task_id': task_id,
                'task_name': task['name'],
                'start_time': start_time
            }
        finally:
            conn.close()

    def stop_session(self, session_id):
        """Stop a specific session.
        
        Args:
            session_id: The ID of the session to stop.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            end_time = datetime.now()
            cursor.execute('UPDATE sessions SET end_time = ? WHERE id = ?', (end_time.isoformat(), session_id))
            conn.commit()
        finally:
            conn.close()

    def rename_task(self, task_name, new_name):
        """Rename an existing task."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE tasks SET name = ? WHERE name = ?', (new_name, task_name))
            conn.commit()
        finally:
            conn.close()

    def delete_task(self, task_name):
        """Delete a task and all its sessions."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM tasks WHERE name = ?', (task_name,))
            cursor.execute('DELETE FROM sessions WHERE task_id IN (SELECT id FROM tasks WHERE name = ?)', (task_name,))
            conn.commit()
        finally:
            conn.close()

    def set_task_status(self, task_name, status):
        """Set task status (active/inactive/completed)."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE tasks SET status = ? WHERE name = ?", (status, task_name))
            conn.commit()
        finally:
            conn.close()

    def get_active_sessions(self):
        """Get all currently active (open) sessions with accumulated time for today."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            # 1. Get active sessions
            cursor.execute('''
                SELECT s.id, s.start_time, t.name as task_name, t.id as task_id
                FROM sessions s
                JOIN tasks t ON s.task_id = t.id
                WHERE s.end_time IS NULL
                ORDER BY s.start_time DESC
            ''')
            
            sessions = []
            today_start = datetime.combine(datetime.now().date(), datetime.min.time()).isoformat()
            
            for row in cursor.fetchall():
                start_val = row['start_time']
                if isinstance(start_val, str):
                    try:
                        start_time = datetime.fromisoformat(start_val)
                    except ValueError:
                        start_time = datetime.now()
                else:
                    start_time = start_val
                
                task_id = row['task_id']
                
                # 2. Calculate accumulated time for this task TODAY (excluding current session)
                cursor.execute('''
                    SELECT start_time, end_time FROM sessions 
                    WHERE task_id = ? AND end_time IS NOT NULL AND start_time >= ?
                ''', (task_id, today_start))
                
                accumulated_seconds = 0
                for s_row in cursor.fetchall():
                    try:
                        s_start = datetime.fromisoformat(s_row['start_time'])
                        s_end = datetime.fromisoformat(s_row['end_time'])
                        accumulated_seconds += (s_end - s_start).total_seconds()
                    except (ValueError, TypeError):
                        pass

                sessions.append({
                    'id': row['id'],
                    'start_time': start_time,
                    'task_name': row['task_name'],
                    'task_id': row['task_id'],
                    'accumulated_seconds': accumulated_seconds
                })
            return sessions
        finally:
            conn.close()

    def get_recent_tasks(self, limit=5):
        """Get recently used ACTIVE tasks (that are not currently running)."""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT DISTINCT t.id, t.name, t.last_used_at
                FROM tasks t
                WHERE t.status = 'active' 
                AND t.id NOT IN (
                    SELECT task_id FROM sessions WHERE end_time IS NULL
                )
                ORDER BY t.last_used_at DESC
                LIMIT ?
            ''', (limit,))
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append({
                    'id': row['id'],
                    'name': row['name']
                })
            return tasks
        finally:
            conn.close()

    def get_daily_summary(self, date=None):
        """Get summary stats for all tasks on a specific date.
        
        Returns:
            List of dicts: {name, status, total_seconds, first_start, last_pause, is_active}
        """
        if date is None:
            date = datetime.now().date()
            
        start_of_day = datetime.combine(date, datetime.min.time()).isoformat()
        end_of_day = datetime.combine(date, datetime.max.time()).isoformat()
        
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            # Get all tasks that had any session today OR are marked active/inactive
            # Actually, user wants "Summary tab should show..." usually means tasks worked on today.
            # But "Inactive tasks should still show up". 
            # I will query all tasks that have sessions today.
            
            cursor.execute('''
                SELECT DISTINCT t.id, t.name, t.status
                FROM tasks t
                JOIN sessions s ON s.task_id = t.id
                WHERE (s.start_time >= ? AND s.start_time <= ?)
                   OR (s.end_time >= ? AND s.end_time <= ?)
                   OR (s.start_time < ? AND (s.end_time IS NULL OR s.end_time > ?))
            ''', (start_of_day, end_of_day, start_of_day, end_of_day, start_of_day, end_of_day))
            
            tasks_data = []
            task_rows = cursor.fetchall()
            
            for t_row in task_rows:
                task_id = t_row['id']
                name = t_row['name']
                status = t_row['status']
                
                # Fetch sessions for this task today
                cursor.execute('''
                    SELECT start_time, end_time FROM sessions 
                    WHERE task_id = ? AND (
                        (start_time >= ? AND start_time <= ?) OR
                        (end_time >= ? AND end_time <= ?) OR
                        (start_time < ? AND (end_time IS NULL OR end_time > ?))
                    )
                    ORDER BY start_time ASC
                ''', (task_id, start_of_day, end_of_day, start_of_day, end_of_day, start_of_day, end_of_day))
                
                sessions = cursor.fetchall()
                if not sessions:
                    continue
                    
                total_seconds = 0
                first_start = None
                last_pause = None
                is_running = False
                
                now = datetime.now()
                
                for i, s_row in enumerate(sessions):
                    try:
                        start = datetime.fromisoformat(s_row['start_time'])
                        end_val = s_row['end_time']
                        
                        if i == 0:
                            first_start = start
                        
                        if end_val:
                            end = datetime.fromisoformat(end_val)
                            total_seconds += (end - start).total_seconds()
                            last_pause = end
                        else:
                            # Running session
                            total_seconds += (now - start).total_seconds()
                            is_running = True
                            # "For tasks, which are in active state, but are running, we can show 'last pause time' if they were paused at any moment."
                            # last_pause remains from previous loop iteration if any
                            
                    except ValueError:
                        pass
                
                tasks_data.append({
                    'name': name,
                    'status': status,
                    'total_seconds': total_seconds,
                    'first_start': first_start,
                    'last_pause': last_pause,
                    'is_running': is_running
                })
                
            return tasks_data
        finally:
            conn.close()

    def get_daily_sessions(self, date=None):
        """Keep existing method for Gantt chart."""
        return self.get_daily_summary(date) # Replaced usage, but Gantt uses raw sessions?
        # Wait, DashboardDialog uses get_daily_sessions for the TimelineArea which expects a list of sessions.
        # I should Restore get_daily_sessions or update DashboardDialog.
        # Restoring get_daily_sessions logic for backward compatibility with Gantt
        
        if date is None:
            date = datetime.now().date()
        start_of_day = datetime.combine(date, datetime.min.time()).isoformat()
        end_of_day = datetime.combine(date, datetime.max.time()).isoformat()
        
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
             cursor.execute('''
                SELECT s.id, s.start_time, s.end_time, t.name as task_name
                FROM sessions s
                JOIN tasks t ON s.task_id = t.id
                WHERE (s.start_time >= ? AND s.start_time <= ?)
                   OR (s.end_time >= ? AND s.end_time <= ?)
                   OR (s.start_time < ? AND (s.end_time IS NULL OR s.end_time > ?))
                ORDER BY s.start_time ASC
            ''', (start_of_day, end_of_day, start_of_day, end_of_day, start_of_day, end_of_day))
             
             sessions = []
             for row in cursor.fetchall():
                 # ... same parsing logic ...
                 start_val = row['start_time']
                 if isinstance(start_val, str):
                     try:
                         start = datetime.fromisoformat(start_val)
                     except ValueError:
                         start = datetime.now()
                 else:
                     start = start_val
                 
                 end_val = row['end_time']
                 end = None
                 if end_val:
                     if isinstance(end_val, str):
                         try:
                             end = datetime.fromisoformat(end_val)
                         except ValueError:
                             end = datetime.now()
                     else:
                         end = end_val
                 
                 sessions.append({
                    'id': row['id'],
                    'start_time': start,
                    'end_time': end,
                    'task_name': row['task_name']
                 })
             return sessions
        finally:
            conn.close()
