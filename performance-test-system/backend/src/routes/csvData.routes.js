const express = require('express');
const router = express.Router();
const csvDataController = require('../controllers/csvData.controller');
const authMiddleware = require('../middlewares/auth.middleware');
const uploadMiddleware = require('../middlewares/upload.middleware');

// 获取所有CSV文件元数据
router.get('/', /* authMiddleware.verifyToken, */ csvDataController.findAll);

// 获取单个CSV文件详情
router.get('/:id', /* authMiddleware.verifyToken, */ csvDataController.findOne);

// 上传CSV文件
router.post(
  '/upload',
  /* authMiddleware.verifyToken, */
  uploadMiddleware.single('file'),
  csvDataController.upload
);

// 导出CSV数据
router.get('/export/:id', /* authMiddleware.verifyToken, */ csvDataController.exportCsv);

// 删除CSV文件
router.delete('/:id', /* authMiddleware.verifyToken, */ csvDataController.delete);

// 更新CSV文件描述
router.patch('/:id', /* authMiddleware.verifyToken, */ csvDataController.update);

// 获取CSV文件数据的统计信息
router.get('/:id/stats', /* authMiddleware.verifyToken, */ csvDataController.getStats);

module.exports = router; 