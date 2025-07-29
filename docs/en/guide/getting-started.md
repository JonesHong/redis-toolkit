# Quick Start

In just 5 minutes, let's experience the power of Redis Toolkit together!

## 🚀 One-Minute Installation

Open your terminal and run the following command:

```bash
pip install redis-toolkit
```

That's it! The basic features are ready to use.

## 🎯 Your First Example

### 1. Import and Initialize

```python
from redis_toolkit import RedisToolkit

# The simplest way to initialize
toolkit = RedisToolkit()
```

::: tip Tip
By default, it connects to `localhost:6379`. If your Redis is located elsewhere, see [Configuration Options](./configuration.md).
:::

### 2. Store and Retrieve Data

```python
# Store a dictionary
user_data = {
    "id": 1001,
    "name": "Alice",
    "email": "alice@example.com",
    "scores": [95, 87, 92]
}
toolkit.setter("user:1001", user_data)

# Retrieve data - automatically deserialized to the original type!
retrieved = toolkit.getter("user:1001")
print(retrieved)
# Output: {'id': 1001, 'name': 'Alice', 'email': 'alice@example.com', 'scores': [95, 87, 92]}

# Note: retrieved is a dict, not a string!
print(type(retrieved))  # <class 'dict'>
```

### 3. Handle Different Data Types

The power of Redis Toolkit lies in automatically handling various Python data types:

```python
# Lists
toolkit.setter("top_scores", [100, 98, 95, 92, 88])
scores = toolkit.getter("top_scores")  # Returns list

# Booleans
toolkit.setter("is_active", True)
active = toolkit.getter("is_active")  # Returns bool, not string "true"

# Numbers
toolkit.setter("temperature", 23.5)
temp = toolkit.getter("temperature")  # Returns float

# Bytes
toolkit.setter("binary_data", b"Hello bytes!")
data = toolkit.getter("binary_data")  # Returns bytes
```

## 📡 Quick Pub/Sub Experience

### Send Messages

```python
# Publisher
publisher = RedisToolkit()

# Send structured messages
message = {
    "event": "user_login",
    "user_id": 1001,
    "timestamp": "2024-01-01 10:00:00"
}
publisher.publisher("events", message)
```

### Receive Messages

```python
# Subscriber
def handle_message(channel, data):
    print(f"Received message from {channel}:")
    print(f"Event: {data['event']}")
    print(f"User: {data['user_id']}")

subscriber = RedisToolkit(
    channels=["events"],
    message_handler=handle_message
)

# The subscriber automatically listens for messages in the background
```

## 🎨 Media Processing Preview

If you have the media processing package installed, you can easily handle images:

```python
# Requires: pip install redis-toolkit[cv2]
from redis_toolkit.converters import encode_image, decode_image
import cv2

# Read and store an image
img = cv2.imread('photo.jpg')
encoded = encode_image(img, format='jpg', quality=85)
toolkit.setter('user:1001:avatar', encoded)

# Retrieve the image
avatar_bytes = toolkit.getter('user:1001:avatar')
avatar_img = decode_image(avatar_bytes)
```

## ✅ Complete Example: User System

Let's integrate what we've learned with a practical example:

```python
from redis_toolkit import RedisToolkit
from datetime import datetime

class UserCache:
    def __init__(self):
        self.toolkit = RedisToolkit()
    
    def save_user(self, user_id, user_info):
        """Save user information"""
        # Add timestamp
        user_info['last_updated'] = datetime.now().isoformat()
        
        # Store in Redis
        key = f"user:{user_id}"
        self.toolkit.setter(key, user_info)
        
        # Set expiration (optional)
        self.toolkit.client.expire(key, 3600)  # Expires in 1 hour
    
    def get_user(self, user_id):
        """Get user information"""
        return self.toolkit.getter(f"user:{user_id}")
    
    def update_score(self, user_id, new_score):
        """Update user score"""
        user = self.get_user(user_id)
        if user:
            if 'scores' not in user:
                user['scores'] = []
            user['scores'].append(new_score)
            self.save_user(user_id, user)
            return True
        return False

# Usage example
cache = UserCache()

# Save user
cache.save_user(1001, {
    "name": "Alice",
    "email": "alice@example.com",
    "level": 5,
    "scores": [95, 87]
})

# Update score
cache.update_score(1001, 92)

# Get user
user = cache.get_user(1001)
print(f"{user['name']}'s scores: {user['scores']}")
# Output: Alice's scores: [95, 87, 92]
```

## 🎉 Congratulations!

You've learned the basics of Redis Toolkit! In just 5 minutes, you've discovered:

- ✅ How to install and initialize
- ✅ The power of automatic serialization
- ✅ Basic pub/sub usage
- ✅ Practical application examples

## 🚀 Next Steps

Ready to dive deeper? Here are some suggestions:

<div class="next-steps">
  <a href="./installation.html" class="next-step-card">
    <h4>📦 Detailed Installation Guide</h4>
    <p>Learn about installation options and dependency management</p>
  </a>
  
  <a href="./basic-usage.html" class="next-step-card">
    <h4>📖 Basic Usage Tutorial</h4>
    <p>Deep dive into using various features</p>
  </a>
  
  <a href="/en/advanced/media-processing.html" class="next-step-card">
    <h4>🎨 Advanced Media Processing</h4>
    <p>Explore image, audio, and video processing capabilities</p>
  </a>
</div>

::: tip Learning Tips
- Follow the examples hands-on to deepen your understanding
- Try modifying the examples to see what happens
- If you encounter issues, check the [FAQ](/en/reference/faq.html) or [Troubleshooting](/en/reference/troubleshooting.html)
:::

<style>
.next-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.next-step-card {
  display: block;
  padding: 1.5rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
}

.next-step-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #dc382d;
}

.next-step-card h4 {
  color: #dc382d;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.next-step-card p {
  color: #666;
  margin: 0;
  font-size: 0.95rem;
}
</style>