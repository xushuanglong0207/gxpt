module.exports = (sequelize, Sequelize) => {
  const TestCase = sequelize.define("test_case", {
    id: {
      type: Sequelize.UUID,
      defaultValue: Sequelize.UUIDV4,
      primaryKey: true
    },
    title: {
      type: Sequelize.STRING,
      allowNull: false
    },
    steps: {
      type: Sequelize.TEXT,
      allowNull: false
    },
    expectedResults: {
      type: Sequelize.TEXT,
      allowNull: false
    },
    status: {
      type: Sequelize.ENUM('draft', 'active', 'completed', 'archived'),
      defaultValue: 'draft'
    },
    priority: {
      type: Sequelize.ENUM('low', 'medium', 'high', 'critical'),
      defaultValue: 'medium'
    },
    createdBy: {
      type: Sequelize.UUID,
      allowNull: false
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
    tableName: 'test_cases'
  });

  return TestCase;
}; 