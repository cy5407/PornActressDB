#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VS Code 快捷鍵診斷工具
"""

import json
import os
from pathlib import Path

def check_vscode_extensions():
    """檢查已安裝的 VS Code 擴充功能"""
    print("🔍 檢查 VS Code 擴充功能...")
    
    try:
        # 檢查 Copilot 擴充功能
        result = os.popen("code --list-extensions").read()
        extensions = result.strip().split('\n')
        
        copilot_extensions = [ext for ext in extensions if 'copilot' in ext.lower()]
        claude_extensions = [ext for ext in extensions if 'claude' in ext.lower()]
        
        print(f"✅ GitHub Copilot 擴充功能: {copilot_extensions}")
        print(f"🤖 Claude 相關擴充功能: {claude_extensions}")
        
        return copilot_extensions, claude_extensions
    except Exception as e:
        print(f"❌ 檢查擴充功能時發生錯誤: {e}")
        return [], []

def check_keybindings():
    """檢查快捷鍵設定檔案"""
    print("\n⌨️ 檢查快捷鍵設定...")
    
    keybindings_path = Path(".vscode/keybindings.json")
    
    if keybindings_path.exists():
        try:
            with open(keybindings_path, 'r', encoding='utf-8') as f:
                keybindings = json.load(f)
            
            print(f"✅ 找到快捷鍵設定檔案: {keybindings_path}")
            print(f"📋 設定的快捷鍵數量: {len(keybindings)}")
            
            for binding in keybindings:
                key = binding.get('key', 'unknown')
                command = binding.get('command', 'unknown')
                print(f"  • {key} → {command}")
                
            return True, keybindings
        except Exception as e:
            print(f"❌ 讀取快捷鍵設定時發生錯誤: {e}")
            return False, []
    else:
        print(f"❌ 找不到快捷鍵設定檔案: {keybindings_path}")
        return False, []

def check_vscode_settings():
    """檢查 VS Code 設定檔案"""
    print("\n⚙️ 檢查 VS Code 設定...")
    
    settings_path = Path(".vscode/settings.json")
    
    if settings_path.exists():
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 移除註解 (簡單處理)
                lines = [line for line in content.split('\n') if not line.strip().startswith('//')]
                clean_content = '\n'.join(lines)
                settings = json.loads(clean_content)
            
            print(f"✅ 找到 VS Code 設定檔案: {settings_path}")
            
            # 檢查 Copilot 相關設定
            copilot_settings = {k: v for k, v in settings.items() if 'copilot' in k.lower()}
            if copilot_settings:
                print("📋 GitHub Copilot 設定:")
                for key, value in copilot_settings.items():
                    print(f"  • {key}: {value}")
            else:
                print("⚠️ 沒有找到 GitHub Copilot 相關設定")
                
            return True, settings
        except Exception as e:
            print(f"❌ 讀取 VS Code 設定時發生錯誤: {e}")
            return False, {}
    else:
        print(f"❌ 找不到 VS Code 設定檔案: {settings_path}")
        return False, {}

def generate_test_commands():
    """生成測試命令"""
    print("\n🧪 測試命令建議:")
    
    commands = [
        ("Ctrl+Alt+P", "github.copilot.chat.focus", "開啟 GitHub Copilot 聊天"),
        ("Ctrl+Shift+Space", "editor.action.inlineSuggest.trigger", "觸發程式碼建議"),
        ("Ctrl+Alt+C", "workbench.action.chat.open", "開啟聊天面板"),
        ("Ctrl+I", "github.copilot.interactiveEditor.explain", "解釋程式碼"),
    ]
    
    print("請在 VS Code 中嘗試以下操作:")
    for i, (key, command, description) in enumerate(commands, 1):
        print(f"{i}. 按 {key} → {description}")
        print(f"   命令: {command}")
        print()

def main():
    """主診斷函式"""
    print("🔧 VS Code 快捷鍵診斷工具")
    print("=" * 50)
    
    # 檢查擴充功能
    copilot_exts, claude_exts = check_vscode_extensions()
    
    # 檢查快捷鍵設定
    has_keybindings, keybindings = check_keybindings()
    
    # 檢查 VS Code 設定
    has_settings, settings = check_vscode_settings()
    
    # 生成測試建議
    generate_test_commands()
    
    # 診斷結果總結
    print("\n📋 診斷結果總結:")
    print(f"✅ GitHub Copilot 已安裝: {'是' if copilot_exts else '否'}")
    print(f"✅ 快捷鍵設定存在: {'是' if has_keybindings else '否'}")
    print(f"✅ VS Code 設定存在: {'是' if has_settings else '否'}")
    
    if not copilot_exts:
        print("\n⚠️ 建議: 請先安裝 GitHub Copilot 擴充功能")
        print("   在 VS Code 中按 Ctrl+Shift+X 搜尋 'GitHub Copilot'")
    
    if not has_keybindings:
        print("\n⚠️ 建議: 快捷鍵設定檔案可能有問題")
        print("   請檢查 .vscode/keybindings.json 檔案")
    
    print("\n🚀 接下來請:")
    print("1. 重新啟動 VS Code")
    print("2. 開啟 test_shortcuts.py 檔案")
    print("3. 逐一測試上述快捷鍵")

if __name__ == "__main__":
    main()
