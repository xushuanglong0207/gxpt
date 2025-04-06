# Docker镜像拉取超时问题解决指南

## 问题描述

在构建Docker镜像时遇到以下错误：
```
failed to solve: node:18-alpine: failed to resolve source metadata for docker.io/library/node:18-alpine: failed to do request: Head "https://registry.docker-cn.com/v2/library/node/manifests/18-alpine?ns=docker.io": net/http: TLS handshake timeout
```

这是由于Docker尝试从Docker中国镜像站点(registry.docker-cn.com)拉取镜像，但连接超时导致的。

## 解决方案

### 方案1：更换Docker镜像源（推荐）

1. 打开Docker Desktop
2. 点击右上角的齿轮图标(Settings)
3. 在左侧导航中选择"Docker Engine"
4. 在右侧JSON配置中添加或修改registry-mirrors配置：

```json
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ],
  "experimental": false,
  "features": {
    "buildkit": true
  }
}
```

5. 点击"Apply & Restart"重启Docker服务
6. 重新构建镜像：`docker-compose build --no-cache backend`

### 方案2：临时使用非中国镜像源

如果您不想更改Docker全局配置，可以临时使用非镜像源拉取：

1. 手动拉取镜像（绕过镜像站点）：
```bash
# 设置临时环境变量
set DOCKER_CLI_EXPERIMENTAL=enabled

# 直接从Docker Hub拉取镜像
docker pull node:18-alpine --platform linux/amd64
```

2. 然后重新构建：
```bash
docker-compose build --no-cache backend
```

### 方案3：使用本地已有镜像

如果您的系统上已经有类似的基础镜像，可以修改Dockerfile使用本地镜像：

1. 查看本地已有的Node镜像：
```bash
docker images | grep node
```

2. 如果有类似镜像（例如node:16-alpine），可以临时修改Dockerfile：
```dockerfile
# 修改为本地已有的版本
FROM node:16-alpine

# 或使用完整标准镜像
FROM node:18
```

### 方案4：重启Docker服务和计算机

有时候简单地重启可以解决网络问题：

1. 完全退出Docker Desktop
2. 重启您的计算机
3. 重新启动Docker Desktop
4. 尝试重新构建：`docker-compose build --no-cache backend`

## 后续步骤

解决网络问题后，按照`REBUILD_STEPS.md`中的步骤继续完成系统重建：

1. 构建后端：`docker-compose build --no-cache backend`
2. 构建前端：`docker-compose build --no-cache frontend` 
3. 启动所有服务：`docker-compose up -d` 