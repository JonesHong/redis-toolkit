# 第一個 Redis 應用

本教程將指導您建立一個簡單的任務管理應用，展示 Redis Toolkit 的核心功能。

## 學習目標

完成本教程後，您將學會：

- 使用 Redis Toolkit 進行基本的 CRUD 操作
- 實現批次操作以提升性能
- 使用發布/訂閱功能進行實時通信
- 處理錯誤和異常情況

## 建立任務管理應用

### 步驟 1：項目設置

首先，創建一個新的 Python 文件 `task_manager.py`：

```python
from redis_toolkit import RedisToolkit, RedisOptions
import uuid
import time
from datetime import datetime

class TaskManager:
    def __init__(self):
        # 配置選項
        options = RedisOptions(
            is_logger_info=True,
            enable_validation=True
        )
        self.toolkit = RedisToolkit(options=options)
        
    def create_task(self, title, description):
        """創建新任務"""
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 存儲任務
        self.toolkit.setter(f"task:{task_id}", task)
        
        # 發布任務創建事件
        self.toolkit.publisher("task_events", {
            "event": "task_created",
            "task_id": task_id,
            "timestamp": time.time()
        })
        
        return task_id
```

### 步驟 2：實現 CRUD 操作

```python
    def get_task(self, task_id):
        """獲取任務詳情"""
        return self.toolkit.getter(f"task:{task_id}")
    
    def update_task(self, task_id, updates):
        """更新任務"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # 更新字段
        task.update(updates)
        task["updated_at"] = datetime.now().isoformat()
        
        # 保存更新
        self.toolkit.setter(f"task:{task_id}", task)
        
        # 發布更新事件
        self.toolkit.publisher("task_events", {
            "event": "task_updated",
            "task_id": task_id,
            "updates": updates,
            "timestamp": time.time()
        })
        
        return task
    
    def delete_task(self, task_id):
        """刪除任務"""
        if not self.get_task(task_id):
            raise ValueError(f"Task {task_id} not found")
        
        self.toolkit.deleter(f"task:{task_id}")
        
        # 發布刪除事件
        self.toolkit.publisher("task_events", {
            "event": "task_deleted",
            "task_id": task_id,
            "timestamp": time.time()
        })
```

### 步驟 3：批次操作

```python
    def get_all_tasks(self):
        """獲取所有任務"""
        # 獲取所有任務鍵
        pattern = "task:*"
        keys = []
        
        # 使用 scan_iter 避免阻塞
        for key in self.toolkit.client.scan_iter(match=pattern):
            keys.append(key.decode())
        
        if not keys:
            return []
        
        # 批次獲取所有任務
        tasks = self.toolkit.batch_get(keys)
        return [task for task in tasks.values() if task]
    
    def create_multiple_tasks(self, tasks_data):
        """批次創建任務"""
        tasks_to_create = {}
        task_ids = []
        
        for task_data in tasks_data:
            task_id = str(uuid.uuid4())
            task = {
                "id": task_id,
                "title": task_data["title"],
                "description": task_data["description"],
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            tasks_to_create[f"task:{task_id}"] = task
            task_ids.append(task_id)
        
        # 批次存儲
        self.toolkit.batch_set(tasks_to_create)
        
        # 發布批次創建事件
        self.toolkit.publisher("task_events", {
            "event": "tasks_batch_created",
            "task_ids": task_ids,
            "count": len(task_ids),
            "timestamp": time.time()
        })
        
        return task_ids
```

### 步驟 4：事件監聽器

創建 `task_listener.py`：

```python
from redis_toolkit import RedisToolkit
import time

def handle_task_event(channel, data):
    """處理任務事件"""
    event = data.get("event")
    task_id = data.get("task_id")
    timestamp = data.get("timestamp")
    
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 事件: {event}")
    
    if event == "task_created":
        print(f"  新任務創建: {task_id}")
    elif event == "task_updated":
        updates = data.get("updates", {})
        print(f"  任務更新: {task_id}")
        print(f"  更新內容: {updates}")
    elif event == "task_deleted":
        print(f"  任務刪除: {task_id}")
    elif event == "tasks_batch_created":
        count = data.get("count", 0)
        print(f"  批次創建 {count} 個任務")

if __name__ == "__main__":
    # 創建訂閱者
    subscriber = RedisToolkit(
        channels=["task_events"],
        message_handler=handle_task_event
    )
    
    print("任務事件監聽器已啟動...")
    print("按 Ctrl+C 停止")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在關閉...")
        subscriber.cleanup()
```

### 步驟 5：使用應用

創建 `main.py` 來使用任務管理器：

```python
from task_manager import TaskManager

def main():
    # 創建任務管理器
    manager = TaskManager()
    
    # 創建單個任務
    print("創建單個任務...")
    task_id = manager.create_task(
        title="學習 Redis Toolkit",
        description="完成第一個應用教程"
    )
    print(f"任務已創建: {task_id}")
    
    # 獲取任務
    task = manager.get_task(task_id)
    print(f"\n任務詳情: {task}")
    
    # 更新任務狀態
    print("\n更新任務狀態...")
    updated_task = manager.update_task(task_id, {"status": "in_progress"})
    print(f"更新後: {updated_task}")
    
    # 批次創建任務
    print("\n批次創建任務...")
    batch_tasks = [
        {"title": "任務 1", "description": "描述 1"},
        {"title": "任務 2", "description": "描述 2"},
        {"title": "任務 3", "description": "描述 3"}
    ]
    task_ids = manager.create_multiple_tasks(batch_tasks)
    print(f"創建了 {len(task_ids)} 個任務")
    
    # 獲取所有任務
    print("\n所有任務:")
    all_tasks = manager.get_all_tasks()
    for task in all_tasks:
        print(f"  - {task['title']} ({task['status']})")
    
    # 刪除任務
    print(f"\n刪除任務 {task_id}...")
    manager.delete_task(task_id)
    print("任務已刪除")

if __name__ == "__main__":
    main()
```

## 運行應用

1. 首先，在一個終端窗口運行事件監聽器：

```bash
python task_listener.py
```

2. 在另一個終端窗口運行主應用：

```bash
python main.py
```

您將看到主應用創建和管理任務，同時事件監聽器實時顯示所有操作。

## 錯誤處理

改進任務管理器的錯誤處理：

```python
from redis_toolkit.exceptions import (
    ValidationError,
    SerializationError,
    RedisToolkitError
)

def safe_create_task(self, title, description):
    """安全創建任務，包含錯誤處理"""
    try:
        # 驗證輸入
        if not title or len(title) > 200:
            raise ValueError("標題必須介於 1-200 個字符")
        
        return self.create_task(title, description)
        
    except ValidationError as e:
        print(f"驗證錯誤: {e}")
        return None
        
    except SerializationError as e:
        print(f"序列化錯誤: {e}")
        return None
        
    except RedisToolkitError as e:
        print(f"Redis 錯誤: {e}")
        return None
        
    except Exception as e:
        print(f"未預期的錯誤: {e}")
        return None
```

## 最佳實踐

1. **使用上下文管理器**：

```python
with TaskManager() as manager:
    task_id = manager.create_task("任務標題", "任務描述")
    # 自動清理資源
```

2. **處理缺失的鍵**：

```python
task = manager.get_task("non-existent-id")
if task is None:
    print("任務不存在")
```

3. **批次操作優化**：

```python
# 不要這樣做
for task_id in task_ids:
    task = manager.get_task(task_id)
    
# 應該這樣做
tasks = manager.toolkit.batch_get([f"task:{id}" for id in task_ids])
```

## 總結

恭喜！您已經建立了第一個使用 Redis Toolkit 的應用。您學會了：

- ✅ 基本的 CRUD 操作
- ✅ 批次操作以提升性能
- ✅ 發布/訂閱模式的實時通信
- ✅ 錯誤處理和最佳實踐

## 下一步

- 探索[媒體處理功能](/how-to/media-processing)
- 學習[性能調優技巧](/how-to/performance-tuning)
- 查看完整的 [API 參考](/reference/api/core)