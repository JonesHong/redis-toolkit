---
home: true
heroImage: /hero.png
heroText: Redis Toolkit
tagline: A powerful Redis toolkit that makes data processing simple and elegant.
actionText: Get Started →
actionLink: /en/guide/getting-started
features:
- title: 🎯 Smart Serialization
  details: Automatically handles various data types like dicts, lists, and NumPy arrays, eliminating manual conversion. Utilizes secure JSON serialization to avoid pickle's security risks.
- title: 🔐 Security First
  details: Rejects pickle, fully adopting JSON serialization. Built-in input validation and error handling ensure secure data operations.
- title: 🎵 Media Processing
  details: Built-in image, audio, and video converters for easy multimedia data handling. Supports popular frameworks like OpenCV and SciPy.
footer: MIT Licensed | Copyright © 2024 Redis Toolkit Team
---

<div class="features-extra">
  <div class="feature">
    <h3>🚀 Blazing Fast Setup</h3>
    <p>Install and run your first example in under 5 minutes, and immediately experience the power of Redis.</p>
  </div>
  <div class="feature">
    <h3>📡 Publish/Subscribe</h3>
    <p>Simplified Pub/Sub API with automatic JSON serialization, making message delivery effortless.</p>
  </div>
  <div class="feature">
    <h3>⚡ High Performance</h3>
    <p>Built-in connection pool management, batch operations, and retry mechanisms ensure efficient and stable Redis operations.</p>
  </div>
</div>

## 🎯 Quick Installation

<CodeGroup>
<CodeGroupItem title="Basic Installation">

```bash
pip install redis-toolkit
```

</CodeGroupItem>

<CodeGroupItem title="With Image Processing">

```bash
pip install redis-toolkit[cv2]
```

</CodeGroupItem>

<CodeGroupItem title="Full Installation">

```bash
pip install redis-toolkit[all]
```

</CodeGroupItem>
</CodeGroup>

## 📝 Simple Example

```python
from redis_toolkit import RedisToolkit

# Initialization
toolkit = RedisToolkit()

# Store various data types
toolkit.setter("user", {"name": "Alice", "age": 25})
toolkit.setter("scores", [95, 87, 92])
toolkit.setter("active", True)

# Automatic Deserialization
user = toolkit.getter("user")      # Returns dict
scores = toolkit.getter("scores")  # Returns list
active = toolkit.getter("active")  # Returns bool
```

## 🎨 Media Processing Example

```python
from redis_toolkit import RedisToolkit
from redis_toolkit.converters import encode_image, decode_image
import cv2

toolkit = RedisToolkit()

# Process image
img = cv2.imread('photo.jpg')
img_bytes = encode_image(img, format='jpg', quality=90)
toolkit.setter('my_image', img_bytes)

# Retrieve and decode
retrieved = toolkit.getter('my_image')
decoded_img = decode_image(retrieved)
```

## 🌟 Why Choose Redis Toolkit?

<div class="why-choose">
  <div class="reason">
    <h4>Simple & Intuitive</h4>
    <p>Clean API design and a gentle learning curve allow you to focus on business logic rather than low-level implementation details.</p>
  </div>
  <div class="reason">
    <h4>Comprehensive Features</h4>
    <p>From basic operations to advanced functionalities, from data access to media processing, one toolkit meets all your needs.</p>
  </div>
  <div class="reason">
    <h4>Stable & Reliable</h4>
    <p>Robust error handling, automatic retry mechanisms, and connection pool management ensure stable operation in production environments.</p>
  </div>
  <div class="reason">
    <h4>Active Community</h4>
    <p>Continuously updated and maintained, with quick issue responses. Contributions are welcome to build a better tool together.</p>
  </div>
</div>

---

<div class="getting-started-cta">
  <h2>Ready to Get Started?</h2>
  <p>Follow our guide to easily master the powerful features of Redis Toolkit.</p>
  <a href="/en/guide/getting-started" class="action-button">Start Now →</a>
</div>