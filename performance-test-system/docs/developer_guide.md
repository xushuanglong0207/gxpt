# 性能测试后台管理系统开发者指南

## 目录

1. [系统架构概述](#系统架构概述)
2. [技术栈详解](#技术栈详解)
3. [项目结构](#项目结构)
4. [开发环境搭建](#开发环境搭建)
5. [API文档](#API文档)
6. [数据库设计](#数据库设计)
7. [前端开发指南](#前端开发指南)
8. [后端开发指南](#后端开发指南)
9. [测试指南](#测试指南)
10. [部署指南](#部署指南)
11. [常见问题与解决方案](#常见问题与解决方案)

## 系统架构概述

性能测试后台管理系统采用前后端分离的架构，由以下主要部分组成：

1. **前端应用**：基于React.js和Next.js构建的单页面应用（SPA）
2. **后端API服务**：基于Node.js和Express构建的RESTful API服务
3. **数据库**：PostgreSQL关系型数据库
4. **文件存储**：用于存储上传的CSV文件和其他资源
5. **认证服务**：基于JWT的用户认证和授权系统

系统架构图：

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│             │      │             │      │             │
│  前端应用   │ <──> │  后端API    │ <──> │  数据库     │
│  (Next.js)  │      │  (Express)  │      │ (PostgreSQL)│
│             │      │             │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
                           ↑
                           │
                     ┌─────┴─────┐
                     │           │
                     │ 文件存储  │
                     │           │
                     └───────────┘
```

## 技术栈详解

### 前端技术栈

- **React.js**: 用于构建用户界面的JavaScript库
- **Next.js**: React框架，提供服务端渲染、路由等功能
- **TypeScript**: JavaScript的超集，提供类型检查
- **Ant Design Pro**: 企业级UI组件库
- **Axios**: 基于Promise的HTTP客户端
- **React-Quill**: 富文本编辑器
- **ECharts**: 数据可视化库
- **PapaParse**: CSV解析库
- **Styled-Components**: CSS-in-JS解决方案
- **Dayjs**: 轻量级日期处理库
- **Immer**: 不可变状态管理
- **ahooks**: React Hooks库

### 后端技术栈

- **Node.js**: JavaScript运行时环境
- **Express**: Web应用框架
- **Sequelize**: ORM框架，用于数据库操作
- **PostgreSQL**: 关系型数据库
- **JWT**: JSON Web Token，用于身份验证
- **Bcrypt**: 密码哈希库
- **Multer**: 文件上传中间件
- **Winston**: 日志记录库
- **Joi**: 数据验证库
- **Dotenv**: 环境变量管理

## 项目结构

### 前端项目结构

```
frontend/
├── public/                # 静态资源
├── src/
│   ├── components/        # 可复用组件
│   │   ├── common/        # 通用组件
│   │   ├── testCase/      # 测试用例相关组件
│   │   ├── csvData/       # CSV数据相关组件
│   │   └── knowledge/     # 知识分享相关组件
│   ├── pages/             # 页面组件
│   │   ├── _app.tsx       # 应用入口
│   │   ├── index.tsx      # 首页
│   │   ├── login.tsx      # 登录页
│   │   ├── test-cases/    # 测试用例页面
│   │   ├── csv-data/      # CSV数据页面
│   │   └── knowledge/     # 知识分享页面
│   ├── layouts/           # 布局组件
│   ├── styles/            # 样式文件
│   ├── utils/             # 工具函数
│   ├── services/          # API服务
│   ├── hooks/             # 自定义Hooks
│   ├── context/           # React上下文
│   └── assets/            # 资源文件
├── .env.local             # 本地环境变量
├── next.config.js         # Next.js配置
├── tsconfig.json          # TypeScript配置
└── package.json           # 项目依赖
```

### 后端项目结构

```
backend/
├── src/
│   ├── controllers/       # 控制器
│   │   ├── testCase.controller.js
│   │   ├── csvData.controller.js
│   │   ├── knowledgeShare.controller.js
│   │   └── auth.controller.js
│   ├── models/            # 数据模型
│   │   ├── index.js
│   │   ├── testCase.model.js
│   │   ├── csvData.model.js
│   │   ├── knowledgeShare.model.js
│   │   ├── user.model.js
│   │   ├── tag.model.js
│   │   └── comment.model.js
│   ├── routes/            # 路由
│   │   ├── testCase.routes.js
│   │   ├── csvData.routes.js
│   │   ├── knowledgeShare.routes.js
│   │   └── auth.routes.js
│   ├── services/          # 服务
│   │   ├── testCase.service.js
│   │   ├── csvData.service.js
│   │   ├── knowledgeShare.service.js
│   │   └── auth.service.js
│   ├── middlewares/       # 中间件
│   │   ├── auth.middleware.js
│   │   ├── upload.middleware.js
│   │   └── validation.middleware.js
│   ├── utils/             # 工具函数
│   │   ├── logger.js
│   │   ├── csvParser.js
│   │   └── errorHandler.js
│   ├── config/            # 配置文件
│   │   ├── db.config.js
│   │   ├── auth.config.js
│   │   └── app.config.js
│   └── main.js            # 应用入口
├── .env                   # 环境变量
├── .sequelizerc           # Sequelize配置
└── package.json           # 项目依赖
```

## 开发环境搭建

### 前提条件

- Node.js (v14+)
- PostgreSQL (v12+)
- npm 或 yarn
- Git

### 克隆项目

```bash
git clone https://github.com/your-username/performance-test-system.git
cd performance-test-system
```

### 后端开发环境

1. 进入后端目录
   ```bash
   cd backend
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 创建`.env`文件
   ```
   NODE_ENV=development
   PORT=3001
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=performance_test_system
   DB_USER=postgres
   DB_PASSWORD=postgres
   JWT_SECRET=your_jwt_secret
   ```

4. 创建数据库
   ```bash
   createdb -U postgres performance_test_system
   ```

5. 启动开发服务器
   ```bash
   npm run dev
   ```

### 前端开发环境

1. 进入前端目录
   ```bash
   cd frontend
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 创建`.env.local`文件
   ```
   NEXT_PUBLIC_API_URL=http://localhost:3001/api
   ```

4. 启动开发服务器
   ```bash
   npm run dev
   ```

5. 访问 http://localhost:3000 查看应用

## API文档

系统API遵循RESTful设计原则，主要包括以下几类：

### 认证API

| 方法   | 路径                  | 描述           | 权限     |
|--------|----------------------|----------------|----------|
| POST   | /api/auth/register   | 用户注册       | 公开     |
| POST   | /api/auth/login      | 用户登录       | 公开     |
| POST   | /api/auth/refresh-token | 刷新令牌    | 公开     |
| POST   | /api/auth/change-password | 修改密码  | 已认证   |
| GET    | /api/auth/me         | 获取当前用户信息 | 已认证 |
| PUT    | /api/auth/profile    | 更新用户资料   | 已认证   |

### 测试用例API

| 方法   | 路径                  | 描述           | 权限     |
|--------|----------------------|----------------|----------|
| GET    | /api/test-cases      | 获取所有测试用例 | 已认证  |
| GET    | /api/test-cases/:id  | 获取单个测试用例 | 已认证  |
| POST   | /api/test-cases      | 创建测试用例   | 已认证   |
| PUT    | /api/test-cases/:id  | 更新测试用例   | 已认证   |
| DELETE | /api/test-cases/:id  | 删除测试用例   | 已认证   |
| POST   | /api/test-cases/batch-import | 批量导入 | 已认证 |
| GET    | /api/test-cases/export/:id | 导出测试用例 | 已认证 |

### CSV数据API

| 方法   | 路径                  | 描述           | 权限     |
|--------|----------------------|----------------|----------|
| GET    | /api/csv-data        | 获取所有CSV文件 | 已认证  |
| GET    | /api/csv-data/:id    | 获取单个CSV文件 | 已认证  |
| POST   | /api/csv-data/upload | 上传CSV文件    | 已认证   |
| GET    | /api/csv-data/export/:id | 导出CSV数据 | 已认证 |
| DELETE | /api/csv-data/:id    | 删除CSV文件    | 已认证   |
| PATCH  | /api/csv-data/:id    | 更新CSV文件描述 | 已认证 |
| GET    | /api/csv-data/:id/stats | 获取统计信息 | 已认证 |

### 知识分享API

| 方法   | 路径                  | 描述           | 权限     |
|--------|----------------------|----------------|----------|
| GET    | /api/knowledge       | 获取所有知识分享 | 已认证  |
| GET    | /api/knowledge/:id   | 获取单个知识分享 | 已认证  |
| POST   | /api/knowledge       | 创建知识分享   | 已认证   |
| PUT    | /api/knowledge/:id   | 更新知识分享   | 已认证   |
| DELETE | /api/knowledge/:id   | 删除知识分享   | 已认证   |
| GET    | /api/knowledge/search | 搜索知识分享  | 已认证   |
| GET    | /api/knowledge/:id/versions | 获取版本历史 | 已认证 |
| POST   | /api/knowledge/:id/comments | 添加评论 | 已认证 |
| GET    | /api/knowledge/:id/comments | 获取评论 | 已认证 |
| POST   | /api/knowledge/:id/like | 点赞        | 已认证   |

## 数据库设计

系统使用PostgreSQL数据库，主要包含以下表：

### users表

| 字段名    | 类型      | 描述        | 约束           |
|-----------|-----------|-------------|----------------|
| id        | UUID      | 用户ID      | 主键           |
| username  | VARCHAR   | 用户名      | 唯一, 非空     |
| email     | VARCHAR   | 邮箱        | 唯一, 非空     |
| password  | VARCHAR   | 密码哈希    | 非空           |
| fullName  | VARCHAR   | 全名        | 非空           |
| role      | ENUM      | 角色        | 非空, 默认'tester' |
| avatar    | VARCHAR   | 头像URL     |                |
| department| VARCHAR   | 部门        |                |
| isActive  | BOOLEAN   | 是否激活    | 默认true       |
| lastLogin | TIMESTAMP | 最后登录时间 |               |
| createdAt | TIMESTAMP | 创建时间    | 非空           |
| updatedAt | TIMESTAMP | 更新时间    | 非空           |

### test_cases表

| 字段名          | 类型      | 描述        | 约束           |
|-----------------|-----------|-------------|----------------|
| id              | UUID      | 测试用例ID  | 主键           |
| title           | VARCHAR   | 标题        | 非空           |
| steps           | TEXT      | 测试步骤    | 非空           |
| expectedResults | TEXT      | 预期结果    | 非空           |
| status          | ENUM      | 状态        | 非空, 默认'draft' |
| priority        | ENUM      | 优先级      | 非空, 默认'medium' |
| createdBy       | UUID      | 创建者ID    | 非空, 外键     |
| createdAt       | TIMESTAMP | 创建时间    | 非空           |
| updatedAt       | TIMESTAMP | 更新时间    | 非空           |

### csv_data表

| 字段名       | 类型      | 描述        | 约束           |
|--------------|-----------|-------------|----------------|
| id           | UUID      | CSV数据ID   | 主键           |
| filename     | VARCHAR   | 文件名      | 非空           |
| originalName | VARCHAR   | 原始文件名  | 非空           |
| description  | TEXT      | 描述        |                |
| data         | JSONB     | CSV数据     | 非空           |
| headers      | VARCHAR[] | 列头        | 非空           |
| size         | INTEGER   | 文件大小    | 非空           |
| uploadedBy   | UUID      | 上传者ID    | 非空, 外键     |
| createdAt    | TIMESTAMP | 创建时间    | 非空           |
| updatedAt    | TIMESTAMP | 更新时间    | 非空           |

### knowledge_shares表

| 字段名        | 类型      | 描述        | 约束           |
|---------------|-----------|-------------|----------------|
| id            | UUID      | 知识分享ID  | 主键           |
| title         | VARCHAR   | 标题        | 非空           |
| content       | TEXT      | 内容        | 非空           |
| htmlContent   | TEXT      | HTML内容    | 非空           |
| summary       | TEXT      | 摘要        |                |
| category      | VARCHAR   | 分类        | 非空           |
| authorId      | UUID      | 作者ID      | 非空, 外键     |
| status        | ENUM      | 状态        | 非空, 默认'draft' |
| viewCount     | INTEGER   | 查看次数    | 默认0          |
| likeCount     | INTEGER   | 点赞次数    | 默认0          |
| version       | INTEGER   | 版本号      | 默认1          |
| versionHistory| JSONB     | 版本历史    | 默认[]         |
| createdAt     | TIMESTAMP | 创建时间    | 非空           |
| updatedAt     | TIMESTAMP | 更新时间    | 非空           |

### tags表

| 字段名     | 类型      | 描述        | 约束           |
|------------|-----------|-------------|----------------|
| id         | UUID      | 标签ID      | 主键           |
| name       | VARCHAR   | 标签名      | 唯一, 非空     |
| color      | VARCHAR   | 颜色        | 默认'#1890ff'  |
| description| TEXT      | 描述        |                |
| createdAt  | TIMESTAMP | 创建时间    | 非空           |
| updatedAt  | TIMESTAMP | 更新时间    | 非空           |

### comments表

| 字段名      | 类型      | 描述        | 约束           |
|-------------|-----------|-------------|----------------|
| id          | UUID      | 评论ID      | 主键           |
| content     | TEXT      | 内容        | 非空           |
| userId      | UUID      | 用户ID      | 非空, 外键     |
| knowledgeId | UUID      | 知识分享ID  | 非空, 外键     |
| parentId    | UUID      | 父评论ID    | 可空           |
| isEdited    | BOOLEAN   | 是否已编辑  | 默认false      |
| createdAt   | TIMESTAMP | 创建时间    | 非空           |
| updatedAt   | TIMESTAMP | 更新时间    | 非空           |

## 前端开发指南

### 组件开发规范

1. **组件命名**：使用PascalCase命名组件文件和组件名
2. **目录结构**：按功能模块组织组件
3. **样式**：使用Styled-Components或CSS Modules
4. **状态管理**：使用React Hooks和Context API
5. **类型定义**：使用TypeScript接口定义props和状态

### 新增页面流程

1. 在`src/pages`目录下创建新页面文件
2. 在`src/services`目录下添加相应的API服务
3. 在`src/components`目录下创建页面所需组件
4. 在页面中引入组件和服务
5. 实现页面逻辑和UI

### 样式指南

1. 使用Ant Design Pro提供的组件和样式
2. 遵循设计规范，保持UI一致性
3. 使用响应式设计，适配不同屏幕尺寸
4. 使用主题变量，避免硬编码颜色和尺寸

### 国际化

1. 使用Next.js的国际化功能
2. 在`src/locales`目录下定义翻译文件
3. 使用`useTranslation`钩子获取翻译函数
4. 所有用户可见的文本都应支持国际化

## 后端开发指南

### 控制器开发规范

1. **命名**：使用camelCase命名控制器文件和方法
2. **职责**：控制器负责处理HTTP请求和响应
3. **错误处理**：使用try-catch捕获异常，返回统一格式的错误响应
4. **验证**：使用Joi验证请求数据

### 新增API流程

1. 在`src/models`目录下定义数据模型（如需要）
2. 在`src/services`目录下实现业务逻辑
3. 在`src/controllers`目录下创建控制器方法
4. 在`src/routes`目录下定义路由
5. 在`src/main.js`中注册路由

### 中间件开发

1. 中间件应该是纯函数，接收req、res和next参数
2. 中间件应该处理特定的横切关注点，如认证、日志记录等
3. 中间件应该在完成任务后调用next()，或在出错时调用next(error)

### 数据库操作

1. 使用Sequelize ORM进行数据库操作
2. 在模型中定义字段、关联和验证规则
3. 使用事务确保数据一致性
4. 使用索引优化查询性能

## 测试指南

### 单元测试

1. 使用Jest进行单元测试
2. 测试文件命名为`*.test.js`或`*.spec.js`
3. 测试覆盖率目标：80%+
4. 运行测试：`npm test`

### 集成测试

1. 使用Supertest测试API端点
2. 使用测试数据库进行测试
3. 测试文件放在`tests/integration`目录下
4. 运行集成测试：`npm run test:integration`

### 端到端测试

1. 使用Cypress进行端到端测试
2. 测试文件放在`cypress/integration`目录下
3. 运行端到端测试：`npm run test:e2e`

## 部署指南

### 传统部署

1. 构建前端应用：`cd frontend && npm run build`
2. 构建后端应用：`cd backend && npm run build`
3. 配置生产环境变量
4. 使用PM2或类似工具启动后端服务
5. 使用Nginx或类似工具部署前端静态文件

### Docker部署

1. 构建Docker镜像：`docker-compose build`
2. 启动容器：`docker-compose up -d`
3. 查看日志：`docker-compose logs -f`
4. 停止容器：`docker-compose down`

### CI/CD集成

1. 使用GitHub Actions或Jenkins设置CI/CD流程
2. 配置自动测试、构建和部署
3. 设置环境变量和密钥

## 常见问题与解决方案

### 1. 数据库连接问题

**问题**：无法连接到PostgreSQL数据库

**解决方案**：
- 检查数据库服务是否运行
- 验证连接参数（主机、端口、用户名、密码）
- 确保数据库用户有足够的权限
- 检查防火墙设置

### 2. 文件上传失败

**问题**：上传CSV文件时出错

**解决方案**：
- 检查文件大小是否超过限制（10MB）
- 确保文件格式正确（.csv）
- 验证上传目录是否存在且可写
- 检查磁盘空间是否充足

### 3. JWT认证问题

**问题**：JWT令牌验证失败

**解决方案**：
- 确保JWT_SECRET环境变量已正确设置
- 检查令牌是否过期
- 验证令牌格式是否正确
- 确保请求头中包含正确的Authorization字段

### 4. 前端构建问题

**问题**：前端构建失败

**解决方案**：
- 清除node_modules并重新安装依赖
- 检查package.json中的依赖版本
- 验证TypeScript类型定义
- 检查构建脚本和配置

### 5. 性能优化

**问题**：系统响应缓慢

**解决方案**：
- 优化数据库查询，添加适当的索引
- 实现缓存机制（如Redis）
- 使用分页加载大量数据
- 优化前端资源加载和渲染
- 考虑使用CDN加速静态资源 