#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
此文件用于抑制 Paramiko 库中的 TripleDES 弃用警告。
可以放在项目根目录，并在运行测试前导入。
"""

import warnings

# 抑制 cryptography 的弃用警告
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*TripleDES has been moved to cryptography.hazmat.decrepit.*"
)

# 抑制 paramiko 模块中的所有弃用警告
warnings.filterwarnings(
    "ignore", 
    category=DeprecationWarning, 
    module="paramiko.*"
)

# 特别抑制 CryptographyDeprecationWarning
try:
    from cryptography.utils import CryptographyDeprecationWarning
    warnings.filterwarnings(
        "ignore",
        category=CryptographyDeprecationWarning
    )
except ImportError:
    pass 