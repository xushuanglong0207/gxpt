const express = require('express');
const router = express.Router();
const authController = require('../controllers/auth.controller');
const authMiddleware = require('../middlewares/auth.middleware');

// 用户注册
router.post('/register', authController.register);

// 用户登录
router.post('/login', authController.login);

// 刷新token
router.post('/refresh-token', authController.refreshToken);

// 修改密码
router.post('/change-password', /* authMiddleware.verifyToken, */ authController.changePassword);

// 找回密码
router.post('/forgot-password', authController.forgotPassword);

// 重置密码
router.post('/reset-password', authController.resetPassword);

// 获取当前用户信息
router.get('/me', /* authMiddleware.verifyToken, */ authController.getCurrentUser);

// 更新用户资料
router.put('/profile', /* authMiddleware.verifyToken, */ authController.updateProfile);

// 登出
router.post('/logout', /* authMiddleware.verifyToken, */ authController.logout);

module.exports = router; 