const { Sequelize } = require('sequelize');
const dotenv = require('dotenv');

dotenv.config();

// 创建数据库连接
const sequelize = new Sequelize(
  process.env.DB_NAME || 'performance_test_system',
  process.env.DB_USER || 'postgres',
  process.env.DB_PASSWORD || 'postgres',
  {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    dialect: 'postgres',
    logging: process.env.NODE_ENV === 'development' ? console.log : false,
    pool: {
      max: 5,
      min: 0,
      acquire: 30000,
      idle: 10000
    }
  }
);

// 导入模型
const TestCase = require('./testCase.model')(sequelize, Sequelize);
const CsvData = require('./csvData.model')(sequelize, Sequelize);
const KnowledgeShare = require('./knowledgeShare.model')(sequelize, Sequelize);
const User = require('./user.model')(sequelize, Sequelize);
const Tag = require('./tag.model')(sequelize, Sequelize);
const Comment = require('./comment.model')(sequelize, Sequelize);

// 模型关联
User.hasMany(TestCase, { as: 'testCases', foreignKey: 'createdBy' });
TestCase.belongsTo(User, { as: 'creator', foreignKey: 'createdBy' });

User.hasMany(CsvData, { as: 'csvFiles', foreignKey: 'uploadedBy' });
CsvData.belongsTo(User, { as: 'uploader', foreignKey: 'uploadedBy' });

User.hasMany(KnowledgeShare, { as: 'knowledgeShares', foreignKey: 'authorId' });
KnowledgeShare.belongsTo(User, { as: 'author', foreignKey: 'authorId' });

KnowledgeShare.belongsToMany(Tag, { through: 'KnowledgeTag', as: 'tags' });
Tag.belongsToMany(KnowledgeShare, { through: 'KnowledgeTag', as: 'knowledgeShares' });

User.hasMany(Comment, { as: 'comments', foreignKey: 'userId' });
Comment.belongsTo(User, { as: 'user', foreignKey: 'userId' });

KnowledgeShare.hasMany(Comment, { as: 'comments', foreignKey: 'knowledgeId' });
Comment.belongsTo(KnowledgeShare, { as: 'knowledge', foreignKey: 'knowledgeId' });

// 导出模型和Sequelize实例
module.exports = {
  sequelize,
  Sequelize,
  TestCase,
  CsvData,
  KnowledgeShare,
  User,
  Tag,
  Comment
}; 