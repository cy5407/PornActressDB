#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查資料庫結構
"""

import sqlite3
from pathlib import Path

def main():
    print("=== 檢查資料庫結構 ===")
    
    # 資料庫路徑
    db_path = Path.home() / "Documents" / "ActressClassifier" / "actress_database.db"
    print(f"資料庫路徑: {db_path}")
    
    if not db_path.exists():
        print("❌ 資料庫檔案不存在！")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查看所有資料表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n可用的資料表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # 檢查每個資料表的結構
    for table in tables:
        table_name = table[0]
        print(f"\n=== {table_name} 資料表結構 ===")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            cid, name, type_, notnull, default, pk = col
            print(f"  {name}: {type_} {'(主鍵)' if pk else ''}")
        
        # 查看前幾筆資料
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  資料筆數: {count}")
        
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            print("  範例資料:")
            for i, row in enumerate(rows, 1):
                print(f"    {i}: {row}")
    
    conn.close()

if __name__ == "__main__":
    main()
