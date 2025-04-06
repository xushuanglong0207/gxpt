// 知识分享控制器
const { v4: uuidv4 } = require('uuid');

// 模拟数据存储
let knowledgeShares = [];

// 获取所有知识分享
const findAll = (req, res) => {
  try {
    res.status(200).json(knowledgeShares);
  } catch (error) {
    res.status(500).json({ message: '获取知识分享列表失败', error: error.message });
  }
};

// 获取单个知识分享
const findOne = (req, res) => {
  try {
    const id = req.params.id;
    const knowledge = knowledgeShares.find(item => item.id === id);
    
    if (!knowledge) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    res.status(200).json(knowledge);
  } catch (error) {
    res.status(500).json({ message: '获取知识分享详情失败', error: error.message });
  }
};

// 创建新知识分享
const create = (req, res) => {
  try {
    const { title, content, tags = [] } = req.body;
    
    if (!title || !content) {
      return res.status(400).json({ message: '标题和内容不能为空' });
    }
    
    const newKnowledge = {
      id: uuidv4(),
      title,
      content,
      tags,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      createdBy: req.userId || 'anonymous',
      versions: [],
      comments: [],
      likes: 0
    };
    
    knowledgeShares.push(newKnowledge);
    
    res.status(201).json(newKnowledge);
  } catch (error) {
    res.status(500).json({ message: '创建知识分享失败', error: error.message });
  }
};

// 更新知识分享
const update = (req, res) => {
  try {
    const id = req.params.id;
    const { title, content } = req.body;
    
    const knowledgeIndex = knowledgeShares.findIndex(item => item.id === id);
    
    if (knowledgeIndex === -1) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    // 保存当前版本
    const currentVersion = { ...knowledgeShares[knowledgeIndex] };
    delete currentVersion.versions;
    
    // 更新知识分享
    if (title) knowledgeShares[knowledgeIndex].title = title;
    if (content) knowledgeShares[knowledgeIndex].content = content;
    knowledgeShares[knowledgeIndex].updatedAt = new Date().toISOString();
    
    // 添加到版本历史
    if (!knowledgeShares[knowledgeIndex].versions) {
      knowledgeShares[knowledgeIndex].versions = [];
    }
    knowledgeShares[knowledgeIndex].versions.push(currentVersion);
    
    res.status(200).json(knowledgeShares[knowledgeIndex]);
  } catch (error) {
    res.status(500).json({ message: '更新知识分享失败', error: error.message });
  }
};

// 删除知识分享
const deleteKnowledge = (req, res) => {
  try {
    const id = req.params.id;
    const knowledgeIndex = knowledgeShares.findIndex(item => item.id === id);
    
    if (knowledgeIndex === -1) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    // 从数组中移除
    knowledgeShares.splice(knowledgeIndex, 1);
    
    res.status(200).json({ message: '知识分享删除成功' });
  } catch (error) {
    res.status(500).json({ message: '删除知识分享失败', error: error.message });
  }
};

// 搜索知识分享
const search = (req, res) => {
  try {
    const { query, tags } = req.query;
    
    let results = [...knowledgeShares];
    
    // 按关键词过滤
    if (query) {
      const searchQuery = query.toLowerCase();
      results = results.filter(
        item => item.title.toLowerCase().includes(searchQuery) || 
               item.content.toLowerCase().includes(searchQuery)
      );
    }
    
    // 按标签过滤
    if (tags) {
      const tagList = tags.split(',');
      results = results.filter(
        item => item.tags.some(tag => tagList.includes(tag))
      );
    }
    
    res.status(200).json(results);
  } catch (error) {
    res.status(500).json({ message: '搜索知识分享失败', error: error.message });
  }
};

// 获取知识分享的历史版本
const getVersions = (req, res) => {
  try {
    const id = req.params.id;
    const knowledge = knowledgeShares.find(item => item.id === id);
    
    if (!knowledge) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    res.status(200).json(knowledge.versions || []);
  } catch (error) {
    res.status(500).json({ message: '获取版本历史失败', error: error.message });
  }
};

// 回退到特定版本
const revertToVersion = (req, res) => {
  try {
    const id = req.params.id;
    const versionIndex = parseInt(req.params.version);
    
    const knowledgeIndex = knowledgeShares.findIndex(item => item.id === id);
    
    if (knowledgeIndex === -1) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    const knowledge = knowledgeShares[knowledgeIndex];
    
    if (!knowledge.versions || !knowledge.versions[versionIndex]) {
      return res.status(404).json({ message: '找不到该版本' });
    }
    
    // 保存当前版本
    const currentVersion = { ...knowledge };
    delete currentVersion.versions;
    
    // 恢复到指定版本
    const targetVersion = knowledge.versions[versionIndex];
    knowledge.title = targetVersion.title;
    knowledge.content = targetVersion.content;
    knowledge.updatedAt = new Date().toISOString();
    
    // 将当前版本添加到版本历史
    knowledge.versions.push(currentVersion);
    
    res.status(200).json(knowledge);
  } catch (error) {
    res.status(500).json({ message: '回退版本失败', error: error.message });
  }
};

// 添加评论
const addComment = (req, res) => {
  try {
    const id = req.params.id;
    const { content } = req.body;
    
    if (!content) {
      return res.status(400).json({ message: '评论内容不能为空' });
    }
    
    const knowledgeIndex = knowledgeShares.findIndex(item => item.id === id);
    
    if (knowledgeIndex === -1) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    const comment = {
      id: uuidv4(),
      content,
      createdAt: new Date().toISOString(),
      createdBy: req.userId || 'anonymous'
    };
    
    if (!knowledgeShares[knowledgeIndex].comments) {
      knowledgeShares[knowledgeIndex].comments = [];
    }
    
    knowledgeShares[knowledgeIndex].comments.push(comment);
    
    res.status(201).json(comment);
  } catch (error) {
    res.status(500).json({ message: '添加评论失败', error: error.message });
  }
};

// 获取评论
const getComments = (req, res) => {
  try {
    const id = req.params.id;
    const knowledge = knowledgeShares.find(item => item.id === id);
    
    if (!knowledge) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    res.status(200).json(knowledge.comments || []);
  } catch (error) {
    res.status(500).json({ message: '获取评论失败', error: error.message });
  }
};

// 点赞知识分享
const like = (req, res) => {
  try {
    const id = req.params.id;
    const knowledgeIndex = knowledgeShares.findIndex(item => item.id === id);
    
    if (knowledgeIndex === -1) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    // 增加点赞数
    knowledgeShares[knowledgeIndex].likes = (knowledgeShares[knowledgeIndex].likes || 0) + 1;
    
    res.status(200).json({ likes: knowledgeShares[knowledgeIndex].likes });
  } catch (error) {
    res.status(500).json({ message: '点赞失败', error: error.message });
  }
};

// 获取知识分享的标签
const getTags = (req, res) => {
  try {
    const id = req.params.id;
    const knowledge = knowledgeShares.find(item => item.id === id);
    
    if (!knowledge) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    res.status(200).json(knowledge.tags || []);
  } catch (error) {
    res.status(500).json({ message: '获取标签失败', error: error.message });
  }
};

// 添加标签
const addTags = (req, res) => {
  try {
    const id = req.params.id;
    const { tags } = req.body;
    
    if (!tags || !Array.isArray(tags)) {
      return res.status(400).json({ message: '标签必须是数组' });
    }
    
    const knowledgeIndex = knowledgeShares.findIndex(item => item.id === id);
    
    if (knowledgeIndex === -1) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    // 确保tags属性存在
    if (!knowledgeShares[knowledgeIndex].tags) {
      knowledgeShares[knowledgeIndex].tags = [];
    }
    
    // 添加新标签
    knowledgeShares[knowledgeIndex].tags = [
      ...new Set([...knowledgeShares[knowledgeIndex].tags, ...tags])
    ];
    
    res.status(200).json(knowledgeShares[knowledgeIndex].tags);
  } catch (error) {
    res.status(500).json({ message: '添加标签失败', error: error.message });
  }
};

// 删除标签
const removeTag = (req, res) => {
  try {
    const id = req.params.id;
    const tagId = req.params.tagId;
    
    const knowledgeIndex = knowledgeShares.findIndex(item => item.id === id);
    
    if (knowledgeIndex === -1) {
      return res.status(404).json({ message: '找不到该知识分享' });
    }
    
    if (!knowledgeShares[knowledgeIndex].tags) {
      return res.status(404).json({ message: '该知识分享没有标签' });
    }
    
    // 移除标签
    knowledgeShares[knowledgeIndex].tags = knowledgeShares[knowledgeIndex].tags.filter(tag => tag !== tagId);
    
    res.status(200).json(knowledgeShares[knowledgeIndex].tags);
  } catch (error) {
    res.status(500).json({ message: '删除标签失败', error: error.message });
  }
};

module.exports = {
  findAll,
  findOne,
  create,
  update,
  delete: deleteKnowledge,
  search,
  getVersions,
  revertToVersion,
  addComment,
  getComments,
  like,
  getTags,
  addTags,
  removeTag
}; 