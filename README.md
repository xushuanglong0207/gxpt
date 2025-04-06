# 高效测试平台

这是一个集成了API自动化测试、UI自动化测试和SSH自动化测试的综合测试平台。

## 功能特点

- **API自动化测试**：支持REST API、GraphQL等接口的自动化测试
- **UI自动化测试**：基于Selenium的Web界面自动化测试
- **SSH自动化测试**：远程服务器操作和测试
- **报告生成**：美观的测试报告，支持多种格式（HTML、Allure、JSON）
- **并行执行**：支持测试用例并行执行
- **配置管理**：灵活的环境配置和参数管理
- **日志记录**：详细的测试执行日志

## 项目结构

```
auto_test_platform/
├── api_test/            # API测试模块
│   ├── testcases/       # API测试用例
│   └── api_test_runner.py  # API测试运行器
├── ui_test/             # UI测试模块
│   ├── testcases/       # UI测试用例
│   ├── screenshots/     # 测试截图
│   └── ui_test_runner.py   # UI测试运行器
├── ssh_test/            # SSH测试模块
│   ├── testcases/       # SSH测试用例
│   ├── logs/            # SSH命令日志
│   └── ssh_test_runner.py  # SSH测试运行器
├── common/              # 公共组件
│   ├── config_manager.py   # 配置管理
│   └── report_generator.py # 报告生成
├── config/              # 配置文件
│   ├── config.yaml         # 通用配置
│   ├── config_dev.yaml     # 开发环境配置
│   ├── config_test.yaml    # 测试环境配置
│   └── config_prod.yaml    # 生产环境配置
├── reports/             # 测试报告
├── logs/                # 日志文件
├── requirements.txt     # 依赖包
└── run.py               # 主运行入口
```

## 安装与配置

### 环境要求

- Python 3.7+
- Chrome/Firefox/Edge浏览器（UI测试）
- SSH访问权限（SSH测试）

### 安装步骤

1. 克隆项目到本地
   ```bash
   git clone https://github.com/yourusername/auto_test_platform.git
   cd auto_test_platform
   ```

2. 创建虚拟环境（可选但推荐）
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量或修改配置文件
   - 创建`.env`文件设置敏感信息（如密码、API密钥等）
   - 或直接修改`config/`目录下的配置文件

## 使用方法

### 运行所有测试

```bash
python run.py
```

### 运行特定模块测试

```bash
python run.py --module api  # 运行API测试
python run.py --module ui   # 运行UI测试
python run.py --module ssh  # 运行SSH测试
```

### 指定环境

```bash
python run.py --env dev   # 开发环境
python run.py --env test  # 测试环境
python run.py --env prod  # 生产环境
```

### 指定报告类型

```bash
python run.py --report html    # 生成HTML报告
python run.py --report allure  # 生成Allure报告
python run.py --report json    # 生成JSON报告
```

### 并行执行

```bash
python run.py --parallel 5  # 使用5个并行进程
```

### 按标签运行测试

```bash
python run.py --tags "api,login"  # 运行带有api和login标签的测试
```

## 测试用例编写

### API测试用例

API测试用例使用JSON格式定义，放置在`api_test/testcases/`目录下。示例：

```json
{
  "name": "用户API测试",
  "description": "测试用户相关的API接口",
  "tags": ["api", "user"],
  "method": "GET",
  "endpoint": "/api/users",
  "headers": {
    "Authorization": "Bearer {{token}}"
  },
  "params": {
    "page": 1,
    "limit": 10
  },
  "expected_status": 200,
  "expected_response": {
    "success": true
  }
}
```

### UI测试用例

UI测试用例使用JSON格式定义，放置在`ui_test/testcases/`目录下。示例：

```json
{
  "name": "登录功能测试",
  "description": "测试用户登录功能",
  "tags": ["ui", "login"],
  "url": "http://example.com/login",
  "steps": [
    {
      "name": "输入用户名",
      "action": "input",
      "locator": {
        "type": "id",
        "value": "username"
      },
      "value": "testuser"
    },
    {
      "name": "点击登录按钮",
      "action": "click",
      "locator": {
        "type": "css",
        "value": "button[type='submit']"
      }
    }
  ]
}
```

### SSH测试用例

SSH测试用例使用JSON格式定义，放置在`ssh_test/testcases/`目录下。示例：

```json
{
  "name": "服务器状态检查",
  "description": "检查服务器的基本状态",
  "tags": ["ssh", "server"],
  "host": "server.example.com",
  "port": 22,
  "username": "admin",
  "key_file": "~/.ssh/id_rsa",
  "commands": [
    {
      "name": "检查磁盘空间",
      "command": "df -h"
    },
    {
      "name": "检查内存使用",
      "command": "free -m"
    }
  ],
  "expected_results": {
    "检查磁盘空间": {
      "exit_code": 0
    }
  }
}
```

## 配置说明

在`config/config.yaml`和环境特定的配置文件中可以配置：

- 测试环境（开发、测试、生产）
- API基础URL和请求头
- 浏览器类型和选项
- SSH连接信息
- 并行执行数量
- 报告格式和路径
- 日志级别和路径

## 扩展开发

1. 在对应模块下创建新的测试用例
2. 遵循项目的设计模式和命名规范
3. 运行测试验证功能

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件 
