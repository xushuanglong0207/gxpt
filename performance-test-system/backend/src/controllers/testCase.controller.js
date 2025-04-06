/**
 * 测试用例控制器
 */

const db = require('../models');
const TestCase = db.testCase;
const { Op } = require('sequelize');

/**
 * 获取所有测试用例
 */
exports.findAll = async (req, res) => {
  try {
    const { page = 1, limit = 10, search, status, priority } = req.query;
    const offset = (page - 1) * limit;
    
    const where = {};
    if (search) {
      where[Op.or] = [
        { title: { [Op.iLike]: `%${search}%` } },
        { steps: { [Op.iLike]: `%${search}%` } }
      ];
    }
    if (status) where.status = status;
    if (priority) where.priority = priority;

    const { count, rows } = await TestCase.findAndCountAll({
      where,
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['updatedAt', 'DESC']]
    });
    
    res.status(200).json({
      success: true,
      data: {
        total: count,
        items: rows,
        page: parseInt(page),
        totalPages: Math.ceil(count / limit)
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: '获取测试用例失败',
      error: error.message
    });
  }
};

/**
 * 获取单个测试用例
 */
exports.findOne = async (req, res) => {
  try {
    const { id } = req.params;
    const testCase = await TestCase.findByPk(id);
    
    if (!testCase) {
      return res.status(404).json({
        success: false,
        message: '测试用例不存在'
      });
    }
    
    res.status(200).json({
      success: true,
      data: testCase
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: '获取测试用例失败',
      error: error.message
    });
  }
};

/**
 * 创建测试用例
 */
exports.create = async (req, res) => {
  try {
    const testCaseData = {
      ...req.body,
      createdBy: req.user.id // 假设使用了auth中间件设置req.user
    };
    
    const newTestCase = await TestCase.create(testCaseData);
    
    res.status(201).json({
      success: true,
      message: '测试用例创建成功',
      data: newTestCase
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: '创建测试用例失败',
      error: error.message
    });
  }
};

/**
 * 更新测试用例
 */
exports.update = async (req, res) => {
  try {
    const { id } = req.params;
    const testCase = await TestCase.findByPk(id);
    
    if (!testCase) {
      return res.status(404).json({
        success: false,
        message: '测试用例不存在'
      });
    }
    
    // 检查权限
    if (testCase.createdBy !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: '没有权限修改此测试用例'
      });
    }
    
    await testCase.update(req.body);
    
    res.status(200).json({
      success: true,
      message: '测试用例更新成功',
      data: testCase
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: '更新测试用例失败',
      error: error.message
    });
  }
};

/**
 * 删除测试用例
 */
exports.delete = async (req, res) => {
  try {
    const { id } = req.params;
    const testCase = await TestCase.findByPk(id);
    
    if (!testCase) {
      return res.status(404).json({
        success: false,
        message: '测试用例不存在'
      });
    }
    
    // 检查权限
    if (testCase.createdBy !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: '没有权限删除此测试用例'
      });
    }
    
    await testCase.destroy();
    
    res.status(200).json({
      success: true,
      message: '测试用例删除成功'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: '删除测试用例失败',
      error: error.message
    });
  }
};

/**
 * 批量导入测试用例
 */
exports.batchImport = async (req, res) => {
  try {
    const testCases = req.body.map(testCase => ({
      ...testCase,
      createdBy: req.user.id
    }));
    
    const importedTestCases = await TestCase.bulkCreate(testCases, {
      validate: true
    });
    
    res.status(201).json({
      success: true,
      message: '测试用例批量导入成功',
      data: {
        count: importedTestCases.length,
        testCases: importedTestCases
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: '批量导入测试用例失败',
      error: error.message
    });
  }
};

/**
 * 导出测试用例
 */
exports.exportTestCases = async (req, res) => {
  try {
    const { ids } = req.query;
    const where = {};
    
    if (ids) {
      where.id = {
        [Op.in]: ids.split(',')
      };
    }
    
    const testCases = await TestCase.findAll({ where });
    
    res.status(200).json({
      success: true,
      data: testCases
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: '导出测试用例失败',
      error: error.message
    });
  }
}; 