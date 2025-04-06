import os
import requests
from pathlib import Path

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
    """下载所有前端资源到本地"""
    # 设置基础路径
    static_dir = Path(__file__).parent / 'static'
    
    # 创建必要的目录结构
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
    
    # 要下载的文件列表
    files_to_download = [
        # Bootstrap & jQuery
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.1.3/css/bootstrap.min.css',
            'path': static_dir / 'css' / 'bootstrap.min.css'
        },
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.1.3/js/bootstrap.bundle.min.js',
            'path': static_dir / 'js' / 'bootstrap.bundle.min.js'
        },
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.min.js',
            'path': static_dir / 'js' / 'jquery.min.js'
        },
        
        # Font Awesome
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.3/css/all.min.css',
            'path': static_dir / 'css' / 'font-awesome.min.css'
        },
        # Font Awesome 字体文件
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.3/webfonts/fa-solid-900.woff2',
            'path': static_dir / 'fonts' / 'fa-solid-900.woff2'
        },
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.3/webfonts/fa-regular-400.woff2',
            'path': static_dir / 'fonts' / 'fa-regular-400.woff2'
        },
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.3/webfonts/fa-brands-400.woff2',
            'path': static_dir / 'fonts' / 'fa-brands-400.woff2'
        },
        
        # TinyMCE相关文件
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/tinymce.min.js',
            'path': static_dir / 'js' / 'tinymce' / 'tinymce.min.js'
        },
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/langs/zh_CN.min.js',
            'path': static_dir / 'js' / 'tinymce' / 'langs' / 'zh_CN.min.js'
        },
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/skins/ui/oxide/skin.min.css',
            'path': static_dir / 'js' / 'tinymce' / 'skins' / 'ui' / 'oxide' / 'skin.min.css'
        },
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/skins/ui/oxide/content.min.css',
            'path': static_dir / 'js' / 'tinymce' / 'skins' / 'ui' / 'oxide' / 'content.min.css'
        },
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/skins/content/default/content.min.css',
            'path': static_dir / 'js' / 'tinymce' / 'skins' / 'ui' / 'oxide' / 'default-content.min.css'
        },
        
        # ViewerJS
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/viewerjs/1.11.3/viewer.min.js',
            'path': static_dir / 'js' / 'viewer.min.js'
        },
        {
            'url': 'https://cdn.bootcdn.net/ajax/libs/viewerjs/1.11.3/viewer.min.css',
            'path': static_dir / 'css' / 'viewer.min.css'
        }
    ]
    
    # 下载所有文件
    success_count = 0
    total_count = len(files_to_download)
    
    for index, file_info in enumerate(files_to_download, 1):
        print(f"\n[{index}/{total_count}] 开始下载...")
        if download_file(file_info['url'], file_info['path']):
            success_count += 1
    
    print(f"\n下载完成! 成功下载: {success_count}/{total_count}")
    print(f"资源文件已保存到: {static_dir}")

if __name__ == '__main__':
    main() 