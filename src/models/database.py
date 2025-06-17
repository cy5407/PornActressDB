# -*- coding: utf-8 -*-
"""
資料庫管理模組
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# 修正 sqlite3 DeprecationWarning
sqlite3.register_adapter(datetime, lambda val: val.isoformat())
sqlite3.register_converter("timestamp", lambda val: datetime.fromisoformat(val.decode()))


class SQLiteDBManager:
    """SQLite 資料庫管理器"""
    
    def __init__(self, db_path: str):
        if not db_path: 
            raise ValueError("資料庫路徑不能為空。請檢查您的 config.ini 檔案。")
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_schema()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    
    def _create_schema(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, original_filename TEXT, file_path TEXT, studio TEXT, search_method TEXT, last_updated TIMESTAMP)')
            cursor.execute('CREATE TABLE IF NOT EXISTS actresses (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)')
            cursor.execute('CREATE TABLE IF NOT EXISTS video_actress_link (video_id INTEGER, actress_id INTEGER, PRIMARY KEY (video_id, actress_id), FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE, FOREIGN KEY (actress_id) REFERENCES actresses(id) ON DELETE CASCADE)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_code ON videos(code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_actress_name ON actresses(name)')
            conn.commit()
    
    def add_or_update_video(self, code: str, info: Dict):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM videos WHERE code = ?", (code,))
            video_row = cursor.fetchone()
            if video_row:
                video_id = video_row[0]
                cursor.execute("UPDATE videos SET original_filename=?, file_path=?, studio=?, search_method=?, last_updated=? WHERE id=?", (info.get('original_filename'), str(info.get('file_path')), info.get('studio'), info.get('search_method'), datetime.now(), video_id))
            else:
                cursor.execute("INSERT INTO videos (code, original_filename, file_path, studio, search_method, last_updated) VALUES (?, ?, ?, ?, ?, ?)", (code, info.get('original_filename'), str(info.get('file_path')), info.get('studio'), info.get('search_method'), datetime.now()))
                video_id = cursor.lastrowid
            actress_names = info.get('actresses', [])
            if not actress_names: 
                conn.commit()
                return
            actress_ids = []
            for name in actress_names:
                cursor.execute("INSERT OR IGNORE INTO actresses (name) VALUES (?)", (name,))
                cursor.execute("SELECT id FROM actresses WHERE name = ?", (name,))
                actress_id_row = cursor.fetchone()
                if actress_id_row: 
                    actress_ids.append(actress_id_row[0])
            cursor.execute("DELETE FROM video_actress_link WHERE video_id = ?", (video_id,))
            if actress_ids:
                link_data = [(video_id, actress_id) for actress_id in actress_ids]
                cursor.executemany("INSERT OR IGNORE INTO video_actress_link (video_id, actress_id) VALUES (?, ?)", link_data)
            conn.commit()
    
    def get_video_info(self, code: str) -> Optional[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos WHERE code = ?", (code,))
            video_row = cursor.fetchone()
            if not video_row: 
                return None
            video_id, code_val, *video_data = video_row
            cursor.execute("SELECT a.name FROM actresses a JOIN video_actress_link va ON a.id = va.actress_id WHERE va.video_id = ?", (video_id,))
            actresses = [row[0] for row in cursor.fetchall()]
            return {
                'code': code_val, 
                'original_filename': video_data[0], 
                'file_path': video_data[1], 
                'studio': video_data[2], 
                'search_method': video_data[3], 
                'last_updated': video_data[4], 
                'actresses': actresses
            }
    
    def get_all_videos(self) -> List[Dict]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos")
            return [dict(row) for row in cursor.fetchall()]
