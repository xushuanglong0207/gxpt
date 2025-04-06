module.exports = (sequelize, Sequelize) => {
  const CsvData = sequelize.define("csv_data", {
    id: {
      type: Sequelize.UUID,
      defaultValue: Sequelize.UUIDV4,
      primaryKey: true
    },
    filename: {
      type: Sequelize.STRING,
      allowNull: false
    },
    originalName: {
      type: Sequelize.STRING,
      allowNull: false
    },
    description: {
      type: Sequelize.TEXT
    },
    data: {
      type: Sequelize.JSONB, // 存储解析后的CSV数据
      allowNull: false
    },
    headers: {
      type: Sequelize.ARRAY(Sequelize.STRING), // 存储CSV的列头
      allowNull: false
    },
    size: {
      type: Sequelize.INTEGER, // 文件大小（字节）
      allowNull: false
    },
    uploadedBy: {
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
    tableName: 'csv_data'
  });

  return CsvData;
}; 