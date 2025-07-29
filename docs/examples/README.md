# 範例程式碼

歡迎來到範例程式碼區！這裡收集了各種實用的 Redis Toolkit 使用範例，從基礎到進階，幫助您快速上手。

## 📂 範例分類

<div class="example-grid">
  <div class="example-card">
    <h3>🎯 基礎範例</h3>
    <p>適合初學者的簡單範例</p>
    <ul>
      <li>Hello World</li>
      <li>基本存取操作</li>
      <li>資料類型處理</li>
      <li>簡單的發布訂閱</li>
    </ul>
    <a href="./basic/" class="example-link">查看範例 →</a>
  </div>
  
  <div class="example-card">
    <h3>🎨 媒體處理範例</h3>
    <p>圖片、音頻、視頻處理實例</p>
    <ul>
      <li>圖片快取系統</li>
      <li>音頻轉換服務</li>
      <li>視頻縮圖生成</li>
      <li>媒體檔案管理</li>
    </ul>
    <a href="./media/" class="example-link">查看範例 →</a>
  </div>
  
  <div class="example-card">
    <h3>💼 實戰案例</h3>
    <p>真實應用場景的完整實現</p>
    <ul>
      <li>用戶系統</li>
      <li>即時聊天室</li>
      <li>任務隊列</li>
      <li>快取系統</li>
    </ul>
    <a href="./real-world/" class="example-link">查看範例 →</a>
  </div>
</div>

## 🚀 快速開始範例

### Hello Redis Toolkit

```python
from redis_toolkit import RedisToolkit

# 初始化
toolkit = RedisToolkit()

# 存儲資料
toolkit.setter("greeting", "Hello, Redis Toolkit!")

# 讀取資料
message = toolkit.getter("greeting")
print(message)  # Hello, Redis Toolkit!

# 存儲複雜資料
user = {
    "id": 1,
    "name": "Alice",
    "scores": [95, 87, 92]
}
toolkit.setter("user:1", user)

# 自動反序列化
retrieved_user = toolkit.getter("user:1")
print(f"{retrieved_user['name']} 的分數: {retrieved_user['scores']}")
```

## 📱 實用小範例

### 計數器

```python
class Counter:
    def __init__(self, name):
        self.toolkit = RedisToolkit()
        self.key = f"counter:{name}"
    
    def increment(self):
        current = self.toolkit.getter(self.key) or 0
        self.toolkit.setter(self.key, current + 1)
        return current + 1
    
    def get(self):
        return self.toolkit.getter(self.key) or 0
    
    def reset(self):
        self.toolkit.setter(self.key, 0)

# 使用範例
page_views = Counter("page_views")
page_views.increment()
print(f"瀏覽次數: {page_views.get()}")
```

### 簡單快取

```python
import time

def cached(key, ttl=300):
    """快取裝飾器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            toolkit = RedisToolkit()
            
            # 嘗試從快取獲取
            cached_result = toolkit.getter(key)
            if cached_result is not None:
                return cached_result
            
            # 執行函數並快取結果
            result = func(*args, **kwargs)
            toolkit.setter(key, result, ex=ttl)
            return result
        
        return wrapper
    return decorator

# 使用範例
@cached("expensive_calculation", ttl=600)
def calculate_something():
    print("執行昂貴的計算...")
    time.sleep(2)  # 模擬耗時操作
    return {"result": 42}

# 第一次呼叫會執行計算
result1 = calculate_something()

# 後續呼叫直接返回快取
result2 = calculate_something()
```

### 排行榜

```python
class Leaderboard:
    def __init__(self, name):
        self.toolkit = RedisToolkit()
        self.key = f"leaderboard:{name}"
    
    def add_score(self, player, score):
        """添加或更新玩家分數"""
        self.toolkit.client.zadd(self.key, {player: score})
    
    def get_top(self, count=10):
        """獲取前 N 名"""
        top_players = self.toolkit.client.zrevrange(
            self.key, 0, count-1, withscores=True
        )
        return [(p.decode(), int(s)) for p, s in top_players]
    
    def get_rank(self, player):
        """獲取玩家排名"""
        rank = self.toolkit.client.zrevrank(self.key, player)
        return rank + 1 if rank is not None else None

# 使用範例
game_scores = Leaderboard("game_2024")

# 添加分數
game_scores.add_score("Alice", 1500)
game_scores.add_score("Bob", 1200)
game_scores.add_score("Charlie", 1800)

# 獲取排行榜
top_3 = game_scores.get_top(3)
for i, (player, score) in enumerate(top_3, 1):
    print(f"{i}. {player}: {score} 分")
```

## 🎯 學習路徑建議

### 初學者路線

1. **基礎操作** → 從 Hello World 開始
2. **資料類型** → 了解序列化功能
3. **簡單應用** → 實作計數器、快取
4. **發布訂閱** → 嘗試訊息傳遞

### 進階路線

1. **批次操作** → 提升效能
2. **媒體處理** → 處理圖片音頻
3. **錯誤處理** → 建立穩定系統
4. **實戰專案** → 完整應用開發

## 💡 範例使用技巧

### 1. 複製並修改

所有範例都可以直接複製使用，根據需求修改：

```python
# 複製範例程式碼
# 修改配置參數
# 調整業務邏輯
# 添加錯誤處理
```

### 2. 組合使用

不同範例可以組合使用：

```python
# 結合快取 + 計數器
class CachedCounter(Counter):
    def increment(self):
        result = super().increment()
        # 清除相關快取
        self.toolkit.client.delete("stats:cache")
        return result
```

### 3. 性能測試

在範例基礎上進行性能測試：

```python
import time

def benchmark(func, iterations=1000):
    start = time.time()
    for _ in range(iterations):
        func()
    elapsed = time.time() - start
    print(f"執行 {iterations} 次耗時: {elapsed:.3f} 秒")
    print(f"平均每次: {elapsed/iterations*1000:.2f} 毫秒")

# 測試範例
benchmark(lambda: toolkit.setter("test", "value"))
```

## 📚 完整範例專案

### 迷你部落格系統

結合多個功能的完整範例：

```python
class MiniBlog:
    def __init__(self):
        self.toolkit = RedisToolkit()
    
    def create_post(self, author, title, content):
        """創建文章"""
        post_id = self.toolkit.client.incr("post:id")
        post = {
            "id": post_id,
            "author": author,
            "title": title,
            "content": content,
            "created_at": time.time(),
            "views": 0
        }
        
        # 儲存文章
        self.toolkit.setter(f"post:{post_id}", post)
        
        # 添加到文章列表
        self.toolkit.client.lpush("posts:recent", post_id)
        
        # 更新作者的文章列表
        self.toolkit.client.sadd(f"author:{author}:posts", post_id)
        
        return post_id
    
    def get_post(self, post_id):
        """獲取文章並增加瀏覽次數"""
        key = f"post:{post_id}"
        post = self.toolkit.getter(key)
        
        if post:
            # 增加瀏覽次數
            post["views"] += 1
            self.toolkit.setter(key, post)
        
        return post
    
    def get_recent_posts(self, count=10):
        """獲取最近的文章"""
        post_ids = self.toolkit.client.lrange("posts:recent", 0, count-1)
        posts = []
        
        for pid in post_ids:
            post = self.toolkit.getter(f"post:{int(pid)}")
            if post:
                posts.append(post)
        
        return posts

# 使用範例
blog = MiniBlog()

# 創建文章
post_id = blog.create_post(
    author="Alice",
    title="Redis Toolkit 使用心得",
    content="這是一個很棒的工具..."
)

# 讀取文章
post = blog.get_post(post_id)
print(f"《{post['title']}》已被瀏覽 {post['views']} 次")
```

## 🔗 相關資源

- [GitHub 範例倉庫](https://github.com/JonesHong/redis-toolkit/tree/main/examples)
- [API 文檔](/api/) - 詳細的 API 說明
- [最佳實踐](/guide/best-practices.html) - 開發建議

## 🎯 下一步

選擇您感興趣的範例類別開始探索：

<div class="next-steps">
  <a href="./basic/" class="step-card">
    <span class="number">1</span>
    <span class="title">基礎範例</span>
  </a>
  <a href="./media/" class="step-card">
    <span class="number">2</span>
    <span class="title">媒體處理</span>
  </a>
  <a href="./real-world/" class="step-card">
    <span class="number">3</span>
    <span class="title">實戰案例</span>
  </a>
</div>

::: tip 提示
- 所有範例都經過測試，可以直接運行
- 建議先閱讀程式碼，理解邏輯後再運行
- 遇到問題可以查看[疑難排解](/reference/troubleshooting.html)
:::

<style>
.example-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.example-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s;
}

.example-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
  border-color: #dc382d;
}

.example-card h3 {
  color: #dc382d;
  margin-top: 0;
  margin-bottom: 0.8rem;
}

.example-card p {
  color: #666;
  margin-bottom: 1rem;
}

.example-card ul {
  margin: 0 0 1rem 0;
  padding-left: 1.2rem;
  color: #555;
  font-size: 0.9rem;
}

.example-link {
  display: inline-block;
  color: #dc382d;
  text-decoration: none;
  font-weight: 500;
  transition: transform 0.2s;
}

.example-link:hover {
  transform: translateX(3px);
}

.next-steps {
  display: flex;
  gap: 1rem;
  margin: 2rem 0;
  justify-content: center;
  flex-wrap: wrap;
}

.step-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 2rem;
  background: #dc382d;
  color: white;
  text-decoration: none;
  border-radius: 50px;
  transition: all 0.2s;
}

.step-card:hover {
  background: #e85d52;
  transform: translateY(-2px);
}

.step-card .number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: white;
  color: #dc382d;
  border-radius: 50%;
  font-weight: bold;
}

.step-card .title {
  font-weight: 500;
}
</style>