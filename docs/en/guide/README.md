# User Guide

Welcome to Redis Toolkit! This guide will walk you through mastering this powerful tool, starting from scratch.

## 📚 Learning Path

We've designed clear learning paths for users of different levels:

### 🎯 Getting Started for Newbies (Recommended 1-2 hours)

1. **[Quick Start](./getting-started.md)** - Get started in 5 minutes
   - Simplest installation method
   - Your first Hello World example
   - Quick understanding of basic concepts

2. **[Installation Guide](./installation.md)** - Detailed installation instructions
   - System requirements
   - Various installation methods
   - Optional dependencies explanation
   - Troubleshooting common issues

3. **[Basic Usage](./basic-usage.md)** - Master core functionalities
   - Basic access operations
   - Data type handling
   - Simple configuration

### 🚀 Advanced Learning (Recommended 2-4 hours)

4. **[Serialization Features](./serialization.md)** - Deep dive into automatic serialization
   - Supported data types
   - Custom serialization
   - Performance considerations

5. **[Publish/Subscribe](./pubsub.md)** - Master message passing
   - Pub/Sub fundamentals
   - Message handler design
   - Multi-channel subscription

6. **[Configuration Options](./configuration.md)** - Customize your tool
   - Connection configuration
   - Advanced options
   - Best practices

## 🎯 Choose Your Starting Point

<div class="learning-paths">
  <div class="path-card">
    <h3>🆕 Complete Beginner</h3>
    <p>First time with Redis?</p>
    <a href="./getting-started.html" class="path-link">Start with Quick Start →</a>
  </div>
  
  <div class="path-card">
    <h3>💻 Experienced Developer</h3>
    <p>Familiar with basic Redis operations?</p>
    <a href="./serialization.html" class="path-link">Jump directly to Advanced Features →</a>
  </div>
  
  <div class="path-card">
    <h3>🏃 In a Hurry?</h3>
    <p>Need to get up to speed quickly?</p>
    <a href="./basic-usage.html" class="path-link">Check out practical examples →</a>
  </div>
</div>

## 💡 Learning Tips

::: tip Best Learning Approach
1. **Hands-on Practice**: Each section includes executable code examples
2. **Step-by-step**: Follow the recommended order to avoid skipping fundamentals
3. **Practical Application**: Try applying the learned features to your projects
:::

::: warning Important Notes
- Ensure your Redis service is running
- Python version must be >= 3.7
- Some advanced features require additional dependency packages
:::

## 🔗 Quick Links

- **Facing issues?** See [Troubleshooting](/en/reference/troubleshooting.html)
- **Need examples?** Browse [Example Code](/en/examples/)
- **API details?** Refer to [API Documentation](/en/api/)

<style>
.learning-paths {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.path-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.path-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.path-card h3 {
  color: #dc382d;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.path-card p {
  color: #666;
  margin-bottom: 1rem;
}

.path-link {
  display: inline-block;
  color: #dc382d;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border: 2px solid #dc382d;
  border-radius: 4px;
  transition: all 0.2s;
}

.path-link:hover {
  background: #dc382d;
  color: white;
}
</style>