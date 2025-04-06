import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Card, 
  Button, 
  List, 
  Space, 
  Tag, 
  Avatar, 
  Input, 
  Select,
  Row,
  Col,
  Divider,
  Tooltip,
  Badge,
  Modal,
  Form,
  message,
  Drawer,
  Spin,
  Tabs,
  Empty,
  Popconfirm,
  Menu
} from 'antd';
import { 
  FileTextOutlined, 
  UserOutlined, 
  FieldTimeOutlined, 
  EyeOutlined, 
  LikeOutlined, 
  MessageOutlined,
  ShareAltOutlined,
  SearchOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  BookOutlined,
  CalendarOutlined,
  FilterOutlined,
  TeamOutlined,
  TagOutlined,
  ClockCircleOutlined,
  LineChartOutlined,
  RobotOutlined,
  ApiOutlined,
  StarOutlined,
  ToolOutlined
} from '@ant-design/icons';
import AppLayout from '@/components/layout/AppLayout';
import styled from 'styled-components';
// ReactQuill编辑器组件
import dynamic from 'next/dynamic';
import Head from 'next/head';
import { useRouter } from 'next/router';

const ReactQuill = dynamic(() => import('react-quill'), { ssr: false });
import 'react-quill/dist/quill.snow.css';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

// 样式组件
const StyledCard = styled(Card)`
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
`;

const ArticleCard = styled(Card)`
  height: 100%;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .ant-card-cover {
    height: 180px;
    overflow: hidden;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  
  .ant-card-meta-title {
    margin-bottom: 8px;
  }
`;

const SearchHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
`;

const FilterContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
`;

interface IconTextProps {
  icon: React.ReactNode;
  text: string;
  color?: string;
}

const IconText: React.FC<IconTextProps> = ({ icon, text, color }) => (
  <Space>
    <span style={{ color }}>{icon}</span>
    <span>{text}</span>
  </Space>
);

// 接口和类型
interface Article {
  id: string;
  title: string;
  content: string;
  contentType: 'markdown' | 'html' | 'text';
  tags: string[];
  category: string;
  author: {
    id: string;
    name: string;
    avatar: string;
  };
  createdAt: string;
  updatedAt: string;
  viewCount: number;
  likeCount: number;
  isPublic: boolean;
}

interface TagItem {
  name: string;
  count: number;
}

interface ContributorItem {
  name: string;
  avatar: string;
  articles: number;
}

// 文章表单组件
interface ArticleFormProps {
  visible: boolean;
  onCancel: () => void;
  onSubmit: (article: Partial<Article>) => void;
  initialValues?: Partial<Article>;
  title: string;
  confirmLoading: boolean;
}

// 富文本编辑器配置
const editorModules = {
  toolbar: [
    [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
    ['bold', 'italic', 'underline', 'strike', 'blockquote'],
    [{ 'list': 'ordered' }, { 'list': 'bullet' }, { 'indent': '-1' }, { 'indent': '+1' }],
    ['link', 'image', 'code-block'],
    [{ 'color': [] }, { 'background': [] }],
    [{ 'align': [] }],
    ['clean']
  ],
};

const editorFormats = [
  'header',
  'bold', 'italic', 'underline', 'strike', 'blockquote',
  'list', 'bullet', 'indent',
  'link', 'image', 'code-block',
  'color', 'background',
  'align'
];

// 文章表单组件
const ArticleForm: React.FC<ArticleFormProps> = ({
  visible,
  onCancel,
  onSubmit,
  initialValues = {},
  title,
  confirmLoading
}) => {
  const [form] = Form.useForm();
  const [contentType, setContentType] = useState<'markdown' | 'html' | 'text'>(initialValues.contentType || 'html');
  const [content, setContent] = useState(initialValues.content || '');
  
  useEffect(() => {
    if (visible) {
      form.resetFields();
      if (initialValues) {
        form.setFieldsValue({
          ...initialValues,
          tags: initialValues.tags || []
        });
        setContent(initialValues.content || '');
        setContentType(initialValues.contentType || 'html');
      }
    }
  }, [visible, form, initialValues]);
  
  const handleSubmit = () => {
    form.validateFields().then(values => {
      onSubmit({
        ...values,
        content,
        contentType
      });
    });
  };
  
  const contentTypeOptions = [
    { label: 'HTML富文本', value: 'html' },
    { label: 'Markdown', value: 'markdown' },
    { label: '纯文本', value: 'text' }
  ];
  
  const renderEditor = () => {
    switch (contentType) {
      case 'markdown':
        return (
          <Input.TextArea
            value={content}
            onChange={e => setContent(e.target.value)}
            rows={15}
            placeholder="请输入Markdown格式内容..."
          />
        );
      case 'text':
        return (
          <Input.TextArea
            value={content}
            onChange={e => setContent(e.target.value)}
            rows={15}
            placeholder="请输入纯文本内容..."
          />
        );
      case 'html':
      default:
        return (
          <ReactQuill
            theme="snow"
            value={content}
            onChange={setContent}
            modules={editorModules}
            formats={editorFormats}
            placeholder="请输入富文本内容..."
          />
        );
    }
  };
  
  return (
    <Modal
      open={visible}
      title={title}
      onCancel={onCancel}
      onOk={handleSubmit}
      confirmLoading={confirmLoading}
      width={900}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          ...initialValues,
          contentType: initialValues.contentType || 'html',
          isPublic: initialValues.isPublic !== undefined ? initialValues.isPublic : true
        }}
      >
        <Form.Item
          name="title"
          label="文章标题"
          rules={[{ required: true, message: '请输入文章标题' }]}
        >
          <Input placeholder="请输入文章标题" />
        </Form.Item>
        
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="category"
              label="分类"
              rules={[{ required: true, message: '请选择分类' }]}
            >
              <Select placeholder="请选择分类">
                <Option value="performance">性能测试</Option>
                <Option value="automation">自动化测试</Option>
                <Option value="api">API测试</Option>
                <Option value="best-practices">最佳实践</Option>
                <Option value="tools">工具使用</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="contentType"
              label="内容格式"
              rules={[{ required: true, message: '请选择内容格式' }]}
            >
              <Select 
                placeholder="请选择内容格式" 
                onChange={(value) => setContentType(value as 'markdown' | 'html' | 'text')}
                options={contentTypeOptions}
              />
            </Form.Item>
          </Col>
        </Row>
        
        <Form.Item
          name="tags"
          label="标签"
        >
          <Select
            mode="tags"
            placeholder="请输入标签"
            style={{ width: '100%' }}
          >
            <Option value="性能">性能</Option>
            <Option value="压力测试">压力测试</Option>
            <Option value="自动化">自动化</Option>
            <Option value="API">API</Option>
            <Option value="最佳实践">最佳实践</Option>
            <Option value="教程">教程</Option>
          </Select>
        </Form.Item>
        
        <Form.Item
          name="isPublic"
          label="公开性"
          valuePropName="checked"
        >
          <Select defaultValue={true}>
            <Option value={true}>公开</Option>
            <Option value={false}>私有</Option>
          </Select>
        </Form.Item>
        
        <Divider orientation="left">文章内容</Divider>
        
        <EditorContainer>
          {renderEditor()}
        </EditorContainer>
      </Form>
    </Modal>
  );
};

// 文章预览组件
interface ArticlePreviewProps {
  visible: boolean;
  onClose: () => void;
  article: Article | null;
}

const ArticlePreview: React.FC<ArticlePreviewProps> = ({
  visible,
  onClose,
  article
}) => {
  if (!article) return null;
  
  const renderContent = () => {
    switch (article.contentType) {
      case 'markdown':
        return (
          <MarkdownPreview>
            {/* 实际项目中应使用markdown解析器如react-markdown */}
            <pre>{article.content}</pre>
          </MarkdownPreview>
        );
      case 'text':
        return (
          <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
            {article.content}
          </Paragraph>
        );
      case 'html':
      default:
        return (
          <div dangerouslySetInnerHTML={{ __html: article.content }} />
        );
    }
  };
  
  const handleShare = () => {
    // 实际项目中应调用分享API
    const url = `${window.location.origin}/knowledge/${article.id}`;
    navigator.clipboard.writeText(url).then(() => {
      message.success('文章链接已复制到剪贴板');
    }).catch(() => {
      message.error('无法复制链接，请手动复制');
    });
  };
  
  return (
    <Drawer
      title="文章预览"
      width={800}
      placement="right"
      onClose={onClose}
      open={visible}
      extra={
        <Space>
          <Button icon={<EditOutlined />} onClick={onClose}>编辑</Button>
          <Button type="primary" icon={<ShareAltOutlined />} onClick={handleShare}>
            分享
          </Button>
        </Space>
      }
    >
      <div>
        <Title level={2}>{article.title}</Title>
        
        <Space split={<Divider type="vertical" />} style={{ marginBottom: 16 }}>
          <Space>
            <Avatar size="small" src={article.author.avatar} />
            <Text>{article.author.name}</Text>
          </Space>
          <Space>
            <ClockCircleOutlined />
            <Text>{new Date(article.updatedAt).toLocaleDateString()}</Text>
          </Space>
          <Text type="secondary">
            <Space>
              <EyeOutlined />
              {article.viewCount}
            </Space>
          </Text>
        </Space>
        
        <TagsContainer>
          <Tag color="blue">{article.category}</Tag>
          {article.tags.map(tag => (
            <Tag key={tag}>{tag}</Tag>
          ))}
        </TagsContainer>
        
        <Divider />
        
        {renderContent()}
      </div>
    </Drawer>
  );
};

// 主组件
const KnowledgePage: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [formVisible, setFormVisible] = useState(false);
  const [formTitle, setFormTitle] = useState('创建文章');
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [editingArticle, setEditingArticle] = useState<Article | null>(null);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewArticle, setPreviewArticle] = useState<Article | null>(null);
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchValue, setSearchValue] = useState('');
  
  // 获取知识文章
  useEffect(() => {
    fetchArticles();
  }, []);
  
  // 获取文章列表
  const fetchArticles = async () => {
    setLoading(true);
    try {
      // 实际项目中应调用API
      // const response = await api.getArticles();
      // setArticles(response.articles);
      
      // 模拟API调用
      setTimeout(() => {
        const mockArticles: Article[] = [
          {
            id: '1',
            title: '性能测试最佳实践：优化响应时间',
            content: '<h2>如何优化API响应时间</h2><p>本文介绍了提高API性能的几种常见方法：</p><ul><li>使用缓存</li><li>优化数据库查询</li><li>使用异步处理</li><li>负载均衡</li></ul><p>接下来我们详细介绍每种方法...</p>',
            contentType: 'html',
            tags: ['性能', '最佳实践', 'API'],
            category: 'performance',
            author: {
              id: '101',
              name: '张工',
              avatar: 'https://randomuser.me/api/portraits/men/1.jpg'
            },
            createdAt: '2023-01-15T08:30:00.000Z',
            updatedAt: '2023-02-20T14:15:00.000Z',
            viewCount: 120,
            likeCount: 18,
            isPublic: true
          },
          {
            id: '2',
            title: '使用JMeter创建高效的压力测试',
            content: '# JMeter压力测试指南\n\n## 安装与配置\n\n首先，下载最新版JMeter...\n\n## 创建测试计划\n\n1. 添加线程组\n2. 配置HTTP请求\n3. 添加监听器\n\n## 运行测试\n\n使用以下命令行参数运行测试...',
            contentType: 'markdown',
            tags: ['JMeter', '压力测试', '工具'],
            category: 'tools',
            author: {
              id: '102',
              name: '李工',
              avatar: 'https://randomuser.me/api/portraits/women/1.jpg'
            },
            createdAt: '2023-03-10T10:45:00.000Z',
            updatedAt: '2023-03-12T16:20:00.000Z',
            viewCount: 85,
            likeCount: 12,
            isPublic: true
          },
          {
            id: '3',
            title: '自动化测试框架对比：Selenium vs Cypress',
            content: '<h2>主流自动化测试框架对比</h2><p>本文对比了Selenium和Cypress两个流行的前端自动化测试框架：</p><table><tr><th>特性</th><th>Selenium</th><th>Cypress</th></tr><tr><td>语言支持</td><td>多语言</td><td>JavaScript</td></tr><tr><td>浏览器支持</td><td>几乎所有</td><td>Chrome为主</td></tr><tr><td>安装复杂度</td><td>高</td><td>低</td></tr></table><p>详细对比...</p>',
            contentType: 'html',
            tags: ['自动化', 'Selenium', 'Cypress'],
            category: 'automation',
            author: {
              id: '103',
              name: '王工',
              avatar: 'https://randomuser.me/api/portraits/men/2.jpg'
            },
            createdAt: '2023-04-05T13:30:00.000Z',
            updatedAt: '2023-04-08T09:15:00.000Z',
            viewCount: 130,
            likeCount: 24,
            isPublic: true
          },
          {
            id: '4',
            title: 'RESTful API测试策略',
            content: 'API测试是软件测试中非常重要的一环。一个好的API测试策略应该包括：\n\n1. 功能测试：验证API的基本功能是否正常\n2. 性能测试：测试API在高负载下的表现\n3. 安全测试：检查API的安全漏洞\n4. 边界测试：测试边界条件和异常情况\n\n此外，应该使用自动化工具来提高测试效率...',
            contentType: 'text',
            tags: ['API', '测试策略'],
            category: 'api',
            author: {
              id: '104',
              name: '赵工',
              avatar: 'https://randomuser.me/api/portraits/women/2.jpg'
            },
            createdAt: '2023-05-22T08:45:00.000Z',
            updatedAt: '2023-05-25T11:30:00.000Z',
            viewCount: 78,
            likeCount: 15,
            isPublic: true
          },
        ];
        
        setArticles(mockArticles);
        setLoading(false);
      }, 800);
    } catch (error) {
      console.error('获取文章失败:', error);
      message.error('获取文章失败');
      setLoading(false);
    }
  };
  
  // 提交文章（创建或更新）
  const handleSubmit = async (article: Partial<Article>) => {
    setConfirmLoading(true);
    try {
      if (editingArticle) {
        // 更新文章
        // 实际项目中应调用API
        // await api.updateArticle(editingArticle.id, article);
        
        // 模拟API调用
        setTimeout(() => {
          const updatedArticles = articles.map(item => 
            item.id === editingArticle.id ? { ...item, ...article, updatedAt: new Date().toISOString() } : item
          );
          setArticles(updatedArticles);
          message.success('文章更新成功');
          setFormVisible(false);
          setEditingArticle(null);
          setConfirmLoading(false);
        }, 800);
      } else {
        // 创建文章
        // 实际项目中应调用API
        // const response = await api.createArticle(article);
        
        // 模拟API调用
        setTimeout(() => {
          // 获取用户信息
          const userData = localStorage.getItem('user');
          const user = userData ? JSON.parse(userData) : {
            id: '999',
            name: '测试用户',
            avatar: 'https://randomuser.me/api/portraits/men/1.jpg'
          };
          
          const newArticle: Article = {
            id: Date.now().toString(),
            title: article.title || '',
            content: article.content || '',
            contentType: article.contentType || 'html',
            tags: article.tags || [],
            category: article.category || 'performance',
            author: {
              id: user.id,
              name: user.name,
              avatar: user.avatar
            },
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            viewCount: 0,
            likeCount: 0,
            isPublic: article.isPublic !== undefined ? article.isPublic : true
          };
          
          setArticles([newArticle, ...articles]);
          message.success('文章创建成功');
          setFormVisible(false);
          setConfirmLoading(false);
        }, 800);
      }
    } catch (error) {
      console.error('保存文章失败:', error);
      message.error('保存文章失败');
      setConfirmLoading(false);
    }
  };
  
  // 删除文章
  const handleDelete = async (id: string) => {
    try {
      setLoading(true);
      // 实际项目中应调用API
      // await api.deleteArticle(id);
      
      // 模拟API调用
      setTimeout(() => {
        setArticles(articles.filter(item => item.id !== id));
        message.success('文章删除成功');
        setLoading(false);
      }, 800);
    } catch (error) {
      console.error('删除文章失败:', error);
      message.error('删除文章失败');
      setLoading(false);
    }
  };
  
  // 编辑文章
  const handleEdit = (article: Article) => {
    setEditingArticle(article);
    setFormTitle('编辑文章');
    setFormVisible(true);
  };
  
  // 预览文章
  const handlePreview = (article: Article) => {
    setPreviewArticle(article);
    setPreviewVisible(true);
  };
  
  // 新建文章
  const handleCreate = () => {
    setEditingArticle(null);
    setFormTitle('创建文章');
    setFormVisible(true);
  };
  
  // 过滤文章
  const filteredArticles = articles.filter(article => {
    // 分类过滤
    if (activeCategory !== 'all' && article.category !== activeCategory) {
      return false;
    }
    
    // 搜索过滤
    if (searchValue && !article.title.toLowerCase().includes(searchValue.toLowerCase())) {
      return false;
    }
    
    return true;
  });
  
  // 获取分类统计
  const getCategoryCount = (category: string) => {
    return category === 'all' 
      ? articles.length 
      : articles.filter(article => article.category === category).length;
  };
  
  // 分类选项
  const categories = [
    { value: 'all', label: '全部文章', icon: <BookOutlined /> },
    { value: 'performance', label: '性能测试', icon: <LineChartOutlined /> },
    { value: 'automation', label: '自动化测试', icon: <RobotOutlined /> },
    { value: 'api', label: 'API测试', icon: <ApiOutlined /> },
    { value: 'best-practices', label: '最佳实践', icon: <StarOutlined /> },
    { value: 'tools', label: '工具使用', icon: <ToolOutlined /> },
  ];

  return (
    <AppLayout>
      <Head>
        <title>知识分享 - 性能测试管理系统</title>
      </Head>
      
      <StyledCard>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>知识库</Title>
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={handleCreate}
          >
            创建文章
          </Button>
        </div>
        
        <Paragraph>
          知识库收集了团队成员分享的测试相关文章、教程和最佳实践，为团队提供宝贵的学习资源和参考。
        </Paragraph>
      </StyledCard>
      
      <Row gutter={24}>
        <Col xs={24} md={6}>
          <StyledCard>
            <Title level={5}>分类</Title>
            <Menu
              mode="inline"
              selectedKeys={[activeCategory]}
              items={categories.map(category => ({
                key: category.value,
                icon: category.icon,
                label: (
                  <Space>
                    <span>{category.label}</span>
                    <Tag color="blue">{getCategoryCount(category.value)}</Tag>
                  </Space>
                ),
                onClick: () => setActiveCategory(category.value)
              }))}
            />
          </StyledCard>
          
          <StyledCard>
            <Title level={5}>热门标签</Title>
            <TagsContainer>
              {Array.from(new Set(articles.flatMap(article => article.tags)))
                .slice(0, 20)
                .map(tag => (
                  <Tag 
                    key={tag} 
                    color="blue"
                    style={{ cursor: 'pointer', margin: '4px' }}
                    onClick={() => setSearchValue(tag)}
                  >
                    {tag}
                  </Tag>
                ))
              }
            </TagsContainer>
          </StyledCard>
        </Col>
        
        <Col xs={24} md={18}>
          <SearchContainer>
            <Search
              placeholder="搜索文章"
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              style={{ width: 300 }}
            />
            
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              创建文章
            </Button>
          </SearchContainer>
          
          {loading ? (
            <div style={{ textAlign: 'center', padding: '50px 0' }}>
              <Spin size="large" />
            </div>
          ) : filteredArticles.length === 0 ? (
            <Empty description="暂无文章" />
          ) : (
            <List
              grid={{
                gutter: 16,
                xs: 1,
                sm: 1,
                md: 2,
                lg: 3,
                xl: 3,
                xxl: 3,
              }}
              dataSource={filteredArticles}
              renderItem={(article) => (
                <List.Item>
                  <ArticleCard
                    hoverable
                    cover={
                      <div 
                        style={{ 
                          height: 120, 
                          background: `linear-gradient(135deg, ${getColorByCategory(article.category)})`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          padding: '0 16px',
                          color: 'white',
                          fontWeight: 'bold',
                          fontSize: 18
                        }}
                      >
                        {getCategoryLabel(article.category)}
                      </div>
                    }
                    actions={[
                      <Tooltip title="查看文章" key="view">
                        <EyeOutlined onClick={() => handlePreview(article)} />
                      </Tooltip>,
                      <Tooltip title="编辑文章" key="edit">
                        <EditOutlined onClick={() => handleEdit(article)} />
                      </Tooltip>,
                      <Tooltip title="删除文章" key="delete">
                        <Popconfirm
                          title="确定删除这篇文章吗?"
                          onConfirm={() => handleDelete(article.id)}
                          okText="确定"
                          cancelText="取消"
                        >
                          <DeleteOutlined />
                        </Popconfirm>
                      </Tooltip>,
                    ]}
                  >
                    <Card.Meta
                      title={
                        <Text 
                          strong 
                          ellipsis={{ tooltip: article.title }}
                          style={{ cursor: 'pointer' }}
                          onClick={() => handlePreview(article)}
                        >
                          {article.title}
                        </Text>
                      }
                      description={
                        <Space direction="vertical" size={4} style={{ width: '100%' }}>
                          <Space split={<Divider type="vertical" />} size={0}>
                            <Space size={4}>
                              <Avatar size="small" src={article.author.avatar} />
                              <Text type="secondary">{article.author.name}</Text>
                            </Space>
                            <Text type="secondary">
                              <ClockCircleOutlined style={{ marginRight: 4 }} />
                              {new Date(article.updatedAt).toLocaleDateString()}
                            </Text>
                          </Space>
                          
                          <Space size={[0, 4]} wrap>
                            {article.tags.slice(0, 3).map(tag => (
                              <Tag key={tag} style={{ margin: '2px' }}>{tag}</Tag>
                            ))}
                            {article.tags.length > 3 && (
                              <Tag>+{article.tags.length - 3}</Tag>
                            )}
                          </Space>
                        </Space>
                      }
                    />
                  </ArticleCard>
                </List.Item>
              )}
            />
          )}
        </Col>
      </Row>
      
      {/* 文章表单 */}
      <ArticleForm
        visible={formVisible}
        onCancel={() => setFormVisible(false)}
        onSubmit={handleSubmit}
        initialValues={editingArticle || {}}
        title={formTitle}
        confirmLoading={confirmLoading}
      />
      
      {/* 文章预览 */}
      <ArticlePreview
        visible={previewVisible}
        onClose={() => setPreviewVisible(false)}
        article={previewArticle}
      />
    </AppLayout>
  );
};

// 辅助函数：根据分类获取颜色
const getColorByCategory = (category: string) => {
  switch (category) {
    case 'performance':
      return '#1890ff, #096dd9';
    case 'automation':
      return '#52c41a, #389e0d';
    case 'api':
      return '#722ed1, #531dab';
    case 'best-practices':
      return '#fa8c16, #d46b08';
    case 'tools':
      return '#13c2c2, #08979c';
    default:
      return '#1890ff, #096dd9';
  }
};

// 辅助函数：获取分类标签
const getCategoryLabel = (category: string) => {
  switch (category) {
    case 'performance':
      return '性能测试';
    case 'automation':
      return '自动化测试';
    case 'api':
      return 'API测试';
    case 'best-practices':
      return '最佳实践';
    case 'tools':
      return '工具使用';
    default:
      return '其他';
  }
};

export default KnowledgePage; 