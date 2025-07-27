#!/usr/bin/env python3
"""
X API研究・分析ツール セットアップスクリプト

このスクリプトはプロジェクトのパッケージ情報と依存関係を定義します。
"""

from setuptools import setup, find_packages
import os

# プロジェクトのルートディレクトリを取得
here = os.path.abspath(os.path.dirname(__file__))

# README.mdの内容を読み込み
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# requirements.txtから依存関係を読み込み
def get_requirements():
    """requirements.txtから依存関係のリストを取得"""
    requirements = []
    requirements_path = os.path.join(here, 'requirements.txt')
    
    if os.path.exists(requirements_path):
        with open(requirements_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # コメント行と空行をスキップ
                if line and not line.startswith('#'):
                    requirements.append(line)
    
    return requirements

# バージョン情報
VERSION = '1.0.0'

# プロジェクト情報
setup(
    # =============================================================================
    # 基本情報
    # =============================================================================
    name='x-automation-tool',
    version=VERSION,
    description='X API研究・分析用ツール',
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    # =============================================================================
    # 作者・ライセンス情報
    # =============================================================================
    author='X Research Team',
    author_email='research@example.com',
    license='MIT',
    
    # =============================================================================
    # プロジェクトURL
    # =============================================================================
    url='https://github.com/your-username/x-automation-tool',
    project_urls={
        'Bug Reports': 'https://github.com/your-username/x-automation-tool/issues',
        'Source': 'https://github.com/your-username/x-automation-tool',
        'Documentation': 'https://github.com/your-username/x-automation-tool/wiki',
    },
    
    # =============================================================================
    # パッケージ設定
    # =============================================================================
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'docs.*']),
    include_package_data=True,
    
    # =============================================================================
    # Python バージョン要件
    # =============================================================================
    python_requires='>=3.9',
    
    # =============================================================================
    # 依存関係
    # =============================================================================
    install_requires=get_requirements(),
    
    # =============================================================================
    # 追加の依存関係グループ
    # =============================================================================
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-asyncio>=0.21.1',
            'pytest-cov>=4.1.0',
            'black>=23.11.0',
            'isort>=5.12.0',
            'flake8>=6.1.0',
            'mypy>=1.7.1',
        ],
        'docs': [
            'sphinx>=7.1.0',
            'sphinx-rtd-theme>=1.3.0',
            'myst-parser>=2.0.0',
        ],
        'monitoring': [
            'prometheus-client>=0.19.0',
            'grafana-api>=1.0.3',
        ]
    },
    
    # =============================================================================
    # エントリーポイント
    # =============================================================================
    entry_points={
        'console_scripts': [
            'x-automation-tool=run:main',
            'x-analysis=backend.ai.post_analyzer:main',
            'x-data-collector=backend.core.twitter_client:main',
        ],
    },
    
    # =============================================================================
    # 分類情報
    # =============================================================================
    classifiers=[
        # 開発状況
        'Development Status :: 4 - Beta',
        
        # 対象ユーザー
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        
        # トピック
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        
        # ライセンス
        'License :: OSI Approved :: MIT License',
        
        # プログラミング言語
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        
        # 環境
        'Environment :: Web Environment',
        'Environment :: Console',
        
        # フレームワーク
        'Framework :: FastAPI',
        
        # オペレーティングシステム
        'Operating System :: OS Independent',
        
        # 自然言語
        'Natural Language :: Japanese',
        'Natural Language :: English',
    ],
    
    # =============================================================================
    # キーワード
    # =============================================================================
    keywords=[
        'twitter', 'x-api', 'social-media', 'analysis', 'research',
        'ai', 'machine-learning', 'automation', 'fastapi', 'react',
        'data-science', 'social-network-analysis', 'groq'
    ],
    
    # =============================================================================
    # パッケージデータ
    # =============================================================================
    package_data={
        'backend': ['*.json', '*.yaml', '*.yml'],
        'frontend': ['*.json', '*.js', '*.css'],
    },
    
    # =============================================================================
    # データファイル
    # =============================================================================
    data_files=[
        ('config', ['tailwind.config.js']),
        ('', ['.env', '.gitignore']),
    ],
    
    # =============================================================================
    # ZIP セーフ設定
    # =============================================================================
    zip_safe=False,
    
    # =============================================================================
    # テストスイート
    # =============================================================================
    test_suite='tests',
    tests_require=[
        'pytest>=7.4.3',
        'pytest-asyncio>=0.21.1',
        'pytest-cov>=4.1.0',
    ],
)