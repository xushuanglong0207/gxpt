// CSV数据控制器
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const csv = require('csv-parser');

// 模拟数据存储
let csvFiles = [];

// 获取所有CSV文件数据
const findAll = (req, res) => {
  try {
    res.status(200).json(csvFiles);
  } catch (error) {
    res.status(500).json({ message: '获取CSV文件列表失败', error: error.message });
  }
};

// 获取单个CSV文件详情
const findOne = (req, res) => {
  try {
    const id = req.params.id;
    const csvFile = csvFiles.find(file => file.id === id);
    
    if (!csvFile) {
      return res.status(404).json({ message: '找不到CSV文件' });
    }
    
    res.status(200).json(csvFile);
  } catch (error) {
    res.status(500).json({ message: '获取CSV文件详情失败', error: error.message });
  }
};

// 上传CSV文件
const upload = (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: '没有上传文件' });
    }
    
    const fileId = uuidv4();
    const fileName = req.file.originalname;
    const filePath = req.file.path;
    
    // 创建CSV文件记录
    const newCsvFile = {
      id: fileId,
      name: fileName,
      path: filePath,
      uploadDate: new Date().toISOString(),
      description: req.body.description || '',
    };
    
    csvFiles.push(newCsvFile);
    
    res.status(201).json({
      message: '文件上传成功',
      file: newCsvFile
    });
  } catch (error) {
    res.status(500).json({ message: '文件上传失败', error: error.message });
  }
};

// 导出CSV数据
const exportCsv = (req, res) => {
  try {
    const id = req.params.id;
    const csvFile = csvFiles.find(file => file.id === id);
    
    if (!csvFile) {
      return res.status(404).json({ message: '找不到CSV文件' });
    }
    
    res.download(csvFile.path, csvFile.name, (err) => {
      if (err) {
        res.status(500).json({ message: '文件下载失败', error: err.message });
      }
    });
  } catch (error) {
    res.status(500).json({ message: '导出CSV文件失败', error: error.message });
  }
};

// 删除CSV文件
const deleteFile = (req, res) => {
  try {
    const id = req.params.id;
    const fileIndex = csvFiles.findIndex(file => file.id === id);
    
    if (fileIndex === -1) {
      return res.status(404).json({ message: '找不到CSV文件' });
    }
    
    const filePath = csvFiles[fileIndex].path;
    
    // 从文件系统中删除文件
    fs.unlink(filePath, (err) => {
      if (err) {
        return res.status(500).json({ message: '文件删除失败', error: err.message });
      }
      
      // 从数组中移除文件记录
      csvFiles.splice(fileIndex, 1);
      
      res.status(200).json({ message: '文件删除成功' });
    });
  } catch (error) {
    res.status(500).json({ message: '删除CSV文件失败', error: error.message });
  }
};

// 更新CSV文件描述
const update = (req, res) => {
  try {
    const id = req.params.id;
    const { description } = req.body;
    
    const fileIndex = csvFiles.findIndex(file => file.id === id);
    
    if (fileIndex === -1) {
      return res.status(404).json({ message: '找不到CSV文件' });
    }
    
    // 更新描述
    csvFiles[fileIndex].description = description;
    
    res.status(200).json({
      message: '文件描述更新成功',
      file: csvFiles[fileIndex]
    });
  } catch (error) {
    res.status(500).json({ message: '更新CSV文件描述失败', error: error.message });
  }
};

// 获取CSV文件数据的统计信息
const getStats = (req, res) => {
  try {
    const id = req.params.id;
    const csvFile = csvFiles.find(file => file.id === id);
    
    if (!csvFile) {
      return res.status(404).json({ message: '找不到CSV文件' });
    }
    
    // 模拟统计信息
    const stats = {
      rowCount: 100, // 示例数据
      columnCount: 5,
      fileSize: '1.2 MB',
      // 其他统计信息...
    };
    
    res.status(200).json(stats);
  } catch (error) {
    res.status(500).json({ message: '获取CSV文件统计信息失败', error: error.message });
  }
};

module.exports = {
  findAll,
  findOne,
  upload,
  exportCsv,
  delete: deleteFile,
  update,
  getStats
}; 