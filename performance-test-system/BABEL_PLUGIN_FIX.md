# Babel插件缺失修复指南

## 错误分析

在构建前端Docker镜像时遇到新的错误：
```
Failed to compile.
Error: Cannot find module 'babel-plugin-import'
```

**问题原因**：
1. 在`.babelrc`文件中配置了使用`babel-plugin-import`插件
2. 该插件未在项目的`package.json`中定义为依赖项
3. 构建时找不到这个模块

## 解决方案

### 方案1：添加缺失的Babel插件（推荐）

修改前端Dockerfile，在安装依赖后添加手动安装缺失插件的步骤：

```dockerfile
# 使用官方Node.js镜像作为基础镜像
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install --legacy-peer-deps --force

# 手动安装缺少的babel插件
RUN npm install --save-dev babel-plugin-import

# 复制所有文件
COPY . .

# ... 其余部分保持不变 ...
```

### 方案2：移除Babel配置（替代方案）

如果不想安装额外的插件，可以删除`.babelrc`文件或修改其内容：

```bash
# 删除.babelrc文件
rm performance-test-system/frontend/.babelrc
```

或者简化`.babelrc`内容：

```json
{
  "presets": [
    "next/babel"
  ]
}
```

### 方案3：更新package.json

如果希望长期使用该插件，应将其添加到项目的`package.json`文件中：

```json
{
  "devDependencies": {
    "babel-plugin-import": "^1.13.0",
    // ... 其他依赖项
  }
}
```

## 重建步骤

应用以上任一修改后，执行以下命令重新构建：

```bash
# 停止所有容器
docker-compose down

# 删除旧的镜像
docker rmi performance-test-system-frontend

# 重新构建前端
docker-compose build --no-cache frontend

# 启动所有服务
docker-compose up -d
``` 