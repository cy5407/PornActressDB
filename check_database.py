#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫狀態檢查腳本
快速檢查女優分類系統的資料庫連接狀態
"""
import os
import sys
from pathlib import Path

# 加入專案路徑
sys.path.append(str(Path(__file__).parent))

from src.models.config import ConfigManager
from src.models.database import SQLiteDBManager


def check_database_status():
    """檢查資料庫狀態"""
    print("🔍 女優分類系統 - 資料庫狀態檢查")
    print("=" * 50)
    
    try:
        # 檢查設定
        config = ConfigManager()
        db_path = config.get('database', 'database_path')
        
        print(f"📍 設定的資料庫路徑:")
        print(f"   {db_path}")
        
        # 檢查檔案存在性
        if os.path.exists(db_path):
            print("✅ 資料庫檔案存在")
            
            # 檢查檔案大小
            size = os.path.getsize(db_path)
            print(f"📊 檔案大小: {size:,} bytes ({size/1024:.1f} KB)")
            
            # 檢查最後修改時間
            mtime = os.path.getmtime(db_path)
            import datetime
            mod_time = datetime.datetime.fromtimestamp(mtime)
            print(f"🕒 最後修改: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            print("❌ 資料庫檔案不存在")
            
            # 檢查目錄是否存在
            db_dir = Path(db_path).parent
            if db_dir.exists():
                print(f"📁 資料庫目錄存在: {db_dir}")
            else:
                print(f"❌ 資料庫目錄不存在: {db_dir}")
        
        # 嘗試連接資料庫
        print("\n🔗 嘗試連接資料庫...")
        try:
            db_manager = SQLiteDBManager(db_path)
            
            # 檢查資料表
            cursor = db_manager.get_connection().cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print("✅ 資料庫連接成功")
            print(f"📋 資料表數量: {len(tables)}")
            
            if tables:
                print("📋 資料表清單:")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"   - {table[0]}: {count:,} 筆記錄")
            
            cursor.close()
            
        except Exception as e:
            print(f"❌ 資料庫連接失敗: {e}")
        
        # 檢查備份檔案
        print(f"\n📦 檢查備份檔案...")
        db_dir = Path(db_path).parent
        backup_files = list(db_dir.glob("*.bak"))
        
        if backup_files:
            print(f"✅ 找到 {len(backup_files)} 個備份檔案:")
            for backup in sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                size = backup.stat().st_size
                mtime = datetime.datetime.fromtimestamp(backup.stat().st_mtime)
                print(f"   - {backup.name}: {size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("⚠️ 未找到備份檔案")
        
        # 檢查專案中的測試資料庫
        print(f"\n🧪 檢查專案測試資料庫...")
        test_db_path = Path("data/test_database.db")
        if test_db_path.exists():
            size = test_db_path.stat().st_size
            print(f"✅ 測試資料庫存在: {size:,} bytes ({size/1024:.1f} KB)")
        else:
            print("⚠️ 測試資料庫不存在")
        
    except Exception as e:
        print(f"❌ 檢查過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


def check_git_status():
    """檢查 Git 狀態"""
    print(f"\n📋 Git 狀態檢查...")
    try:
        import subprocess
        
        # 檢查 .gitignore 中的資料庫設定
        gitignore_path = Path(".gitignore")
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '*.db' in content:
                    print("✅ .gitignore 正確設定，資料庫檔案已被忽略")
                else:
                    print("⚠️ .gitignore 未設定忽略資料庫檔案")
        
        # 檢查 git 狀態
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            untracked = [line for line in result.stdout.split('\n') 
                        if line.startswith('??') and '.db' in line]
            
            if untracked:
                print("⚠️ 發現未追蹤的資料庫檔案:")
                for line in untracked:
                    print(f"   {line}")
            else:
                print("✅ 沒有未追蹤的資料庫檔案")
        
    except Exception as e:
        print(f"⚠️ 無法檢查 Git 狀態: {e}")


if __name__ == "__main__":
    check_database_status()
    check_git_status()
    
    print(f"\n" + "=" * 50)
    print("🎯 總結:")
    print("- 主要資料庫位於使用者文件目錄")
    print("- Git 儲存庫不包含使用者資料（這是正確的）")
    print("- 如需備份，請複製整個 ActressClassifier 目錄")
    print("- 程式會自動管理資料庫連接和建立")
