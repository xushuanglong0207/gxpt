import React, { useState, useEffect } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  Table, 
  Tag, 
  Progress, 
  Typography,
  DatePicker,
  Select,
  Divider,
  Button,
  Tooltip
} from 'antd';
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined, 
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  CloudDownloadOutlined,
  FilterOutlined,
  SyncOutlined,
  AreaChartOutlined
} from '@ant-design/icons';
import AppLayout from '@/components/layout/AppLayout';
import styled from 'styled-components';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

// 样式组件
const StyledCard = styled(Card)`
  height: 100%;
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16), 0 3px 6px 0 rgba(0, 0, 0, 0.12);
  border-radius: 8px;
`;

const StyledStatisticCard = styled(StyledCard)`
  &.positive {
    .ant-statistic-content-value {
      color: #52c41a;
    }
  }
  
  &.negative {
    .ant-statistic-content-value {
      color: #f5222d;
    }
  }
  
  &.neutral {
    .ant-statistic-content-value {
      color: #1890ff;
    }
  }
`;

const FilterBar = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16), 0 3px 6px 0 rgba(0, 0, 0, 0.12);
`;

// 模拟数据
const mockPerformanceData = {
  summary: {
    avgResponseTime: 245,
    avgResponseTimeTrend: -12,
    throughput: 1250,
    throughputTrend: 8,
    errorRate: 1.8,
    errorRateTrend: -0.5,
    concurrentUsers: 350,
    concurrentUsersTrend: 25
  },
  recentTests: [
    { 
      id: 1, 
      name: 'API压力测试 - 用户登录', 
      date: '2023-11-15', 
      status: 'success', 
      avgResponseTime: 220,
      throughput: 1300,
      errorRate: 0.5,
      duration: '25分钟'
    },
    { 
      id: 2, 
      name: '数据库性能基准测试', 
      date: '2023-11-14', 
      status: 'warning', 
      avgResponseTime: 320,
      throughput: 950,
      errorRate: 2.1,
      duration: '40分钟'
    },
    { 
      id: 3, 
      name: '前端加载性能测试', 
      date: '2023-11-12', 
      status: 'success', 
      avgResponseTime: 180,
      throughput: 1450,
      errorRate: 0.8,
      duration: '15分钟'
    },
    { 
      id: 4, 
      name: '微服务协同压力测试', 
      date: '2023-11-10', 
      status: 'error', 
      avgResponseTime: 420,
      throughput: 780,
      errorRate: 5.2,
      duration: '60分钟'
    },
    { 
      id: 5, 
      name: 'CDN内容分发性能测试', 
      date: '2023-11-08', 
      status: 'success', 
      avgResponseTime: 85,
      throughput: 2100,
      errorRate: 0.3,
      duration: '30分钟'
    }
  ]
};

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState([dayjs().subtract(7, 'day'), dayjs()]);
  const [testType, setTestType] = useState('all');
  
  // 模拟加载数据
  useEffect(() => {
    setTimeout(() => {
      setLoading(false);
    }, 1500);
  }, []);
  
  // 图表配置 - 响应时间趋势
  const getResponseTimeChartOption = () => {
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#6a7985'
          }
        }
      },
      legend: {
        data: ['平均响应时间', '95%响应时间', '最大响应时间']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: [
        {
          type: 'category',
          boundaryGap: false,
          data: ['11/08', '11/09', '11/10', '11/11', '11/12', '11/13', '11/14', '11/15']
        }
      ],
      yAxis: [
        {
          type: 'value',
          name: '响应时间(ms)',
          axisLabel: {
            formatter: '{value} ms'
          }
        }
      ],
      series: [
        {
          name: '平均响应时间',
          type: 'line',
          smooth: true,
          emphasis: {
            focus: 'series'
          },
          lineStyle: {
            width: 3,
            shadowColor: 'rgba(0,0,0,0.2)',
            shadowBlur: 10
          },
          data: [280, 265, 310, 290, 270, 260, 255, 245]
        },
        {
          name: '95%响应时间',
          type: 'line',
          smooth: true,
          emphasis: {
            focus: 'series'
          },
          data: [480, 460, 520, 500, 470, 460, 455, 430]
        },
        {
          name: '最大响应时间',
          type: 'line',
          smooth: true,
          emphasis: {
            focus: 'series'
          },
          data: [820, 790, 910, 870, 800, 780, 760, 700]
        }
      ]
    };
  };
  
  // 图表配置 - 吞吐量与错误率
  const getThroughputChartOption = () => {
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          crossStyle: {
            color: '#999'
          }
        }
      },
      legend: {
        data: ['吞吐量', '错误率']
      },
      xAxis: [
        {
          type: 'category',
          data: ['11/08', '11/09', '11/10', '11/11', '11/12', '11/13', '11/14', '11/15'],
          axisPointer: {
            type: 'shadow'
          }
        }
      ],
      yAxis: [
        {
          type: 'value',
          name: '吞吐量(请求/秒)',
          min: 0,
          max: 2000,
          interval: 500,
          axisLabel: {
            formatter: '{value}'
          }
        },
        {
          type: 'value',
          name: '错误率(%)',
          min: 0,
          max: 10,
          interval: 2,
          axisLabel: {
            formatter: '{value}%'
          }
        }
      ],
      series: [
        {
          name: '吞吐量',
          type: 'bar',
          barWidth: '40%',
          emphasis: {
            focus: 'series'
          },
          data: [1100, 1180, 1220, 1190, 1210, 1230, 1240, 1250]
        },
        {
          name: '错误率',
          type: 'line',
          yAxisIndex: 1,
          emphasis: {
            focus: 'series'
          },
          itemStyle: {
            color: '#f5222d'
          },
          data: [2.8, 2.5, 2.3, 2.2, 2.0, 1.9, 1.8, 1.8]
        }
      ]
    };
  };
  
  // 表格列配置
  const columns = [
    {
      title: '测试名称',
      dataIndex: 'name',
      key: 'name',
      render: (text) => <a>{text}</a>,
    },
    {
      title: '执行日期',
      dataIndex: 'date',
      key: 'date',
      sorter: (a, b) => new Date(a.date) - new Date(b.date),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        let color = 'green';
        let icon = <CheckCircleOutlined />;
        let text = '成功';
        
        if (status === 'warning') {
          color = 'orange';
          icon = <WarningOutlined />;
          text = '警告';
        } else if (status === 'error') {
          color = 'red';
          icon = <CloseCircleOutlined />;
          text = '失败';
        }
        
        return (
          <Tag color={color} icon={icon}>
            {text}
          </Tag>
        );
      },
      filters: [
        { text: '成功', value: 'success' },
        { text: '警告', value: 'warning' },
        { text: '失败', value: 'error' },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: '平均响应时间',
      dataIndex: 'avgResponseTime',
      key: 'avgResponseTime',
      sorter: (a, b) => a.avgResponseTime - b.avgResponseTime,
      render: (time) => `${time} ms`,
    },
    {
      title: '吞吐量',
      dataIndex: 'throughput',
      key: 'throughput',
      sorter: (a, b) => a.throughput - b.throughput,
      render: (throughput) => `${throughput} 请求/秒`,
    },
    {
      title: '错误率',
      dataIndex: 'errorRate',
      key: 'errorRate',
      sorter: (a, b) => a.errorRate - b.errorRate,
      render: (rate) => `${rate}%`,
    },
    {
      title: '执行时长',
      dataIndex: 'duration',
      key: 'duration',
    },
    {
      title: '操作',
      key: 'action',
      render: () => (
        <span>
          <Tooltip title="查看详情">
            <Button 
              type="link" 
              icon={<AreaChartOutlined />} 
              style={{ marginRight: 8 }}
            />
          </Tooltip>
          <Tooltip title="下载报告">
            <Button 
              type="link" 
              icon={<CloudDownloadOutlined />} 
            />
          </Tooltip>
        </span>
      ),
    },
  ];

  return (
    <AppLayout>
      <div className="slide-up">
        <Title level={2}>性能测试仪表盘</Title>
        <Text style={{ fontSize: 16, marginBottom: 24, display: 'block' }}>
          实时监控系统性能指标，分析测试结果，发现潜在问题
        </Text>
        
        <FilterBar>
          <div>
            <Text strong style={{ marginRight: 8 }}>日期范围:</Text>
            <RangePicker 
              value={timeRange} 
              onChange={(dates) => setTimeRange(dates)} 
              allowClear={false}
            />
          </div>
          <div>
            <Text strong style={{ marginRight: 8 }}>测试类型:</Text>
            <Select 
              defaultValue="all" 
              style={{ width: 180 }} 
              onChange={(value) => setTestType(value)}
            >
              <Option value="all">全部测试</Option>
              <Option value="api">API测试</Option>
              <Option value="database">数据库测试</Option>
              <Option value="frontend">前端测试</Option>
              <Option value="microservice">微服务测试</Option>
            </Select>
          </div>
          <div style={{ marginLeft: 'auto' }}>
            <Button 
              type="primary" 
              icon={<SyncOutlined />}
              loading={loading}
            >
              刷新数据
            </Button>
          </div>
        </FilterBar>
        
        <Row gutter={[24, 24]}>
          <Col xs={24} sm={12} md={6}>
            <StyledStatisticCard 
              className="positive" 
              loading={loading}
            >
              <Statistic
                title="平均响应时间"
                value={mockPerformanceData.summary.avgResponseTime}
                precision={0}
                valueStyle={{ color: '#1890ff' }}
                prefix={<span></span>}
                suffix="ms"
              />
              <div>
                {mockPerformanceData.summary.avgResponseTimeTrend < 0 ? (
                  <Text type="success">
                    <ArrowDownOutlined /> {Math.abs(mockPerformanceData.summary.avgResponseTimeTrend)}ms
                  </Text>
                ) : (
                  <Text type="danger">
                    <ArrowUpOutlined /> {mockPerformanceData.summary.avgResponseTimeTrend}ms
                  </Text>
                )}
                <Text type="secondary" style={{ marginLeft: 8 }}>与昨日相比</Text>
              </div>
            </StyledStatisticCard>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <StyledStatisticCard 
              className="positive" 
              loading={loading}
            >
              <Statistic
                title="吞吐量"
                value={mockPerformanceData.summary.throughput}
                precision={0}
                valueStyle={{ color: '#1890ff' }}
                suffix="请求/秒"
              />
              <div>
                {mockPerformanceData.summary.throughputTrend > 0 ? (
                  <Text type="success">
                    <ArrowUpOutlined /> {mockPerformanceData.summary.throughputTrend}
                  </Text>
                ) : (
                  <Text type="danger">
                    <ArrowDownOutlined /> {Math.abs(mockPerformanceData.summary.throughputTrend)}
                  </Text>
                )}
                <Text type="secondary" style={{ marginLeft: 8 }}>与昨日相比</Text>
              </div>
            </StyledStatisticCard>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <StyledStatisticCard 
              className="positive" 
              loading={loading}
            >
              <Statistic
                title="错误率"
                value={mockPerformanceData.summary.errorRate}
                precision={1}
                valueStyle={{ color: mockPerformanceData.summary.errorRate > 2 ? '#f5222d' : '#1890ff' }}
                suffix="%"
              />
              <div>
                {mockPerformanceData.summary.errorRateTrend < 0 ? (
                  <Text type="success">
                    <ArrowDownOutlined /> {Math.abs(mockPerformanceData.summary.errorRateTrend)}%
                  </Text>
                ) : (
                  <Text type="danger">
                    <ArrowUpOutlined /> {mockPerformanceData.summary.errorRateTrend}%
                  </Text>
                )}
                <Text type="secondary" style={{ marginLeft: 8 }}>与昨日相比</Text>
              </div>
            </StyledStatisticCard>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <StyledStatisticCard 
              className="neutral" 
              loading={loading}
            >
              <Statistic
                title="并发用户数"
                value={mockPerformanceData.summary.concurrentUsers}
                precision={0}
                valueStyle={{ color: '#1890ff' }}
                suffix="用户"
              />
              <div>
                {mockPerformanceData.summary.concurrentUsersTrend > 0 ? (
                  <Text type="success">
                    <ArrowUpOutlined /> {mockPerformanceData.summary.concurrentUsersTrend}
                  </Text>
                ) : (
                  <Text type="danger">
                    <ArrowDownOutlined /> {Math.abs(mockPerformanceData.summary.concurrentUsersTrend)}
                  </Text>
                )}
                <Text type="secondary" style={{ marginLeft: 8 }}>与昨日相比</Text>
              </div>
            </StyledStatisticCard>
          </Col>
        </Row>
        
        <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
          <Col xs={24} lg={12}>
            <StyledCard 
              title="响应时间趋势"
              loading={loading}
            >
              <ReactECharts 
                option={getResponseTimeChartOption()} 
                style={{ height: 350 }}
              />
            </StyledCard>
          </Col>
          <Col xs={24} lg={12}>
            <StyledCard 
              title="吞吐量与错误率"
              loading={loading}
            >
              <ReactECharts 
                option={getThroughputChartOption()} 
                style={{ height: 350 }}
              />
            </StyledCard>
          </Col>
        </Row>
        
        <div style={{ marginTop: 24 }}>
          <StyledCard 
            title="最近测试执行"
            loading={loading}
            extra={
              <Button 
                type="primary" 
                icon={<CloudDownloadOutlined />}
              >
                导出报告
              </Button>
            }
          >
            <Table 
              columns={columns} 
              dataSource={mockPerformanceData.recentTests}
              rowKey="id"
              pagination={{ pageSize: 5 }}
            />
          </StyledCard>
        </div>
      </div>
    </AppLayout>
  );
};

export default Dashboard; 