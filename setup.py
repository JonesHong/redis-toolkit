#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Redis Toolkit - Enhanced Redis wrapper with multi-type data support"

# 读取 requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['redis>=4.0.0']

setup(
    name="redis-toolkit",
    version="0.1.3",
    author="JonesHong",
    author_email="latte831104@gmail.com",
    description="Enhanced Redis wrapper with multi-type data support and pub/sub automation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/JonesHong/redis-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        # 開發依賴
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.910',
            'pre-commit>=2.15',
        ],
        
        # 圖片處理依賴（包含 OpenCV）
        'cv2': [
            'opencv-python>=4.5.0',
            'numpy>=1.19.0',
        ],
        
        # 音頻處理依賴（基礎）
        'audio': [
            'numpy>=1.19.0',
            'scipy>=1.7.0',
        ],
        
        # 音頻處理依賴（進階，包含 MP3 支援）
        'audio-full': [
            'numpy>=1.19.0',
            'scipy>=1.7.0',
            'soundfile>=0.10.0',
        ],
        
        # 圖片處理依賴（包含 PIL）
        'image': [
            'opencv-python>=4.5.0',
            'numpy>=1.19.0',
            'Pillow>=8.0.0',
        ],
        
        # 視頻處理依賴（使用 OpenCV）
        'video': [
            'opencv-python>=4.5.0',
            'numpy>=1.19.0',
        ],
        
        # 媒體處理完整套件
        'media': [
            'opencv-python>=4.5.0',
            'numpy>=1.19.0',
            'scipy>=1.7.0',
            'soundfile>=0.10.0',
            'Pillow>=8.0.0',
        ],
        
        # 所有可選依賴
        'all': [
            'opencv-python>=4.5.0',
            'numpy>=1.19.0',
            'scipy>=1.7.0',
            'soundfile>=0.10.0',
            'Pillow>=8.0.0',
        ]
    },
    keywords="redis, toolkit, pubsub, serialization, buffer, audio, video, image, converter",
    project_urls={
        "Bug Reports": "https://github.com/JonesHong/redis-toolkit/issues",
        "Source": "https://github.com/JonesHong/redis-toolkit",
        # "Documentation": "https://redis-toolkit.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)