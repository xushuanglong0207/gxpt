// 认证控制器
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

// JWT密钥，实际应用中应该放在环境变量中
const SECRET_KEY = 'your-secret-key';
const REFRESH_SECRET_KEY = 'your-refresh-secret-key';

// 模拟用户数据库
let users = [
  {
    id: '1',
    username: 'admin',
    password: 'admin123', // 实际应用中应该使用哈希存储
    email: 'admin@example.com',
    role: 'admin',
    profile: {
      name: '管理员',
      avatar: 'https://via.placeholder.com/150',
      department: '技术部',
      position: '系统管理员'
    }
  }
];

// 模拟刷新令牌存储
let refreshTokens = [];

// 生成JWT令牌
const generateToken = (userId) => {
  return jwt.sign({ id: userId }, SECRET_KEY, { expiresIn: '1h' });
};

// 生成刷新令牌
const generateRefreshToken = (userId) => {
  const refreshToken = jwt.sign({ id: userId }, REFRESH_SECRET_KEY, { expiresIn: '7d' });
  refreshTokens.push(refreshToken);
  return refreshToken;
};

// 用户注册
const register = (req, res) => {
  try {
    const { username, password, email } = req.body;
    
    if (!username || !password || !email) {
      return res.status(400).json({ message: '用户名、密码和邮箱不能为空' });
    }
    
    // 检查用户名是否已存在
    if (users.some(user => user.username === username)) {
      return res.status(400).json({ message: '用户名已存在' });
    }
    
    // 检查邮箱是否已存在
    if (users.some(user => user.email === email)) {
      return res.status(400).json({ message: '邮箱已存在' });
    }
    
    // 创建新用户
    const newUser = {
      id: uuidv4(),
      username,
      password, // 实际应用中应该哈希密码
      email,
      role: 'user',
      profile: {
        name: username,
        avatar: 'https://via.placeholder.com/150',
        department: '',
        position: ''
      }
    };
    
    users.push(newUser);
    
    // 生成令牌
    const token = generateToken(newUser.id);
    const refreshToken = generateRefreshToken(newUser.id);
    
    res.status(201).json({
      message: '注册成功',
      token,
      refreshToken,
      user: {
        id: newUser.id,
        username: newUser.username,
        email: newUser.email,
        role: newUser.role,
        profile: newUser.profile
      }
    });
  } catch (error) {
    res.status(500).json({ message: '注册失败', error: error.message });
  }
};

// 用户登录
const login = (req, res) => {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ message: '用户名和密码不能为空' });
    }
    
    // 查找用户
    const user = users.find(user => user.username === username);
    
    if (!user) {
      return res.status(401).json({ message: '用户名或密码错误' });
    }
    
    // 验证密码
    if (user.password !== password) { // 实际应用中应该比较哈希
      return res.status(401).json({ message: '用户名或密码错误' });
    }
    
    // 生成令牌
    const token = generateToken(user.id);
    const refreshToken = generateRefreshToken(user.id);
    
    res.status(200).json({
      message: '登录成功',
      token,
      refreshToken,
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role,
        profile: user.profile
      }
    });
  } catch (error) {
    res.status(500).json({ message: '登录失败', error: error.message });
  }
};

// 刷新令牌
const refreshToken = (req, res) => {
  try {
    const { refreshToken } = req.body;
    
    if (!refreshToken) {
      return res.status(400).json({ message: '刷新令牌不能为空' });
    }
    
    // 验证刷新令牌是否存在
    if (!refreshTokens.includes(refreshToken)) {
      return res.status(403).json({ message: '无效的刷新令牌' });
    }
    
    // 验证刷新令牌
    jwt.verify(refreshToken, REFRESH_SECRET_KEY, (err, decoded) => {
      if (err) {
        // 移除无效的刷新令牌
        refreshTokens = refreshTokens.filter(token => token !== refreshToken);
        return res.status(403).json({ message: '无效的刷新令牌' });
      }
      
      // 生成新的访问令牌
      const newToken = generateToken(decoded.id);
      
      res.status(200).json({
        message: '令牌刷新成功',
        token: newToken
      });
    });
  } catch (error) {
    res.status(500).json({ message: '刷新令牌失败', error: error.message });
  }
};

// 修改密码
const changePassword = (req, res) => {
  try {
    const userId = req.userId;
    const { currentPassword, newPassword } = req.body;
    
    if (!currentPassword || !newPassword) {
      return res.status(400).json({ message: '当前密码和新密码不能为空' });
    }
    
    // 查找用户
    const userIndex = users.findIndex(user => user.id === userId);
    
    if (userIndex === -1) {
      return res.status(404).json({ message: '用户不存在' });
    }
    
    // 验证当前密码
    if (users[userIndex].password !== currentPassword) { // 实际应用中应该比较哈希
      return res.status(401).json({ message: '当前密码错误' });
    }
    
    // 更新密码
    users[userIndex].password = newPassword; // 实际应用中应该哈希新密码
    
    res.status(200).json({ message: '密码修改成功' });
  } catch (error) {
    res.status(500).json({ message: '修改密码失败', error: error.message });
  }
};

// 找回密码
const forgotPassword = (req, res) => {
  try {
    const { email } = req.body;
    
    if (!email) {
      return res.status(400).json({ message: '邮箱不能为空' });
    }
    
    // 查找用户
    const user = users.find(user => user.email === email);
    
    if (!user) {
      // 为安全起见，即使用户不存在也返回成功
      return res.status(200).json({ message: '如果邮箱存在，重置密码链接已发送' });
    }
    
    // 实际应用中，这里应该生成密码重置令牌并发送邮件
    // 简化处理，直接返回成功
    
    res.status(200).json({ message: '如果邮箱存在，重置密码链接已发送' });
  } catch (error) {
    res.status(500).json({ message: '找回密码失败', error: error.message });
  }
};

// 重置密码
const resetPassword = (req, res) => {
  try {
    const { token, newPassword } = req.body;
    
    if (!token || !newPassword) {
      return res.status(400).json({ message: '令牌和新密码不能为空' });
    }
    
    // 实际应用中，应该验证密码重置令牌
    // 简化处理，假设令牌总是有效
    
    res.status(200).json({ message: '密码重置成功' });
  } catch (error) {
    res.status(500).json({ message: '重置密码失败', error: error.message });
  }
};

// 获取当前用户信息
const getCurrentUser = (req, res) => {
  try {
    const userId = req.userId;
    
    // 查找用户
    const user = users.find(user => user.id === userId);
    
    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }
    
    res.status(200).json({
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
      profile: user.profile
    });
  } catch (error) {
    res.status(500).json({ message: '获取用户信息失败', error: error.message });
  }
};

// 更新用户资料
const updateProfile = (req, res) => {
  try {
    const userId = req.userId;
    const { name, avatar, department, position } = req.body;
    
    // 查找用户
    const userIndex = users.findIndex(user => user.id === userId);
    
    if (userIndex === -1) {
      return res.status(404).json({ message: '用户不存在' });
    }
    
    // 更新用户资料
    const profile = users[userIndex].profile;
    
    if (name) profile.name = name;
    if (avatar) profile.avatar = avatar;
    if (department) profile.department = department;
    if (position) profile.position = position;
    
    res.status(200).json({
      message: '用户资料更新成功',
      profile: users[userIndex].profile
    });
  } catch (error) {
    res.status(500).json({ message: '更新用户资料失败', error: error.message });
  }
};

// 登出
const logout = (req, res) => {
  try {
    const { refreshToken } = req.body;
    
    // 移除刷新令牌
    refreshTokens = refreshTokens.filter(token => token !== refreshToken);
    
    res.status(200).json({ message: '登出成功' });
  } catch (error) {
    res.status(500).json({ message: '登出失败', error: error.message });
  }
};

module.exports = {
  register,
  login,
  refreshToken,
  changePassword,
  forgotPassword,
  resetPassword,
  getCurrentUser,
  updateProfile,
  logout
}; 