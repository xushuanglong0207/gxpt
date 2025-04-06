# 创建目录结构
$baseDir = ".\static"
New-Item -Path "$baseDir\css" -ItemType Directory -Force
New-Item -Path "$baseDir\js" -ItemType Directory -Force
New-Item -Path "$baseDir\js\tinymce\langs" -ItemType Directory -Force
New-Item -Path "$baseDir\js\tinymce\skins\ui\oxide" -ItemType Directory -Force
New-Item -Path "$baseDir\js\tinymce\skins\content\default" -ItemType Directory -Force
New-Item -Path "$baseDir\fonts" -ItemType Directory -Force

# 定义要下载的文件
$files = @(
    # Bootstrap & jQuery
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.1.3/css/bootstrap.min.css"
        path = "$baseDir\css\bootstrap.min.css"
    },
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.1.3/js/bootstrap.bundle.min.js"
        path = "$baseDir\js\bootstrap.bundle.min.js"
    },
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.min.js"
        path = "$baseDir\js\jquery.min.js"
    },
    
    # Font Awesome
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.3/css/all.min.css"
        path = "$baseDir\css\font-awesome.min.css"
    },
    # Font Awesome fonts
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.3/webfonts/fa-solid-900.woff2"
        path = "$baseDir\fonts\fa-solid-900.woff2"
    },
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.3/webfonts/fa-regular-400.woff2"
        path = "$baseDir\fonts\fa-regular-400.woff2"
    },
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/font-awesome/5.15.3/webfonts/fa-brands-400.woff2"
        path = "$baseDir\fonts\fa-brands-400.woff2"
    },
    
    # TinyMCE files
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/tinymce.min.js"
        path = "$baseDir\js\tinymce\tinymce.min.js"
    },
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/langs/zh_CN.min.js"
        path = "$baseDir\js\tinymce\langs\zh_CN.min.js"
    },
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/skins/ui/oxide/skin.min.css"
        path = "$baseDir\js\tinymce\skins\ui\oxide\skin.min.css"
    },
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/skins/ui/oxide/content.min.css"
        path = "$baseDir\js\tinymce\skins\ui\oxide\content.min.css"
    },
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/tinymce/6.7.0/skins/content/default/content.min.css"
        path = "$baseDir\js\tinymce\skins\content\default\content.min.css"
    },
    
    # ViewerJS
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/viewerjs/1.11.3/viewer.min.js"
        path = "$baseDir\js\viewer.min.js"
    },
    @{
        url = "https://cdn.bootcdn.net/ajax/libs/viewerjs/1.11.3/viewer.min.css"
        path = "$baseDir\css\viewer.min.css"
    },
    
    # Toastr
    @{
        url = "https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css"
        path = "$baseDir\css\toastr.min.css"
    },
    @{
        url = "https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js"
        path = "$baseDir\js\toastr.min.js"
    }
)

# Download files
$successCount = 0
$totalCount = $files.Count

foreach ($file in $files) {
    Write-Host "Downloading [$($successCount+1)/$totalCount]: $($file.url)" -ForegroundColor Cyan
    try {
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($file.url, $file.path)
        
        Write-Host "Download success: $($file.path)" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "Download failed: $($file.url)" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

Write-Host "`nDownload completed! Total: $successCount/$totalCount files" -ForegroundColor Yellow
Write-Host "Resources saved to: $baseDir" -ForegroundColor Yellow