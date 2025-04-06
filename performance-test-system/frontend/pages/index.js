import React from 'react';
import { Button, Typography, Layout, Space, Card, Statistic, Row, Col } from 'antd';
import { 
  DashboardOutlined, 
  FileTextOutlined, 
  UploadOutlined, 
  BookOutlined,
  UserOutlined
} from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { Content } = Layout;

export default function Home() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Content style={{ padding: '50px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <Typography>
            <Title>性能测试后台管理系统</Title>
            <Paragraph>
              欢迎使用性能测试后台管理系统，这是一个用于管理和分析性能测试数据的平台。
            </Paragraph>
          </Typography>

          <div style={{ marginTop: '40px', marginBottom: '40px' }}>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={8} lg={6}>
                <Card>
                  <Statistic 
                    title="测试用例" 
                    value={42} 
                    prefix={<FileTextOutlined />} 
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8} lg={6}>
                <Card>
                  <Statistic 
                    title="CSV数据文件" 
                    value={18} 
                    prefix={<UploadOutlined />} 
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8} lg={6}>
                <Card>
                  <Statistic 
                    title="知识分享" 
                    value={24} 
                    prefix={<BookOutlined />} 
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8} lg={6}>
                <Card>
                  <Statistic 
                    title="用户" 
                    value={8} 
                    prefix={<UserOutlined />} 
                  />
                </Card>
              </Col>
            </Row>
          </div>

          <Title level={2}>快速导航</Title>
          <Space size="large" wrap>
            <Button type="primary" size="large" icon={<DashboardOutlined />}>
              仪表盘
            </Button>
            <Button size="large" icon={<FileTextOutlined />}>
              测试用例
            </Button>
            <Button size="large" icon={<UploadOutlined />}>
              CSV数据
            </Button>
            <Button size="large" icon={<BookOutlined />}>
              知识分享
            </Button>
          </Space>

          <div style={{ marginTop: '60px' }}>
            <Title level={3}>系统功能</Title>
            <Row gutter={[16, 16]}>
              <Col xs={24} md={8}>
                <Card title="测试用例管理" style={{ height: '100%' }}>
                  <p>创建、编辑和管理性能测试用例，包括测试脚本、参数配置和执行计划。</p>
                </Card>
              </Col>
              <Col xs={24} md={8}>
                <Card title="CSV数据分析" style={{ height: '100%' }}>
                  <p>上传、处理和分析CSV格式的性能测试数据，生成可视化报表和趋势图。</p>
                </Card>
              </Col>
              <Col xs={24} md={8}>
                <Card title="知识分享平台" style={{ height: '100%' }}>
                  <p>分享性能测试经验、最佳实践和问题解决方案，促进团队协作和知识积累。</p>
                </Card>
              </Col>
            </Row>
          </div>
        </div>
      </Content>
    </Layout>
  );
} 