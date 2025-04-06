const express = require('express');
const router = express.Router();
const testCaseController = require('../controllers/testCase.controller');
// const authMiddleware = require('../middlewares/auth.middleware');

// 批量导入测试用例
router.post('/batch-import', testCaseController.batchImport);

// 导出测试用例
router.get('/export/:id', testCaseController.exportTestCases);

// 获取所有测试用例
router.get('/', testCaseController.findAll);

// 根据ID获取单个测试用例
router.get('/:id', testCaseController.findOne);

// 创建新测试用例
router.post('/', testCaseController.create);

// 更新测试用例
router.put('/:id', testCaseController.update);

// 删除测试用例
router.delete('/:id', testCaseController.delete);

module.exports = router;
