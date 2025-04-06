# 使用官方Node.js镜像作为基础镜像（非Alpine版本）
FROM node:18-slim

# 使用中科大镜像源（HTTP）
RUN rm -f /etc/apt/sources.list.d/* && \
    rm -f /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    cat /etc/apt/sources.list

# 设置工作目录
WORKDIR /app

# 更新包列表并安装依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    make \
    g++ \
    gcc \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖（添加--build-from-source确保bcrypt能正确编译）
RUN npm install --production --build-from-source

# 复制所有文件
COPY . .

# 创建上传目录
RUN mkdir -p uploads

# 暴露3001端口
EXPOSE 3001

# 启动应用（检查多种可能的入口文件）
CMD ["sh", "-c", "if [ -f src/app.js ]; then node src/app.js; elif [ -f src/main.js ]; then node src/main.js; elif [ -f src/index.js ]; then node src/index.js; else echo 'No entry file found' && exit 1; fi"] 