# Example Code

Welcome to the example code section! Here we've collected various practical Redis Toolkit usage examples, from basic to advanced, to help you get started quickly.

## 📂 Example Categories

<div class="example-grid">
  <div class="example-card">
    <h3>🎯 Basic Examples</h3>
    <p>Simple examples suitable for beginners</p>
    <ul>
      <li>Hello World</li>
      <li>Basic operations</li>
      <li>Data type handling</li>
      <li>Simple publish/subscribe</li>
    </ul>
    <a href="./basic/" class="example-link">View Examples →</a>
  </div>
  
  <div class="example-card">
    <h3>🎨 Media Processing Examples</h3>
    <p>Image, audio, and video processing examples</p>
    <ul>
      <li>Image caching system</li>
      <li>Audio conversion service</li>
      <li>Video thumbnail generation</li>
      <li>Media file management</li>
    </ul>
    <a href="./media/" class="example-link">View Examples →</a>
  </div>
  
  <div class="example-card">
    <h3>💼 Real-World Cases</h3>
    <p>Complete implementations of real application scenarios</p>
    <ul>
      <li>User system</li>
      <li>Real-time chat room</li>
      <li>Task queue</li>
      <li>Caching system</li>
    </ul>
    <a href="./real-world/" class="example-link">View Examples →</a>
  </div>
</div>

## 🚀 Quick Start Examples

### Hello Redis Toolkit

```python
from redis_toolkit import RedisToolkit

# Initialize
toolkit = RedisToolkit()

# Store data
toolkit.setter("greeting", "Hello, Redis Toolkit!")

# Retrieve data
message = toolkit.getter("greeting")
print(message)  # Hello, Redis Toolkit!

# Store complex data
user = {
    "id": 1,
    "name": "Alice",
    "scores": [95, 87, 92]
}
toolkit.setter("user:1", user)

# Automatic deserialization
retrieved_user = toolkit.getter("user:1")
print(f"{retrieved_user['name']}'s scores: {retrieved_user['scores']}")
```

## 📱 Useful Small Examples

### Counter

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

# Usage example
page_views = Counter("page_views")
page_views.increment()
print(f"Page views: {page_views.get()}")
```

### Simple Cache

```python
import time

def cached(key, ttl=300):
    """Cache decorator"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            toolkit = RedisToolkit()
            
            # Try to get from cache
            cached_result = toolkit.getter(key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            toolkit.setter(key, result, ex=ttl)
            return result
        
        return wrapper
    return decorator

# Usage example
@cached("expensive_calculation", ttl=600)
def calculate_something():
    print("Performing expensive calculation...")
    time.sleep(2)  # Simulate time-consuming operation
    return {"result": 42}

# First call executes the calculation
result1 = calculate_something()

# Subsequent calls return cached result
result2 = calculate_something()
```

### Leaderboard

```python
class Leaderboard:
    def __init__(self, name):
        self.toolkit = RedisToolkit()
        self.key = f"leaderboard:{name}"
    
    def add_score(self, player, score):
        """Add or update player score"""
        self.toolkit.client.zadd(self.key, {player: score})
    
    def get_top(self, count=10):
        """Get top N players"""
        top_players = self.toolkit.client.zrevrange(
            self.key, 0, count-1, withscores=True
        )
        return [(p.decode(), int(s)) for p, s in top_players]
    
    def get_rank(self, player):
        """Get player rank"""
        rank = self.toolkit.client.zrevrank(self.key, player)
        return rank + 1 if rank is not None else None

# Usage example
game_scores = Leaderboard("game_2024")

# Add scores
game_scores.add_score("Alice", 1500)
game_scores.add_score("Bob", 1200)
game_scores.add_score("Charlie", 1800)

# Get leaderboard
top_3 = game_scores.get_top(3)
for i, (player, score) in enumerate(top_3, 1):
    print(f"{i}. {player}: {score} points")
```

## 🎯 Suggested Learning Path

### Beginner Route

1. **Basic Operations** → Start with Hello World
2. **Data Types** → Understand serialization features
3. **Simple Applications** → Implement counters, caches
4. **Publish/Subscribe** → Try message passing

### Advanced Route

1. **Batch Operations** → Improve performance
2. **Media Processing** → Handle images and audio
3. **Error Handling** → Build stable systems
4. **Real Projects** → Complete application development

## 💡 Example Usage Tips

### 1. Copy and Modify

All examples can be directly copied and modified according to your needs:

```python
# Copy example code
# Modify configuration parameters
# Adjust business logic
# Add error handling
```

### 2. Combine Usage

Different examples can be combined:

```python
# Combine cache + counter
class CachedCounter(Counter):
    def increment(self):
        result = super().increment()
        # Clear related cache
        self.toolkit.client.delete("stats:cache")
        return result
```

### 3. Performance Testing

Conduct performance tests based on examples:

```python
import time

def benchmark(func, iterations=1000):
    start = time.time()
    for _ in range(iterations):
        func()
    elapsed = time.time() - start
    print(f"Executed {iterations} times in: {elapsed:.3f} seconds")
    print(f"Average per execution: {elapsed/iterations*1000:.2f} ms")

# Test example
benchmark(lambda: toolkit.setter("test", "value"))
```

## 📚 Complete Example Projects

### Mini Blog System

A complete example combining multiple features:

```python
class MiniBlog:
    def __init__(self):
        self.toolkit = RedisToolkit()
    
    def create_post(self, author, title, content):
        """Create a post"""
        post_id = self.toolkit.client.incr("post:id")
        post = {
            "id": post_id,
            "author": author,
            "title": title,
            "content": content,
            "created_at": time.time(),
            "views": 0
        }
        
        # Save post
        self.toolkit.setter(f"post:{post_id}", post)
        
        # Add to recent posts list
        self.toolkit.client.lpush("posts:recent", post_id)
        
        # Update author's post list
        self.toolkit.client.sadd(f"author:{author}:posts", post_id)
        
        return post_id
    
    def get_post(self, post_id):
        """Get post and increment view count"""
        key = f"post:{post_id}"
        post = self.toolkit.getter(key)
        
        if post:
            # Increment view count
            post["views"] += 1
            self.toolkit.setter(key, post)
        
        return post
    
    def get_recent_posts(self, count=10):
        """Get recent posts"""
        post_ids = self.toolkit.client.lrange("posts:recent", 0, count-1)
        posts = []
        
        for pid in post_ids:
            post = self.toolkit.getter(f"post:{int(pid)}")
            if post:
                posts.append(post)
        
        return posts

# Usage example
blog = MiniBlog()

# Create post
post_id = blog.create_post(
    author="Alice",
    title="My Experience with Redis Toolkit",
    content="This is an amazing tool..."
)

# Read post
post = blog.get_post(post_id)
print(f"'{post['title']}' has been viewed {post['views']} times")
```

## 🔗 Related Resources

- [GitHub Examples Repository](https://github.com/JonesHong/redis-toolkit/tree/main/examples)
- [API Documentation](/en/api/) - Detailed API reference
- [Best Practices](/en/guide/best-practices.html) - Development recommendations

## 🎯 Next Steps

Choose the example category you're interested in to start exploring:

<div class="next-steps">
  <a href="./basic/" class="step-card">
    <span class="number">1</span>
    <span class="title">Basic Examples</span>
  </a>
  <a href="./media/" class="step-card">
    <span class="number">2</span>
    <span class="title">Media Processing</span>
  </a>
  <a href="./real-world/" class="step-card">
    <span class="number">3</span>
    <span class="title">Real-World Cases</span>
  </a>
</div>

::: tip Tips
- All examples are tested and can be run directly
- It's recommended to read the code and understand the logic before running
- If you encounter issues, check [Troubleshooting](/en/reference/troubleshooting.html)
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