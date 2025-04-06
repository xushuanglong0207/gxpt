import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Card, 
  Upload, 
  Button, 
  Table, 
  message, 
  Space, 
  Tabs, 
  Spin, 
  Empty,
  Select,
  Row,
  Col,
  Tag,
  Divider,
  Alert,
  Drawer,
  Form
} from 'antd';
import { 
  UploadOutlined, 
  FileExcelOutlined, 
  DeleteOutlined, 
  LineChartOutlined,
  BarChartOutlined,
  PieChartOutlined,
  ReloadOutlined,
  LinkOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { useRouter } from 'next/router';
import styled from 'styled-components';
import AppLayout from '@/components/layout/AppLayout';
import Head from 'next/head';
import ReactECharts from 'echarts-for-react';
import type { UploadProps, UploadFile } from 'antd/es/upload/interface';
import { testCaseApi } from '@/services/api';
import type { TestCase } from '@/types/testCase';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

// 样式组件
const StyledCard = styled(Card)`
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
`;

const UploadArea = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  background-color: #fafafa;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  transition: all 0.3s;
  
  &:hover {
    border-color: #1890ff;
  }
`;

const ChartCard = styled(Card)`
  margin-top: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
`;

const StyledTable = styled(Table)`
  .ant-table-thead > tr > th {
    background: #f5f7fa;
  }
  
  .ant-table-tbody > tr:hover > td {
    background: #f0f5ff;
  }
`;

// CSV 数据类型
interface CSVData {
  id: string;
  testCaseId: string;
  fileName: string;
  columns: string[];
  data: any[];
  createdAt: string;
  updatedAt: string;
  description?: string;
}

// 图表配置类型
interface ChartConfig {
  type: 'line' | 'bar' | 'pie';
  title: string;
  xAxis?: string;
  yAxis?: string;
  seriesField?: string;
}

// 图表配置对话框组件
interface ChartConfigDrawerProps {
  visible: boolean;
  onClose: () => void;
  onSave: (config: ChartConfig) => void;
  columns: string[];
  initialConfig?: ChartConfig;
}

const ChartConfigDrawer: React.FC<ChartConfigDrawerProps> = ({
  visible,
  onClose,
  onSave,
  columns,
  initialConfig
}) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible && initialConfig) {
      form.setFieldsValue(initialConfig);
    }
  }, [visible, form, initialConfig]);

  const handleSubmit = () => {
    form.validateFields().then(values => {
      onSave(values);
      onClose();
    });
  };

  return (
    <Drawer
      title="图表配置"
      width={400}
      open={visible}
      onClose={onClose}
      extra={
        <Space>
          <Button onClick={onClose}>取消</Button>
          <Button type="primary" onClick={handleSubmit}>保存</Button>
        </Space>
      }
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={initialConfig || { type: 'line', title: '性能测试数据图表' }}
      >
        <Form.Item
          name="title"
          label="图表标题"
          rules={[{ required: true, message: '请输入图表标题' }]}
        >
          <Input placeholder="请输入图表标题" />
        </Form.Item>
        
        <Form.Item
          name="type"
          label="图表类型"
          rules={[{ required: true, message: '请选择图表类型' }]}
        >
          <Select placeholder="请选择图表类型">
            <Option value="line">折线图</Option>
            <Option value="bar">柱状图</Option>
            <Option value="pie">饼图</Option>
          </Select>
        </Form.Item>
        
        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) => prevValues.type !== currentValues.type}
        >
          {({ getFieldValue }) => {
            const chartType = getFieldValue('type');
            
            if (chartType === 'pie') {
              return (
                <>
                  <Form.Item
                    name="seriesField"
                    label="分类字段"
                    rules={[{ required: true, message: '请选择分类字段' }]}
                  >
                    <Select placeholder="请选择分类字段">
                      {columns.map(col => (
                        <Option key={col} value={col}>{col}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                  
                  <Form.Item
                    name="yAxis"
                    label="数值字段"
                    rules={[{ required: true, message: '请选择数值字段' }]}
                  >
                    <Select placeholder="请选择数值字段">
                      {columns.map(col => (
                        <Option key={col} value={col}>{col}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </>
              );
            }
            
            return (
              <>
                <Form.Item
                  name="xAxis"
                  label="X轴字段"
                  rules={[{ required: true, message: '请选择X轴字段' }]}
                >
                  <Select placeholder="请选择X轴字段">
                    {columns.map(col => (
                      <Option key={col} value={col}>{col}</Option>
                    ))}
                  </Select>
                </Form.Item>
                
                <Form.Item
                  name="yAxis"
                  label="Y轴字段"
                  rules={[{ required: true, message: '请选择Y轴字段' }]}
                >
                  <Select placeholder="请选择Y轴字段">
                    {columns.map(col => (
                      <Option key={col} value={col}>{col}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </>
            );
          }}
        </Form.Item>
      </Form>
    </Drawer>
  );
};

// 主组件
const CSVDataPage: React.FC = () => {
  const [csvData, setCsvData] = useState<CSVData | null>(null);
  const [loading, setLoading] = useState(false);
  const [tableLoading, setTableLoading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [testCase, setTestCase] = useState<TestCase | null>(null);
  const [testCaseLoading, setTestCaseLoading] = useState(false);
  const [chartConfig, setChartConfig] = useState<ChartConfig | null>(null);
  const [configDrawerVisible, setConfigDrawerVisible] = useState(false);
  
  const router = useRouter();
  const { testCaseId } = router.query;
  
  // 获取测试用例信息
  useEffect(() => {
    if (testCaseId) {
      fetchTestCase(testCaseId as string);
    }
  }, [testCaseId]);
  
  // 获取测试用例详情
  const fetchTestCase = async (id: string) => {
    setTestCaseLoading(true);
    try {
      // 实际项目中应调用API
      // const response = await testCaseApi.getById(id);
      // setTestCase(response.testCase);
      
      // 模拟API调用
      setTimeout(() => {
        const mockTestCase = {
          id,
          title: '高并发用户登录测试',
          steps: '1. 准备1000个测试账号\n2. 模拟1000个用户同时登录\n3. 监控系统响应时间和资源占用',
          expectedResults: '所有用户应在5秒内完成登录，CPU利用率不超过80%',
          status: 'active',
          priority: 'high',
          category: 'performance',
          createdAt: '2023-03-05T10:45:00.000Z',
          updatedAt: '2023-03-07T16:20:00.000Z'
        };
        
        setTestCase(mockTestCase);
        setTestCaseLoading(false);
      }, 800);
    } catch (error) {
      console.error('获取测试用例失败:', error);
      message.error('获取测试用例失败');
      setTestCaseLoading(false);
    }
  };
  
  // 上传文件前检查
  const beforeUpload = (file: File) => {
    const isCSV = file.type === 'text/csv' || file.name.endsWith('.csv');
    if (!isCSV) {
      message.error('请上传CSV文件');
      return false;
    }
    
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error('文件大小不能超过10MB');
      return false;
    }
    
    return true;
  };
  
  // 文件上传变化处理
  const handleUploadChange: UploadProps['onChange'] = (info) => {
    if (info.file.status === 'uploading') {
      setLoading(true);
      return;
    }
    
    if (info.file.status === 'done') {
      message.success(`${info.file.name} 上传成功`);
      parseCSV(info.file.originFileObj!);
    } else if (info.file.status === 'error') {
      message.error(`${info.file.name} 上传失败`);
      setLoading(false);
    }
    
    setFileList(info.fileList.slice(-1)); // 只保留最后一个文件
  };
  
  // 解析CSV文件
  const parseCSV = (file: File) => {
    setTableLoading(true);
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const csv = e.target?.result as string;
        const lines = csv.split('\n');
        const headers = lines[0].split(',').map(header => header.trim());
        
        const parsedData = [];
        for (let i = 1; i < lines.length; i++) {
          if (lines[i].trim() === '') continue;
          
          const values = lines[i].split(',').map(value => value.trim());
          const row: Record<string, any> = {};
          
          for (let j = 0; j < headers.length; j++) {
            // 尝试将数值转换为数字
            const value = values[j];
            const numValue = Number(value);
            row[headers[j]] = isNaN(numValue) ? value : numValue;
          }
          
          parsedData.push(row);
        }
        
        const newCsvData: CSVData = {
          id: Date.now().toString(),
          testCaseId: testCaseId as string || '',
          fileName: file.name,
          columns: headers,
          data: parsedData,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          description: ''
        };
        
        setCsvData(newCsvData);
        
        // 默认图表配置
        if (headers.length >= 2) {
          const numericColumns = headers.filter(header => 
            parsedData.some(row => typeof row[header] === 'number')
          );
          
          if (numericColumns.length > 0) {
            const nonNumericColumns = headers.filter(header => !numericColumns.includes(header));
            
            setChartConfig({
              type: 'line',
              title: `${testCase?.title || '性能测试'} - 数据图表`,
              xAxis: nonNumericColumns.length > 0 ? nonNumericColumns[0] : headers[0],
              yAxis: numericColumns[0],
              seriesField: nonNumericColumns.length > 1 ? nonNumericColumns[1] : undefined
            });
          }
        }
        
        setLoading(false);
        setTableLoading(false);
      } catch (error) {
        console.error('解析CSV文件失败:', error);
        message.error('解析CSV文件失败，请检查文件格式');
        setLoading(false);
        setTableLoading(false);
      }
    };
    
    reader.onerror = () => {
      message.error('读取文件失败');
      setLoading(false);
      setTableLoading(false);
    };
    
    reader.readAsText(file);
  };
  
  // 保存图表配置
  const saveChartConfig = (config: ChartConfig) => {
    setChartConfig(config);
    message.success('图表配置已保存');
  };
  
  // 生成图表配置
  const getChartOption = () => {
    if (!csvData || !chartConfig) return {};
    
    const { data, columns } = csvData;
    const { type, title, xAxis, yAxis, seriesField } = chartConfig;
    
    if (type === 'pie') {
      const pieData = data.map(item => ({
        name: String(item[seriesField!]),
        value: Number(item[yAxis!])
      }));
      
      return {
        title: {
          text: title,
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: pieData.map(item => item.name)
        },
        series: [
          {
            name: yAxis,
            type: 'pie',
            radius: '50%',
            data: pieData,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };
    }
    
    // 折线图或柱状图
    const categories = [...new Set(data.map(item => item[xAxis!]))];
    
    let series = [];
    if (seriesField) {
      const seriesNames = [...new Set(data.map(item => item[seriesField]))];
      
      series = seriesNames.map(name => {
        const seriesData = categories.map(category => {
          const item = data.find(d => d[xAxis!] === category && d[seriesField] === name);
          return item ? item[yAxis!] : 0;
        });
        
        return {
          name: String(name),
          type: type,
          data: seriesData
        };
      });
    } else {
      const seriesData = categories.map(category => {
        const item = data.find(d => d[xAxis!] === category);
        return item ? item[yAxis!] : 0;
      });
      
      series = [
        {
          name: yAxis,
          type: type,
          data: seriesData
        }
      ];
    }
    
    return {
      title: {
        text: title,
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: seriesField ? [...new Set(data.map(item => item[seriesField]))] : [yAxis],
        bottom: 10
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: categories,
        name: xAxis
      },
      yAxis: {
        type: 'value',
        name: yAxis
      },
      series
    };
  };
  
  // 生成表格列
  const generateColumns = () => {
    if (!csvData) return [];
    
    return csvData.columns.map(column => ({
      title: column,
      dataIndex: column,
      key: column,
      sorter: (a: any, b: any) => {
        if (typeof a[column] === 'number') {
          return a[column] - b[column];
        }
        return String(a[column]).localeCompare(String(b[column]));
      }
    }));
  };
  
  // 渲染测试用例信息
  const renderTestCaseInfo = () => {
    if (testCaseLoading) {
      return (
        <Card style={{ marginBottom: 24 }}>
          <Spin />
        </Card>
      );
    }
    
    if (!testCase) {
      return (
        <Alert
          message="未关联测试用例"
          description="当前CSV数据未关联到任何测试用例，请先选择或创建一个测试用例。"
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
          action={
            <Button 
              type="primary" 
              size="small" 
              onClick={() => router.push('/test-cases')}
            >
              选择测试用例
            </Button>
          }
        />
      );
    }
    
    return (
      <StyledCard>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <Title level={4} style={{ marginBottom: 8 }}>{testCase.title}</Title>
              <Space split={<Divider type="vertical" />}>
                <Text type="secondary">ID: {testCase.id}</Text>
                {testCase.priority === 'critical' && <Tag color="red">紧急</Tag>}
                {testCase.priority === 'high' && <Tag color="orange">高</Tag>}
                {testCase.priority === 'medium' && <Tag color="blue">中</Tag>}
                {testCase.priority === 'low' && <Tag color="green">低</Tag>}
                
                {testCase.status === 'draft' && <Tag color="default">草稿</Tag>}
                {testCase.status === 'active' && <Tag color="processing">进行中</Tag>}
                {testCase.status === 'completed' && <Tag color="success">已完成</Tag>}
                {testCase.status === 'archived' && <Tag color="warning">已归档</Tag>}
              </Space>
            </div>
            <Button 
              type="link" 
              icon={<LinkOutlined />}
              onClick={() => router.push(`/test-cases/${testCase.id}`)}
            >
              查看详情
            </Button>
          </div>
          
          <Row gutter={24} style={{ marginTop: 16 }}>
            <Col span={12}>
              <Title level={5}>测试步骤</Title>
              <Paragraph ellipsis={{ rows: 3, expandable: true, symbol: '展开' }}>
                {testCase.steps}
              </Paragraph>
            </Col>
            <Col span={12}>
              <Title level={5}>预期结果</Title>
              <Paragraph ellipsis={{ rows: 3, expandable: true, symbol: '展开' }}>
                {testCase.expectedResults}
              </Paragraph>
            </Col>
          </Row>
        </Space>
      </StyledCard>
    );
  };
  
  // 渲染上传区域
  const renderUploadArea = () => (
    <StyledCard>
      <Title level={4}>上传CSV数据</Title>
      <UploadArea>
        <Upload.Dragger
          name="file"
          accept=".csv"
          maxCount={1}
          fileList={fileList}
          beforeUpload={beforeUpload}
          onChange={handleUploadChange}
          customRequest={({ file, onSuccess }) => {
            setTimeout(() => {
              onSuccess?.('ok');
            }, 0);
          }}
        >
          <p className="ant-upload-drag-icon">
            <FileExcelOutlined style={{ fontSize: 48, color: '#1890ff' }} />
          </p>
          <p className="ant-upload-text">点击或拖拽上传CSV文件</p>
          <p className="ant-upload-hint">
            支持单个CSV文件上传，文件大小不超过10MB
          </p>
        </Upload.Dragger>
      </UploadArea>
    </StyledCard>
  );
  
  // 渲染表格
  const renderTable = () => {
    if (!csvData) return null;
    
    return (
      <StyledCard>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4}>CSV数据预览</Title>
          <Space>
            <Button 
              icon={<DownloadOutlined />}
              onClick={() => message.info('下载功能开发中')}
            >
              导出数据
            </Button>
            <Button 
              icon={<DeleteOutlined />}
              onClick={() => {
                setCsvData(null);
                setFileList([]);
                setChartConfig(null);
              }}
            >
              清除数据
            </Button>
          </Space>
        </div>
        <StyledTable
          columns={generateColumns()}
          dataSource={csvData.data.map((item, index) => ({ ...item, key: index }))}
          scroll={{ x: 'max-content' }}
          loading={tableLoading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
        />
      </StyledCard>
    );
  };
  
  // 渲染图表
  const renderChart = () => {
    if (!csvData || !chartConfig) return null;
    
    return (
      <ChartCard>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4}>数据可视化</Title>
          <Space>
            <Select
              value={chartConfig.type}
              onChange={(value) => setChartConfig({ ...chartConfig, type: value as 'line' | 'bar' | 'pie' })}
              style={{ width: 120 }}
            >
              <Option value="line">折线图</Option>
              <Option value="bar">柱状图</Option>
              <Option value="pie">饼图</Option>
            </Select>
            <Button 
              icon={<SettingOutlined />}
              onClick={() => setConfigDrawerVisible(true)}
            >
              图表配置
            </Button>
          </Space>
        </div>
        <ReactECharts 
          option={getChartOption()} 
          style={{ height: 400 }} 
          notMerge={true}
          lazyUpdate={true}
        />
      </ChartCard>
    );
  };
  
  // 渲染空状态
  const renderEmptyState = () => (
    <Empty
      image={Empty.PRESENTED_IMAGE_SIMPLE}
      description="暂无数据，请上传CSV文件"
    />
  );
  
  return (
    <AppLayout>
      <Head>
        <title>CSV数据分析 - 性能测试管理系统</title>
      </Head>
      
      {renderTestCaseInfo()}
      
      {renderUploadArea()}
      
      {csvData ? (
        <>
          {renderTable()}
          {renderChart()}
        </>
      ) : (
        renderEmptyState()
      )}
      
      <ChartConfigDrawer
        visible={configDrawerVisible}
        onClose={() => setConfigDrawerVisible(false)}
        onSave={saveChartConfig}
        columns={csvData?.columns || []}
        initialConfig={chartConfig || undefined}
      />
    </AppLayout>
  );
};

export default CSVDataPage; 