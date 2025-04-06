const multer = require('multer');
const path = require('path');
const fs = require('fs');

// 确保上传目录存在
const uploadDir = path.join(__dirname, '../../uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// 配置存储
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    // 生成唯一文件名
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const extension = path.extname(file.originalname);
    cb(null, file.fieldname + '-' + uniqueSuffix + extension);
  }
});

// 文件过滤器
const fileFilter = (req, file, cb) => {
  const allowedExtensions = ['.csv'];
  const extension = path.extname(file.originalname).toLowerCase();
  
  // 检查是否为允许的文件类型
  if (allowedExtensions.includes(extension)) {
    cb(null, true);
  } else {
    cb(new Error('不支持的文件类型！只允许CSV文件。'), false);
  }
};

// 创建multer实例
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 限制为10MB
  },
  fileFilter: fileFilter
});

// 处理Multer错误的中间件
const handleMulterError = (err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        message: '文件太大，最大允许大小为10MB'
      });
    }
    return res.status(400).json({
      message: `上传文件错误: ${err.message}`
    });
  } else if (err) {
    return res.status(400).json({
      message: err.message
    });
  }
  next();
};

module.exports = {
  upload,
  handleMulterError,
  single: upload.single.bind(upload)
}; 