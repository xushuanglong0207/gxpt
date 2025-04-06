import React, { useState, useEffect, useRef } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Space, 
  Input, 
  Tag, 
  Tooltip, 
  Modal, 
  Form, 
  Select, 
  InputNumber,
  Dropdown,
  Menu,
  Typography,
  message,
  DatePicker,
  Divider,
  Popconfirm,
  Row,
  Col,
  Upload,
  Skeleton,
  Empty,
  Alert,
  Drawer,
  Spin,
  Badge
} from 'antd';
import { 
  PlusOutlined, 
  SearchOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  CopyOutlined,
  ExportOutlined,
  MoreOutlined,
  TagOutlined,
  HistoryOutlined,
  PlayCircleOutlined,
  StopOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  UploadOutlined,
  DownloadOutlined,
  ExclamationCircleOutlined,
  FilterOutlined,
  FileTextOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  EyeOutlined,
  TeamOutlined,
  CloudUploadOutlined,
  BookOutlined
} from '@ant-design/icons';
import type { InputRef } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { FilterConfirmProps } from 'antd/es/table/interface';
import AppLayout from '@/components/layout/AppLayout';
import styled, { keyframes } from 'styled-components';
import { testCaseAPI } from '@/services/api';
import { useRouter } from 'next/router';
import Head from 'next/head';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

// 动画效果
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const shimmer = keyframes`
  0% { background-position: -468px 0; }
  100% { background-position: 468px 0; }
`;

// 样式组件
const PageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  animation: ${fadeIn} 0.5s ease-out;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const StyledCard = styled(Card)`
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  overflow: hidden;
  animation: ${fadeIn} 0.5s ease-out;

  .ant-card-head {
    background: #fafafa;
    border-bottom: 1px solid #f0f0f0;
  }
`;

const StyledTag = styled(Tag)`
  font-weight: 500;
  padding: 2px 10px;
  border-radius: 4px;
  transition: all 0.3s;
  
  &:hover {
    transform: scale(1.05);
  }
`;

const StyledTable = styled(Table)`
  .ant-table-thead > tr > th {
    background: #f7f7f7;
    font-weight: 500;
  }
  
  .ant-table-row {
    transition: all 0.3s;
    
    &:hover {
      background-color: #f8f8ff;
    }
  }
`;

const LoadingPlaceholder = styled.div`
  height: 20px;
  width: 100%;
  background: linear-gradient(to right, #f6f7f8 8%, #edeef1 18%, #f6f7f8 33%);
  background-size: 800px 100px;
  animation: ${shimmer} 2s infinite linear;
  border-radius: 4px;
  margin-bottom: 8px;
`;

const EmptyStateWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #8c8c8c;
`;

// 接口和类型
interface TestCase {
  id: string;
  title: string;
  steps: string;
  expectedResults: string;
  status: 'draft' | 'active' | 'completed' | 'archived';
  priority: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
  updatedAt: string;
  category?: string;
}

interface TestCaseModalProps {
  visible: boolean;
  onCancel: () => void;
  onSubmit: (values: Partial<TestCase>) => void;
  initialValues?: Partial<TestCase>;
  title: string;
  confirmLoading: boolean;
}

// 测试用例表单组件
const TestCaseModal: React.FC<TestCaseModalProps> = ({ 
  visible, 
  onCancel, 
  onSubmit, 
  initialValues,
  title,
  confirmLoading
}) => {
  const [form] = Form.useForm();
  
  useEffect(() => {
    if (visible && initialValues) {
      form.setFieldsValue(initialValues);
    } else if (visible) {
      form.resetFields();
    }
  }, [visible, initialValues, form]);
  
  const handleSubmit = () => {
    form.validateFields().then(values => {
      onSubmit(values);
    });
  };
  
  return (
    <Modal
      title={title}
      open={visible}
      onCancel={onCancel}
      width={700}
      onOk={handleSubmit}
      okText="保存"
      cancelText="取消"
      confirmLoading={confirmLoading}
      maskClosable={false}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={initialValues || { priority: 'medium', status: 'draft' }}
        requiredMark="optional"
      >
        <Form.Item
          name="title"
          label="标题"
          rules={[{ required: true, message: '请输入测试用例标题' }]}
        >
          <Input placeholder="请输入测试用例标题" />
        </Form.Item>
        
        <Form.Item
          name="steps"
          label="测试步骤"
          rules={[{ required: true, message: '请输入测试步骤' }]}
        >
          <TextArea 
            rows={4} 
            placeholder="请输入测试步骤，每个步骤一行" 
            autoSize={{ minRows: 4, maxRows: 8 }}
          />
        </Form.Item>
        
        <Form.Item
          name="expectedResults"
          label="预期结果"
          rules={[{ required: true, message: '请输入预期结果' }]}
        >
          <TextArea 
            rows={4} 
            placeholder="请输入预期结果，每个结果一行" 
            autoSize={{ minRows: 4, maxRows: 8 }}
          />
        </Form.Item>
        
        <Row gutter={24}>
          <Col span={12}>
            <Form.Item
              name="priority"
              label="优先级"
              rules={[{ required: true, message: '请选择优先级' }]}
            >
              <Select placeholder="选择优先级">
                <Option value="critical">
                  <Tag color="red">重要</Tag>
                </Option>
                <Option value="high">
                  <Tag color="orange">高</Tag>
                </Option>
                <Option value="medium">
                  <Tag color="blue">中</Tag>
                </Option>
                <Option value="low">
                  <Tag color="green">低</Tag>
                </Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="status"
              label="状态"
              rules={[{ required: true, message: '请选择状态' }]}
            >
              <Select placeholder="选择状态">
                <Option value="draft">
                  <Tag>草稿</Tag>
                </Option>
                <Option value="active">
                  <Tag color="processing">进行中</Tag>
                </Option>
                <Option value="completed">
                  <Tag color="success">已完成</Tag>
                </Option>
                <Option value="archived">
                  <Tag color="warning">已归档</Tag>
                </Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
  );
};

const TestCases: React.FC = () => {
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [searchedColumn, setSearchedColumn] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTestCase, setEditingTestCase] = useState<TestCase | null>(null);
  const [modalTitle, setModalTitle] = useState('创建测试用例');
  const [error, setError] = useState<string | null>(null);
  const searchInput = useRef<InputRef>(null);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [categories, setCategories] = useState<{ value: string; label: string; count: number }[]>([]);

  // 检查用户是否已登录
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      message.warning('请先登录');
      router.push('/login');
    }
  }, [router]);

  // 获取测试用例列表
  const fetchTestCases = async (page = 1, pageSize = 10, category?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const params: any = { page, limit: pageSize };
      
      if (category) {
        params.category = category;
      }
      
      // 模拟API调用
      setTimeout(() => {
        // 模拟数据
        const mockData: TestCase[] = Array.from({ length: 25 }, (_, index) => ({
          id: `${index + 1}`,
          title: `测试用例 ${index + 1}: 性能压测验证`,
          steps: `1. 准备测试环境\n2. 配置压测参数\n3. 运行测试\n4. 收集结果`,
          expectedResults: `1. 系统响应时间 < 200ms\n2. CPU使用率 < 80%\n3. 内存使用正常`,
          status: ['draft', 'active', 'completed', 'archived'][Math.floor(Math.random() * 4)] as any,
          priority: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)] as any,
          createdAt: new Date(Date.now() - Math.floor(Math.random() * 10000000000)).toISOString(),
          updatedAt: new Date(Date.now() - Math.floor(Math.random() * 1000000000)).toISOString()
        }));
        
        // 分页处理
        const startIdx = (page - 1) * pageSize;
        const endIdx = startIdx + pageSize;
        const paginatedData = mockData.slice(startIdx, endIdx);
        
        setTestCases(paginatedData);
        setPagination({
          ...pagination,
          current: page,
          total: mockData.length
        });
        setLoading(false);
      }, 1000);
      
      // 实际项目中使用真实API
      // const response = await testCaseAPI.getList({
      //   page,
      //   limit: pageSize
      // });
      // setTestCases(response.data.items);
      // setPagination({
      //   ...pagination,
      //   current: page,
      //   total: response.data.total
      // });
    } catch (error) {
      console.error('获取测试用例列表失败', error);
      setError('获取测试用例列表失败，请重试');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTestCases();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 表格搜索处理
  const handleSearch = (
    selectedKeys: string[],
    confirm: (param?: FilterConfirmProps) => void,
    dataIndex: string,
  ) => {
    confirm();
    setSearchText(selectedKeys[0]);
    setSearchedColumn(dataIndex);
  };

  const handleReset = (clearFilters: () => void) => {
    clearFilters();
    setSearchText('');
  };

  const getColumnSearchProps = (dataIndex: keyof TestCase) => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters, close }: any) => (
      <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
        <Input
          ref={searchInput}
          placeholder={`搜索 ${dataIndex}`}
          value={selectedKeys[0]}
          onChange={(e) => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => handleSearch(selectedKeys as string[], confirm, dataIndex as string)}
          style={{ marginBottom: 8, display: 'block' }}
        />
        <Space>
          <Button
            type="primary"
            onClick={() => handleSearch(selectedKeys as string[], confirm, dataIndex as string)}
            icon={<SearchOutlined />}
            size="small"
            style={{ width: 90 }}
          >
            搜索
          </Button>
          <Button
            onClick={() => clearFilters && handleReset(clearFilters)}
            size="small"
            style={{ width: 90 }}
          >
            重置
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => {
              close();
            }}
          >
            关闭
          </Button>
        </Space>
      </div>
    ),
    filterIcon: (filtered: boolean) => (
      <SearchOutlined style={{ color: filtered ? '#1890ff' : undefined }} />
    ),
    onFilter: (value: string, record: TestCase) =>
      record[dataIndex]
        .toString()
        .toLowerCase()
        .includes((value as string).toLowerCase()),
    onFilterDropdownOpenChange: (visible: boolean) => {
      if (visible) {
        setTimeout(() => searchInput.current?.select(), 100);
      }
    },
    render: (text: string) => (
      searchedColumn === dataIndex ? (
        <Tooltip title={text}>
          <span className="ellipsis">
            {text.toString().split('')
              .map((char, i) => {
                const isMatch = text
                  .toString()
                  .toLowerCase()
                  .includes(searchText.toLowerCase()) && 
                  searchText.toLowerCase().includes(char.toLowerCase());
                return isMatch ? <span key={i} style={{ color: '#1890ff' }}>{char}</span> : char;
              })}
          </span>
        </Tooltip>
      ) : (
        <Tooltip title={text}>
          <span className="ellipsis">{text}</span>
        </Tooltip>
      )
    )
  });
  
  // 处理表格变化
  const handleTableChange = (pagination: any) => {
    fetchTestCases(pagination.current, pagination.pageSize, selectedCategory === 'all' ? undefined : selectedCategory);
  };

  // 处理创建/编辑测试用例
  const handleSubmit = async (values: Partial<TestCase>) => {
    try {
      setSubmitting(true);
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      if (editingTestCase) {
        // 在实际项目中使用真实API
        // await testCaseAPI.update(editingTestCase.id, values);
        setTestCases(testCases.map(item => 
          item.id === editingTestCase.id ? { ...item, ...values } : item
        ));
        message.success('测试用例更新成功');
      } else {
        // 在实际项目中使用真实API
        // await testCaseAPI.create(values);
        const newTestCase: TestCase = {
          id: `${Date.now()}`,
          title: values.title || '',
          steps: values.steps || '',
          expectedResults: values.expectedResults || '',
          status: values.status as any || 'draft',
          priority: values.priority as any || 'medium',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
        setTestCases([newTestCase, ...testCases]);
        message.success('测试用例创建成功');
      }
      
      setModalVisible(false);
      setSubmitting(false);
      setEditingTestCase(null);
      
    } catch (error) {
      console.error('操作失败', error);
      message.error('操作失败，请重试');
      setSubmitting(false);
    }
  };

  // 处理删除测试用例
  const handleDelete = async (id: string) => {
    try {
      setLoading(true);
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 在实际项目中使用真实API
      // await testCaseAPI.delete(id);
      setTestCases(testCases.filter(item => item.id !== id));
      message.success('测试用例删除成功');
      setLoading(false);
      
    } catch (error) {
      console.error('删除失败', error);
      message.error('删除失败，请重试');
      setLoading(false);
    }
  };

  // 处理批量导入
  const handleBatchImport = async (file: File) => {
    try {
      message.loading({ content: '正在导入...', key: 'importLoading' });
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 在实际项目中使用真实API
      // const reader = new FileReader();
      // reader.onload = async (e) => {
      //   try {
      //     const content = e.target?.result;
      //     const data = JSON.parse(content as string);
      //     await testCaseAPI.batchImport(data);
      //     message.success('测试用例批量导入成功');
      //     fetchTestCases(1);
      //   } catch (error) {
      //     message.error('导入失败：文件格式错误');
      //     console.error(error);
      //   }
      // };
      // reader.readAsText(file);
      
      message.success({ content: '测试用例批量导入成功', key: 'importLoading' });
      fetchTestCases(1);
      return false;
      
    } catch (error) {
      message.error('导入失败');
      console.error(error);
      return false;
    }
  };

  // 处理导出测试用例
  const handleExport = async () => {
    try {
      message.loading({ content: '正在导出...', key: 'exportLoading' });
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 在实际项目中使用真实API
      // const response = await testCaseAPI.export();
      // const dataStr = JSON.stringify(response.data, null, 2);
      const dataStr = JSON.stringify(testCases, null, 2);
      const blob = new Blob([dataStr], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `test-cases-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success({ content: '导出成功', key: 'exportLoading' });
      
    } catch (error) {
      console.error('导出失败', error);
      message.error('导出失败，请重试');
    }
  };

  // 高级筛选
  const handleAdvancedFilter = () => {
    Modal.info({
      title: '高级筛选',
      content: (
        <Form layout="vertical">
          <Form.Item label="状态">
            <Select mode="multiple" placeholder="选择状态" style={{ width: '100%' }}>
              <Option value="draft">草稿</Option>
              <Option value="active">进行中</Option>
              <Option value="completed">已完成</Option>
              <Option value="archived">已归档</Option>
            </Select>
          </Form.Item>
          <Form.Item label="优先级">
            <Select mode="multiple" placeholder="选择优先级" style={{ width: '100%' }}>
              <Option value="critical">重要</Option>
              <Option value="high">高</Option>
              <Option value="medium">中</Option>
              <Option value="low">低</Option>
            </Select>
          </Form.Item>
          <Form.Item label="创建时间">
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      ),
      okText: '应用筛选',
      width: 500,
      icon: <FilterOutlined />,
      maskClosable: true,
    });
  };

  // 表格列定义
  const columns: ColumnsType<TestCase> = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: '20%',
      render: (text: string) => (
        <Tooltip title={text}>
          <div style={{ 
            maxWidth: '300px', 
            overflow: 'hidden', 
            textOverflow: 'ellipsis', 
            whiteSpace: 'nowrap',
            fontWeight: 500
          }}>
            {text}
          </div>
        </Tooltip>
      ),
      ...getColumnSearchProps('title'),
      sorter: (a, b) => a.title.localeCompare(b.title),
    },
    {
      title: '步骤',
      dataIndex: 'steps',
      key: 'steps',
      width: '22%',
      render: (text: string) => (
        <Tooltip title={text}>
          <div style={{ 
            maxWidth: '300px', 
            overflow: 'hidden', 
            textOverflow: 'ellipsis', 
            whiteSpace: 'nowrap' 
          }}>
            {text}
          </div>
        </Tooltip>
      ),
      ...getColumnSearchProps('steps'),
    },
    {
      title: '预期结果',
      dataIndex: 'expectedResults',
      key: 'expectedResults',
      width: '22%',
      render: (text: string) => (
        <Tooltip title={text}>
          <div style={{ 
            maxWidth: '300px', 
            overflow: 'hidden', 
            textOverflow: 'ellipsis', 
            whiteSpace: 'nowrap' 
          }}>
            {text}
          </div>
        </Tooltip>
      ),
      ...getColumnSearchProps('expectedResults'),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: '10%',
      render: (priority: string) => {
        const colorMap: {[key: string]: string} = {
          critical: 'red',
          high: 'orange',
          medium: 'blue',
          low: 'green'
        };
        const textMap: {[key: string]: string} = {
          critical: '重要',
          high: '高',
          medium: '中',
          low: '低'
        };
        return <StyledTag color={colorMap[priority]}>{textMap[priority]}</StyledTag>;
      },
      filters: [
        { text: '重要', value: 'critical' },
        { text: '高', value: 'high' },
        { text: '中', value: 'medium' },
        { text: '低', value: 'low' },
      ],
      onFilter: (value, record) => record.priority === value,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: '10%',
      render: (status: string) => {
        const colorMap: {[key: string]: string} = {
          draft: 'default',
          active: 'processing',
          completed: 'success',
          archived: 'warning'
        };
        const textMap: {[key: string]: string} = {
          draft: '草稿',
          active: '进行中',
          completed: '已完成',
          archived: '已归档'
        };
        return <StyledTag color={colorMap[status]}>{textMap[status]}</StyledTag>;
      },
      filters: [
        { text: '草稿', value: 'draft' },
        { text: '进行中', value: 'active' },
        { text: '已完成', value: 'completed' },
        { text: '已归档', value: 'archived' },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: '操作',
      key: 'action',
      width: '16%',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingTestCase(record);
              setModalTitle('编辑测试用例');
              setModalVisible(true);
            }}
            title="编辑"
          />
          <Popconfirm
            title="确定要删除这个测试用例吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
            icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
          >
            <Button type="text" danger icon={<DeleteOutlined />} title="删除" />
          </Popconfirm>
          <Button
            type="text"
            icon={<FileTextOutlined />}
            onClick={() => message.info('查看详情功能开发中')}
            title="查看详情"
          />
        </Space>
      )
    }
  ];

  const renderEmptyState = () => (
    <EmptyStateWrapper>
      <Empty 
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        description={<Text type="secondary">暂无测试用例数据</Text>} 
      />
      <Button 
        type="primary" 
        icon={<PlusOutlined />} 
        style={{ marginTop: 16 }}
        onClick={() => {
          setEditingTestCase(null);
          setModalTitle('创建测试用例');
          setModalVisible(true);
        }}
      >
        创建第一个测试用例
      </Button>
    </EmptyStateWrapper>
  );

  return (
    <AppLayout>
      <Head>
        <title>测试用例管理 - 性能测试管理系统</title>
      </Head>

      <div>
        <PageHeader>
          <div>
            <Title level={2}>测试用例管理</Title>
            <Paragraph style={{ fontSize: 16, marginBottom: 0 }}>
              创建、编辑和管理性能测试用例，支持批量操作和执行
            </Paragraph>
          </div>
          <ActionButtons>
            <Button 
              icon={<FilterOutlined />} 
              onClick={handleAdvancedFilter}
              disabled={loading}
            >
              高级筛选
            </Button>
            <Button 
              icon={<DownloadOutlined />} 
              onClick={handleExport}
              disabled={loading || testCases.length === 0}
            >
              导出
            </Button>
            <Upload
              accept=".json"
              showUploadList={false}
              beforeUpload={handleBatchImport}
              disabled={loading}
            >
              <Button 
                icon={<UploadOutlined />}
                disabled={loading}
              >
                批量导入
              </Button>
            </Upload>
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={() => {
                setEditingTestCase(null);
                setModalTitle('创建测试用例');
                setModalVisible(true);
              }}
              disabled={loading}
            >
              创建测试用例
            </Button>
          </ActionButtons>
        </PageHeader>
        
        {error && (
          <Alert 
            message="错误" 
            description={error} 
            type="error" 
            showIcon 
            closable 
            style={{ marginBottom: 16 }}
          />
        )}
        
        <StyledCard>
          {loading ? (
            <div style={{ padding: '20px 0' }}>
              <Skeleton active paragraph={{ rows: 10 }} />
            </div>
          ) : testCases.length === 0 ? (
            renderEmptyState()
          ) : (
            <StyledTable
              columns={columns}
              dataSource={testCases}
              rowKey="id"
              pagination={pagination}
              onChange={handleTableChange}
              loading={loading}
              scroll={{ x: 1000 }}
              rowClassName={() => 'test-case-row'}
              showSorterTooltip
            />
          )}
        </StyledCard>
        
        <TestCaseModal
          visible={modalVisible}
          onCancel={() => {
            setModalVisible(false);
            setEditingTestCase(null);
          }}
          onSubmit={handleSubmit}
          initialValues={editingTestCase || undefined}
          title={modalTitle}
          confirmLoading={submitting}
        />
      </div>
    </AppLayout>
  );
};

export default TestCases; 