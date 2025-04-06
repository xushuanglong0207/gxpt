import os
import requests
import shutil
from pathlib import Path

# TinyMCE资源下载脚本
def download_file(url, save_path):
    """下载文件并保存到指定路径"""
    print(f"下载: {url}")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 保存文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"已保存到: {save_path}")
        return True
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return False

def main():
    # 设置基础路径
    static_dir = Path(__file__).parent / 'static'
    
    # 创建必要的目录
    tinymce_dir = static_dir / 'js' / 'tinymce'
    tinymce_langs_dir = tinymce_dir / 'langs'
    tinymce_skins_dir = tinymce_dir / 'skins' / 'ui' / 'oxide'
    
    os.makedirs(tinymce_dir, exist_ok=True)
    os.makedirs(tinymce_langs_dir, exist_ok=True)
    os.makedirs(tinymce_skins_dir, exist_ok=True)
    
    # 要下载的TinyMCE文件列表
    files_to_download = [
        # 核心JS文件
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/tinymce.min.js',
            'path': tinymce_dir / 'tinymce.min.js'
        },
        # 中文语言包
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/langs/zh_CN.min.js',
            'path': tinymce_langs_dir / 'zh_CN.min.js'
        },
        # 皮肤CSS
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/skins/ui/oxide/skin.min.css',
            'path': tinymce_skins_dir / 'skin.min.css'
        },
        # 内容CSS
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/skins/ui/oxide/content.min.css',
            'path': tinymce_skins_dir / 'content.min.css'
        },
        # 查看器JS
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/viewerjs/1.11.3/viewer.min.js',
            'path': static_dir / 'js' / 'viewer.min.js'
        },
        # 查看器CSS
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/viewerjs/1.11.3/viewer.min.css',
            'path': static_dir / 'css' / 'viewer.min.css'
        }
    ]
    
    # 下载文件
    success_count = 0
    for file_info in files_to_download:
        if download_file(file_info['url'], file_info['path']):
            success_count += 1
    
    print(f"\n下载完成! 成功下载: {success_count}/{len(files_to_download)}")

if __name__ == '__main__':
    main() 