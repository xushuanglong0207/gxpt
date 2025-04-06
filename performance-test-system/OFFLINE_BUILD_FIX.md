# 离线构建方案

如果您持续遇到网络问题，无法通过修改镜像源解决，这里提供一个离线构建方案。

## 方案一：使用本地Node.js环境

### 前端项目离线构建

1. 安装Node.js（如果尚未安装）：
   - 下载地址：https://nodejs.org/dist/v18.18.2/node-v18.18.2-x64.msi (Windows x64版本)
   - 安装时选择"添加到PATH"

2. 配置npm使用淘宝镜像：
   ```bash
   npm config set registry https://registry.npmmirror.com
   ```

3. 手动构建前端项目：
   ```bash
   cd performance-test-system/frontend
   npm install --legacy-peer-deps
   npm run build
   ```

4. 将构建后的dist或.next目录复制到Docker环境：
   - 修改前端Dockerfile，跳过构建步骤，直接复制构建产物

### 后端项目离线构建

1. 在本地安装依赖：
   ```bash
   cd performance-test-system/backend
   npm install --build-from-source
   ```

2. 使用本地Node.js运行后端：
   ```bash
   node src/app.js  # 或main.js或index.js
   ```

## 方案二：创建自定义基础镜像

如果您有能够正常访问互联网的环境，可以构建一个包含所有必要依赖的自定义基础镜像，然后在离线环境使用。

1. 在网络良好的环境中构建基础镜像：
   ```dockerfile
   FROM node:18-slim
   
   # 安装所有必要的系统依赖
   RUN apt-get update && apt-get install -y \
       python3 \
       make \
       g++ \
       gcc \
       ca-certificates \
       && rm -rf /var/lib/apt/lists/*
   
   # 预装常用npm包
   RUN npm install -g next react react-dom typescript @babel/core babel-plugin-import
   
   # 设置工作目录
   WORKDIR /app
   ```

2. 构建并保存镜像：
   ```bash
   docker build -t custom-node-base:18 .
   docker save -o custom-node-base.tar custom-node-base:18
   ```

3. 将tar文件传输到离线环境，并加载：
   ```bash
   docker load -i custom-node-base.tar
   ```

4. 在Dockerfile中使用这个自定义基础镜像：
   ```dockerfile
   FROM custom-node-base:18
   # 其余步骤...
   ```

## 方案三：完全离线Docker构建

如果必须使用Docker且网络问题无法解决：

1. 获取并保存所有必要的Docker镜像：
   ```bash
   docker pull node:18-slim
   docker save -o node-18-slim.tar node:18-slim
   ```

2. 创建一个包含所有npm依赖的压缩包：
   - 在一个能联网的环境中执行：
   ```bash
   cd performance-test-system/frontend
   npm install --legacy-peer-deps
   tar -czf node_modules.tar.gz node_modules
   
   cd ../backend
   npm install --build-from-source
   tar -czf node_modules.tar.gz node_modules
   ```

3. 修改Dockerfile使用本地依赖：
   ```dockerfile
   FROM node:18-slim
   
   WORKDIR /app
   
   # 复制本地预先下载的依赖
   COPY node_modules.tar.gz .
   RUN tar -xzf node_modules.tar.gz && rm node_modules.tar.gz
   
   # 复制代码
   COPY . .
   
   # 跳过npm install步骤
   # ...其余步骤...
   ```

## 方案四：使用预构建容器

如果您有多台机器需要部署，可以考虑：

1. 在网络良好的环境构建好Docker镜像
2. 将构建好的镜像保存为tar文件：
   ```bash
   docker save -o frontend-image.tar performance-test-system_frontend
   docker save -o backend-image.tar performance-test-system_backend
   ```
3. 将tar文件传输到离线环境
4. 在离线环境加载镜像：
   ```bash
   docker load -i frontend-image.tar
   docker load -i backend-image.tar
   ```
5. 使用docker-compose启动服务 