#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent 測試檔案自動管理工具
用於整理和管理 .ai-playground 目錄中的檔案
"""

import argparse
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import re


class AIFileManager:
    """AI 檔案管理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.playground_dir = self.project_root / ".ai-playground"
    
    def organize_files(self):
        """整理散落的測試檔案"""
        print("🔄 開始整理 AI 實驗檔案...")
        
        # 定義檔案模式和目標目錄
        patterns = {
            r"test_.*\.py$": "validations",
            r"experiment.*\.py$": "experiments",
            r"prototype.*\.py$": "prototypes", 
            r"debug.*\.py$": "experiments",
            r"temp.*\.py$": "experiments",
            r"validation.*\.py$": "validations"
        }
        
        moved_count = 0
        # 掃描專案根目錄和 src 目錄
        for search_dir in [self.project_root, self.project_root / "src"]:
            for file_path in search_dir.glob("*.py"):
                if self._should_move_file(file_path):
                    target_dir = self._get_target_directory(file_path, patterns)
                    if target_dir and self._move_file_safely(file_path, target_dir):
                        moved_count += 1
        
        print(f"✅ 整理完成，移動了 {moved_count} 個檔案")
    
    def clean_old_files(self, days: int = 7):
        """清理舊的測試檔案"""
        print(f"🧹 清理 {days} 天前的檔案...")
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        for file_path in self.playground_dir.rglob("*.py"):
            if file_path.parent.name == "archived":
                continue
                
            if file_path.stat().st_mtime < cutoff_date.timestamp():
                print(f"發現舊檔案: {file_path.relative_to(self.project_root)}")
                response = input(f"移動到 archived/ ? (y/N): ").strip().lower()
                if response == 'y':
                    archive_path = self.playground_dir / "archived" / file_path.name
                    # 避免檔名衝突
                    if archive_path.exists():
                        timestamp = datetime.now().strftime("%H%M%S")
                        archive_path = archive_path.with_stem(f"{archive_path.stem}_{timestamp}")
                    
                    shutil.move(str(file_path), str(archive_path))
                    print(f"   ✅ 已歸檔: {archive_path.relative_to(self.project_root)}")
                    cleaned_count += 1
        
        print(f"✅ 清理完成，歸檔了 {cleaned_count} 個檔案")
    
    def generate_report(self):
        """產生 AI 活動報告"""
        print("📊 產生 AI Agent 活動報告...")
        
        stats = {}
        total_files = 0
        
        for subdir in ["experiments", "validations", "prototypes", "archived"]:
            dir_path = self.playground_dir / subdir
            if dir_path.exists():
                py_files = list(dir_path.glob("*.py"))
                stats[subdir] = len(py_files)
                total_files += len(py_files)
            else:
                stats[subdir] = 0
        
        print(f"""
AI Agent 檔案統計報告
{'='*40}
📁 實驗檔案 (experiments): {stats['experiments']} 個
🔍 驗證檔案 (validations): {stats['validations']} 個  
🏗️  原型檔案 (prototypes):  {stats['prototypes']} 個
📦 歸檔檔案 (archived):    {stats['archived']} 個
{'='*40}
📈 總計: {total_files} 個 AI 產生的檔案
        """)
        
        # 分析最近活動
        recent_files = []
        week_ago = datetime.now() - timedelta(days=7)
        
        for file_path in self.playground_dir.rglob("*.py"):
            if file_path.stat().st_mtime > week_ago.timestamp():
                recent_files.append(file_path)
        
        if recent_files:
            print(f"📅 最近 7 天新增了 {len(recent_files)} 個檔案:")
            for file_path in sorted(recent_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                print(f"   • {file_path.relative_to(self.playground_dir)} ({mod_time.strftime('%m-%d %H:%M')})")
    
    def _should_move_file(self, file_path: Path) -> bool:
        """判斷檔案是否應該移動"""
        # 不移動主要程式檔案
        if file_path.name in ["main.py", "__init__.py", "setup.py"]:
            return False
        
        # 不移動已經在正確位置的檔案
        if ".ai-playground" in str(file_path):
            return False
            
        return True
    
    def _get_target_directory(self, file_path: Path, patterns: dict) -> str:
        """根據檔案名稱決定目標目錄"""
        filename = file_path.name
        
        for pattern, target_dir in patterns.items():
            if re.search(pattern, filename):
                return target_dir
        
        # 預設放到 experiments
        return "experiments"
    
    def _move_file_safely(self, file_path: Path, target_dir: str) -> bool:
        """安全地移動檔案"""
        target_path = self.playground_dir / target_dir / file_path.name
        
        # 檢查目標檔案是否已存在
        if target_path.exists():
            timestamp = datetime.now().strftime("%H%M%S")
            target_path = target_path.with_stem(f"{target_path.stem}_{timestamp}")
        
        try:
            shutil.move(str(file_path), str(target_path))
            print(f"   📁 {file_path.name} → {target_dir}/")
            return True
        except Exception as e:
            print(f"   ❌ 移動失敗 {file_path.name}: {e}")
            return False


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description="AI Agent 檔案管理工具")
    parser.add_argument("--organize", action="store_true", help="整理散落的檔案")
    parser.add_argument("--clean", action="store_true", help="清理舊檔案")
    parser.add_argument("--days", type=int, default=7, help="清理幾天前的檔案 (預設: 7)")
    parser.add_argument("--report", action="store_true", help="產生活動報告")
    parser.add_argument("--all", action="store_true", help="執行所有操作")
    
    args = parser.parse_args()
    
    if not any([args.organize, args.clean, args.report, args.all]):
        parser.print_help()
        return
    
    manager = AIFileManager()
    
    if args.all or args.organize:
        manager.organize_files()
    
    if args.all or args.clean:
        manager.clean_old_files(args.days)
    
    if args.all or args.report:
        manager.generate_report()
    
    print("\n🎉 AI 檔案管理完成！")


if __name__ == "__main__":
    main()
