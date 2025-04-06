# 使用官方Node.js镜像作为基础镜像（非Alpine版本）
FROM node:18-slim AS builder

# 使用中科大镜像源（HTTP）
RUN rm -f /etc/apt/sources.list.d/* && \
    rm -f /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    cat /etc/apt/sources.list

# 配置NPM使用淘宝镜像源
RUN npm config set registry https://registry.npmmirror.com

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install --legacy-peer-deps

# 手动安装缺少的babel插件
RUN npm install --save-dev babel-plugin-import

# 复制所有文件
COPY . .

# 确保public目录存在
RUN mkdir -p public

# 清理缓存
RUN npm cache clean --force
RUN rm -rf .next

# 添加NODE_OPTIONS环境变量以支持CommonJS
ENV NODE_OPTIONS="--max-old-space-size=4096"

# 构建应用
RUN npm run build

# 生产环境
FROM node:18-slim AS runner

# 使用中科大镜像源（HTTP）
RUN rm -f /etc/apt/sources.list.d/* && \
    rm -f /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    cat /etc/apt/sources.list

WORKDIR /app

# 设置环境变量
ENV NODE_ENV production
ENV PORT 3000

# 确保public目录存在
RUN mkdir -p public

# 复制必要文件
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# 如果使用standalone输出模式，复制standalone文件夹
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# 暴露3000端口
EXPOSE 3000

# 启动应用（使用standalone模式的启动命令）
CMD ["node", "server.js"] 