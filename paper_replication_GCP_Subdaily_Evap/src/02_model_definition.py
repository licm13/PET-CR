# -*- coding: utf-8 -*-
"""
02_model_definition.py

此文件是一个薄包装，用于符合“01/02/03/04”命名结构。
实际的模型定义位于同目录下的 `model_definition.py` 中。

This file is a thin wrapper to satisfy the "01/02/03/04" naming convention.
The actual model definition is in `model_definition.py`.
"""

from model_definition import *  # noqa: F401,F403

if __name__ == "__main__":
    print("GCPWithStability is defined in model_definition.py")
