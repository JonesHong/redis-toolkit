#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 專案重組腳本
自動化移動檔案並保留 Git 歷史
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional, List

# 檔案映射表
FILE_MAPPINGS = {
    # 單元測試
    'tests/test_core.py': 'tests/unit/test_core.py',
    'tests/test_serializers.py': 'tests/unit/test_serializers.py',
    'tests/test_conveters.py': 'tests/unit/test_converters.py',  # 修正拼寫
    'tests/test_validation.py': 'tests/unit/test_validation.py',
    'tests/test_retry.py': 'tests/unit/test_retry.py',
    'tests/test_pool_manager.py': 'tests/unit/test_pool_manager.py',
    'tests/test_converter_errors.py': 'tests/unit/test_converter_errors.py',
    
    # 整合測試
    'tests/test_initialization.py': 'tests/integration/test_initialization.py',
    'tests/test_conveters_intergration.py': 'tests/integration/test_converters_integration.py',  # 修正拼寫
    'tests/test_pubsub_thread.py': 'tests/integration/test_pubsub_thread.py',
    
    # 範例程式
    'examples/basic_usage.py': 'examples/quickstart/01_hello_redis.py',
    'examples/batch_operations.py': 'examples/features/batch_operations.py',
    'examples/pubsub_example.py': 'examples/features/pubsub_messaging.py',
    'examples/image_transfer.py': 'examples/real-world/media_processing/image_example.py',
    'examples/audio_streaming.py': 'examples/real-world/media_processing/audio_example.py',
    'examples/video_caching.py': 'examples/real-world/media_processing/video_example.py',
    'examples/media_example.py': 'examples/real-world/media_processing/complete_example.py',
    'examples/performance_test.py': 'examples/features/performance_demo.py',
}

# 要刪除的重複檔案
FILES_TO_DELETE = [
    'examples/quick_start.py',  # 與 basic_usage.py 重複
]

# 目錄映射
DIR_MAPPINGS = {
    'benchmarks': 'tests/performance',
    'examples/data': 'examples/real-world/media_processing/data',
}


def run_git_command(cmd: List[str]) -> bool:
    """執行 Git 命令並返回是否成功"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Git 命令失敗: {' '.join(cmd)}")
            print(f"錯誤: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"執行命令時發生錯誤: {e}")
        return False


def git_mv(src: str, dst: str) -> bool:
    """使用 git mv 移動檔案，保留歷史"""
    # 確保目標目錄存在
    dst_dir = os.path.dirname(dst)
    if dst_dir:
        os.makedirs(dst_dir, exist_ok=True)
    
    # 執行 git mv
    return run_git_command(['git', 'mv', src, dst])


def move_files():
    """移動所有檔案"""
    print("開始移動檔案...")
    success_count = 0
    fail_count = 0
    
    # 移動單個檔案
    for src, dst in FILE_MAPPINGS.items():
        if os.path.exists(src):
            print(f"移動: {src} -> {dst}")
            if git_mv(src, dst):
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"跳過不存在的檔案: {src}")
    
    # 移動目錄
    for src_dir, dst_dir in DIR_MAPPINGS.items():
        if os.path.exists(src_dir):
            print(f"移動目錄: {src_dir} -> {dst_dir}")
            # 先創建目標目錄
            os.makedirs(dst_dir, exist_ok=True)
            # 移動目錄內的所有檔案
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    src_file = os.path.join(root, file)
                    # 計算相對路徑
                    rel_path = os.path.relpath(src_file, src_dir)
                    dst_file = os.path.join(dst_dir, rel_path)
                    
                    print(f"  移動: {src_file} -> {dst_file}")
                    if git_mv(src_file, dst_file):
                        success_count += 1
                    else:
                        fail_count += 1
    
    # 刪除重複檔案
    for file_to_delete in FILES_TO_DELETE:
        if os.path.exists(file_to_delete):
            print(f"刪除重複檔案: {file_to_delete}")
            if run_git_command(['git', 'rm', file_to_delete]):
                success_count += 1
            else:
                fail_count += 1
    
    print(f"\n完成！成功: {success_count}, 失敗: {fail_count}")
    return fail_count == 0


def create_init_files():
    """為 Python 套件創建 __init__.py 檔案"""
    init_dirs = [
        'tests/unit',
        'tests/integration',
        'tests/performance',
    ]
    
    for dir_path in init_dirs:
        init_file = os.path.join(dir_path, '__init__.py')
        if not os.path.exists(init_file):
            Path(init_file).touch()
            run_git_command(['git', 'add', init_file])
            print(f"創建: {init_file}")


def update_imports():
    """更新檔案中的導入路徑"""
    # 這裡可以使用 sed 或 Python 來批量更新導入
    print("\n請手動檢查並更新以下檔案中的導入路徑：")
    print("- tests/conftest.py")
    print("- tests/run_tests.py")
    print("- 任何引用了移動檔案的程式碼")


def main():
    """主函數"""
    # 檢查是否在 Git 倉庫中
    if not os.path.exists('.git'):
        print("錯誤：請在 Git 倉庫根目錄執行此腳本")
        sys.exit(1)
    
    # 檢查是否有未提交的更改
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if result.stdout.strip():
        print("警告：有未提交的更改。")
        print("將在執行重組前暫存當前更改...")
        run_git_command(['git', 'add', '-A'])
        run_git_command(['git', 'commit', '-m', 'WIP: 重組前的暫存提交'])
    
    # 執行移動操作
    if move_files():
        create_init_files()
        update_imports()
        
        print("\n建議的下一步操作：")
        print("1. 檢查並更新所有導入路徑")
        print("2. 運行測試確保一切正常: pytest tests/")
        print("3. 提交更改: git commit -m 'refactor: 重組專案結構'")
    else:
        print("\n移動過程中發生錯誤，請檢查並手動修復")


if __name__ == "__main__":
    main()