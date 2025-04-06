const express = require('express');
const router = express.Router();
const knowledgeShareController = require('../controllers/knowledgeShare.controller');
const authMiddleware = require('../middlewares/auth.middleware');

// 获取所有知识分享
router.get('/', /* authMiddleware.verifyToken, */ knowledgeShareController.findAll);

// 获取单个知识分享
router.get('/:id', /* authMiddleware.verifyToken, */ knowledgeShareController.findOne);

// 创建新知识分享
router.post('/', /* authMiddleware.verifyToken, */ knowledgeShareController.create);

// 更新知识分享
router.put('/:id', /* authMiddleware.verifyToken, */ knowledgeShareController.update);

// 删除知识分享
router.delete('/:id', /* authMiddleware.verifyToken, */ knowledgeShareController.delete);

// 搜索知识分享
router.get('/search', /* authMiddleware.verifyToken, */ knowledgeShareController.search);

// 获取知识分享的历史版本
router.get('/:id/versions', /* authMiddleware.verifyToken, */ knowledgeShareController.getVersions);

// 回退到特定版本
router.post('/:id/revert/:version', /* authMiddleware.verifyToken, */ knowledgeShareController.revertToVersion);

// 添加评论
router.post('/:id/comments', /* authMiddleware.verifyToken, */ knowledgeShareController.addComment);

// 获取评论
router.get('/:id/comments', /* authMiddleware.verifyToken, */ knowledgeShareController.getComments);

// 点赞知识分享
router.post('/:id/like', /* authMiddleware.verifyToken, */ knowledgeShareController.like);

// 获取知识分享的标签
router.get('/:id/tags', /* authMiddleware.verifyToken, */ knowledgeShareController.getTags);

// 添加标签
router.post('/:id/tags', /* authMiddleware.verifyToken, */ knowledgeShareController.addTags);

// 删除标签
router.delete('/:id/tags/:tagId', /* authMiddleware.verifyToken, */ knowledgeShareController.removeTag);

module.exports = router; 