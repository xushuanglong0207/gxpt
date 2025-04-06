import os
from pathlib import Path

# 创建必要的目录结构
def main():
    # 设置基础路径
    static_dir = Path(__file__).parent / 'static'
    
    # 创建必要的目录
    directories = [
        static_dir / 'js',
        static_dir / 'css',
        static_dir / 'js' / 'tinymce',
        static_dir / 'js' / 'tinymce' / 'langs',
        static_dir / 'js' / 'tinymce' / 'skins' / 'ui' / 'oxide',
        static_dir / 'fonts'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"创建目录: {directory}")

if __name__ == '__main__':
    main()
    print("目录创建完成!") 