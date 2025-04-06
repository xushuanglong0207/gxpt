// 认证中间件
const jwt = require('jsonwebtoken');

// JWT密钥，实际应用中应该放在环境变量中
const SECRET_KEY = 'your-secret-key';

// 验证JWT令牌
const verifyToken = (req, res, next) => {
  try {
    // 获取请求头中的Authorization
    const authHeader = req.headers.authorization;
    
    if (!authHeader) {
      return res.status(401).json({ message: '未提供认证令牌' });
    }
    
    // 提取令牌
    const token = authHeader.split(' ')[1];
    
    if (!token) {
      return res.status(401).json({ message: '无效的认证令牌格式' });
    }
    
    // 验证令牌
    jwt.verify(token, SECRET_KEY, (err, decoded) => {
      if (err) {
        return res.status(401).json({ message: '无效的认证令牌' });
      }
      
      // 将用户ID添加到请求对象
      req.userId = decoded.id;
      
      // 继续处理请求
      next();
    });
  } catch (error) {
    res.status(500).json({ message: '认证失败', error: error.message });
  }
};

// 验证管理员权限
const verifyAdmin = (req, res, next) => {
  try {
    // 首先验证令牌
    verifyToken(req, res, () => {
      // 这里应该查询数据库获取用户角色
      // 简化处理，假设用户ID为1的是管理员
      if (req.userId === '1') {
        next();
      } else {
        res.status(403).json({ message: '需要管理员权限' });
      }
    });
  } catch (error) {
    res.status(500).json({ message: '权限验证失败', error: error.message });
  }
};

module.exports = {
  verifyToken,
  verifyAdmin
};
