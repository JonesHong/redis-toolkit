## 项目架构

```
redis-toolkit/
├── redis_toolkit/
│   ├── __init__.py              # 包初始化，导出主要类
│   ├── core.py                  # 主要的 RedisToolkit 类
│   ├── options.py               # RedisOptions 和配置选项
│   ├── exceptions.py            # 自定义异常类
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── serializers.py       # 数据序列化/反序列化工具
│   │   ├── retry.py             # 重试装饰器
│   │   └── validators.py        # 数据验证工具
│   └── types.py                 # 类型提示和数据类
├── tests/
│   ├── __init__.py
│   ├── test_core.py             # 核心功能测试
│   ├── test_serializers.py      # 序列化测试
│   ├── test_pubsub.py           # 发布订阅测试
│   └── conftest.py              # pytest 配置
├── examples/
│   ├── basic_usage.py           # 基础使用示例
│   ├── audio_streaming.py       # 音频流示例
│   └── video_buffer.py          # 视频缓冲示例
├── docs/
│   ├── README.md
│   ├── API.md                   # API 文档
│   └── EXAMPLES.md              # 使用示例
├── setup.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt         # 开发依赖
├── .gitignore
├── LICENSE
└── README.md
```
