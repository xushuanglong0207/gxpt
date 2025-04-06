module.exports = (sequelize, Sequelize) => {
  const KnowledgeShare = sequelize.define("knowledge_share", {
    id: {
      type: Sequelize.UUID,
      defaultValue: Sequelize.UUIDV4,
      primaryKey: true
    },
    title: {
      type: Sequelize.STRING,
      allowNull: false
    },
    content: {
      type: Sequelize.TEXT('long'),
      allowNull: false
    },
    htmlContent: {
      type: Sequelize.TEXT('long'),
      allowNull: false
    },
    summary: {
      type: Sequelize.TEXT,
      allowNull: true
    },
    category: {
      type: Sequelize.STRING,
      allowNull: false
    },
    authorId: {
      type: Sequelize.UUID,
      allowNull: false
    },
    status: {
      type: Sequelize.ENUM('draft', 'published', 'archived'),
      defaultValue: 'draft'
    },
    viewCount: {
      type: Sequelize.INTEGER,
      defaultValue: 0
    },
    likeCount: {
      type: Sequelize.INTEGER,
      defaultValue: 0
    },
    version: {
      type: Sequelize.INTEGER,
      defaultValue: 1
    },
    versionHistory: {
      type: Sequelize.JSONB,
      defaultValue: []
    },
    createdAt: {
      type: Sequelize.DATE,
      defaultValue: Sequelize.NOW
    },
    updatedAt: {
      type: Sequelize.DATE,
      defaultValue: Sequelize.NOW
    }
  }, {
    timestamps: true,
    tableName: 'knowledge_shares'
  });

  return KnowledgeShare;
}; 