# 性能测试后台管理系统

这是一个现代化的性能测试后台管理系统，提供测试用例管理、CSV数据分析和知识分享功能。

## 功能特点

### 1. 简化的测试用例设计
- 简洁记录测试用例的基本步骤、描述和预期结果
- 轻量级的数据结构，避免冗余信息
- 直观的用户界面，方便查看和管理测试用例

### 2. CSV文件上传与自动生成表格
- 支持CSV文件上传和自动解析
- 根据列名自动生成可视化表格
- 支持数据排序、筛选和搜索
- 数据验证和错误处理
- 支持导出和分享数据

### 3. 测试知识分享模块
- 富文本编辑器支持，可添加文本、图片、代码块等
- 分类和标签系统，便于组织和查找
- 评论和反馈功能
- 版本历史管理
- 搜索功能

## 技术栈

### 前端
- React.js + TypeScript
- Next.js (服务端渲染)
- Ant Design Pro (UI组件库)
- Axios (HTTP客户端)
- React-Quill (富文本编辑器)
- ECharts (数据可视化)
- PapaParse (CSV解析)

### 后端
- Node.js + Express
- Sequelize ORM
- PostgreSQL (数据库)
- JWT (身份验证)
- Multer (文件上传)
- Winston (日志记录)

## 系统架构

```
performance-test-system/
├── frontend/                # 前端代码
│   ├── public/              # 静态资源
│   └── src/                 # 源代码
│       ├── components/      # 组件
│       ├── pages/           # 页面
│       ├── layouts/         # 布局
│       ├── styles/          # 样式
│       ├── utils/           # 工具函数
│       ├── services/        # API服务
│       ├── hooks/           # 自定义钩子
│       ├── context/         # 上下文
│       └── assets/          # 资源文件
│
├── backend/                 # 后端代码
│   ├── src/                 # 源代码
│   │   ├── controllers/     # 控制器
│   │   ├── models/          # 数据模型
│   │   ├── routes/          # 路由
│   │   ├── services/        # 服务
│   │   ├── middlewares/     # 中间件
│   │   ├── utils/           # 工具函数
│   │   └── config/          # 配置文件
│   └── uploads/             # 上传文件存储
│
└── docs/                    # 文档
```

## 数据库设计

系统使用PostgreSQL数据库，主要包含以下表：

1. `users` - 用户信息
2. `test_cases` - 测试用例
3. `csv_data` - CSV文件数据
4. `knowledge_shares` - 知识分享
5. `tags` - 标签
6. `comments` - 评论

## 部署指南

### 前提条件
- Node.js (v14+)
- PostgreSQL (v12+)
- npm 或 yarn

### 后端部署
1. 进入后端目录
   ```bash
   cd performance-test-system/backend
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 创建`.env`文件并配置环境变量
   ```
   NODE_ENV=production
   PORT=3001
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=performance_test_system
   DB_USER=postgres
   DB_PASSWORD=your_password
   JWT_SECRET=your_jwt_secret
   ```

4. 启动服务器
   ```bash
   npm start
   ```

### 前端部署
1. 进入前端目录
   ```bash
   cd performance-test-system/frontend
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 创建`.env.local`文件并配置环境变量
   ```
   NEXT_PUBLIC_API_URL=http://localhost:404
This page could not be found.3001/api
   ```

4. 构建生产版本
   ```bash
   npm run build
   ```

5. 启动服务
   ```bash
   npm startDocker Desktop - WSL update failed
   An error occurred while updating WSL.
   
   You can manually update using wsl --update.
   
   If the issue persists, collect diagnostics and submit an issue ⁠.
   
   wsl update failed: update failed: updating wsl: exit code: 1: running WSL command wsl.exe C:\WINDOWS\System32\wsl.exe --update --web-download: : exit status 1
   ```

### 使用Docker部署（推荐）
1. 确保安装了Docker和Docker Compose
2. 在项目根目录运行
   ```bash
   docker-compose up -d
   ```

## 使用指南

### 1. 用户注册与登录
- 访问系统首页，点击"注册"创建新账户
- 使用邮箱和密码登录系统

### 2. 测试用例管理
- 在"测试用例"页面可以查看、创建、编辑和删除测试用例
- 点击"新建测试用例"按钮创建新的测试用例
- 填写测试标题、步骤和预期结果
- 可以设置优先级和状态

### 3. CSV数据分析
- 在"CSV数据"页面可以上传和管理CSV文件
- 点击"上传CSV"按钮选择文件上传
- 系统会自动解析CSV并生成表格
- 可以对数据进行排序、筛选和搜索
- 点击"导出"按钮可以导出数据

### 4. 知识分享
- 在"知识库"页面可以浏览和创建知识分享
- 点击"新建文章"按钮创建新的知识分享
- 使用富文本编辑器编写内容
- 可以添加分类和标签
- 支持版本历史管理和回退
- 可以对文章进行评论和点赞

## 常见问题

1. **Q: 如何重置密码？**
   A: 在登录页面点击"忘记密码"，按照提示操作。

2. **Q: 上传CSV文件有什么限制？**
   A: 文件大小限制为10MB，只支持.csv格式。

3. **Q: 如何管理用户权限？**
   A: 管理员可以在"用户管理"页面设置用户角色和权限。

## 联系与支持

如有问题或建议，请联系系统管理员或发送邮件至support@example.com。

## 许可证

本项目采用MIT许可证。 