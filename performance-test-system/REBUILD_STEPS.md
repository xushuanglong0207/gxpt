# Docker环境完整重建指南

## 1. 已修复的问题

本指南解决了以下几个关键问题：

1. **前端构建问题**：
   - ES模块与CommonJS不兼容导致的错误
   - Babel插件缺失问题

2. **后端构建问题**：
   - bcrypt包需要Python和编译工具
   - 入口文件路径不确定的问题

3. **Docker网络问题**：
   - 镜像拉取超时问题
   - 使用非Alpine基础镜像避免网络问题

## 2. 完整重建步骤

### 步骤0：解决Docker镜像拉取问题（如果遇到）

如果遇到Docker镜像拉取超时错误，请先按照`DOCKER_NETWORK_FIX.md`中的方法解决：

1. 更换Docker镜像源
2. 或使用node:18-slim替代node:18-alpine（已在Dockerfile中更新）
3. 或重启Docker服务

### 步骤1：停止并清理所有容器和镜像

```bash
# 停止所有容器
docker-compose down

# 删除所有相关镜像
docker rmi $(docker images "performance-test-system*" -q)

# 清理未使用的卷
docker volume prune -f

# 清理Docker系统缓存
docker system prune -a
```

### 步骤2：重新构建后端

后端Dockerfile已修改为：
- 使用`node:18-slim`基础镜像（避免Alpine镜像拉取问题）
- 添加了Python和编译工具（apt-get安装）
- 使用`--build-from-source`标志编译bcrypt
- 动态检测入口文件

```bash
# 重新构建后端（不使用缓存）
docker-compose build --no-cache backend
```

### 步骤3：重新构建前端

前端Dockerfile已修改为：
- 使用`node:18-slim`基础镜像（避免Alpine镜像拉取问题）
- 手动安装`babel-plugin-import`插件
- 简化了.babelrc文件
- 添加NODE_OPTIONS环境变量

```bash
# 重新构建前端（不使用缓存）
docker-compose build --no-cache frontend
```

### 步骤4：构建并启动所有服务

```bash
# 启动所有服务
docker-compose up -d
```

### 步骤5：验证服务是否正常运行

```bash
# 查看所有容器状态
docker-compose ps

# 检查前端是否可访问
curl -I http://localhost:3000

# 检查后端API是否可访问
curl http://localhost:3001/api/test-cases
```

## 3. 潜在的问题与解决方案

### 如果前端构建仍然失败

尝试使用以下命令查看详细的构建日志：
```bash
docker-compose logs frontend
```

可能的解决方案：
- 完全删除.babelrc文件
- 如果需要其它babel插件，请修改Dockerfile添加安装命令
- 考虑在next.config.js中增加更多transpilePackages

### 如果后端构建仍然失败

尝试使用以下命令查看详细的构建日志：
```bash
docker-compose logs backend
```

可能的解决方案：
- 使用完整的基础镜像 (FROM node:18)，而不是slim版本
- 尝试使用--unsafe-perm标志：`npm install --production --unsafe-perm`
- 如果bcrypt仍有问题，考虑使用纯JavaScript实现的替代品如bcryptjs

## 4. 通过浏览器验证

完成以上步骤后，在浏览器中访问以下URL：
- http://localhost:3000 - 应该显示登录页面或重定向到登录页面
- http://localhost:3000/login - 应显示登录界面
- http://localhost:3001/api/test-cases - 应返回API数据（可能为空数组或需要认证） 