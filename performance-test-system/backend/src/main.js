const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const dotenv = require('dotenv');
const { sequelize } = require('./models');

// 加载环境变量
dotenv.config();

// 创建Express应用
const app = express();

// 中间件配置
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// 导入路由
const testCaseRoutes = require('./routes/testCase.routes');
// const csvDataRoutes = require('./routes/csvData.routes');
const knowledgeShareRoutes = require('./routes/knowledgeShare.routes');
const authRoutes = require('./routes/auth.routes');

// 注册路由
app.use('/api/test-cases', testCaseRoutes);
// app.use('/api/csv-data', csvDataRoutes);
app.use('/api/knowledge', knowledgeShareRoutes);
app.use('/api/auth', authRoutes);

// 默认路由
app.get('/', (req, res) => {
  res.json({ message: '欢迎使用性能测试后台管理系统API' });
});

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    message: err.message,
    error: process.env.NODE_ENV === 'production' ? {} : err
  });
});

// 设置端口
const PORT = process.env.PORT || 3001;

// 启动服务器
async function startServer() {
  try {
    // 连接数据库
    await sequelize.authenticate();
    console.log('数据库连接成功');
    
    // 启动服务器
    app.listen(PORT, () => {
      console.log(`服务器运行在端口 ${PORT}`);
    });
  } catch (error) {
    console.error('无法启动服务器:', error);
  }
}

startServer(); 