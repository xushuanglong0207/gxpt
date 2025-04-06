import React, { useState, useEffect } from 'react';
import { Layout, Menu, theme, Avatar, Dropdown, Badge, Button, Spin, message, Modal } from 'antd';
import { 
  DashboardOutlined, 
  FileTextOutlined, 
  UploadOutlined, 
  BookOutlined,
  UserOutlined,
  MenuFoldOutlined, 
  MenuUnfoldOutlined,
  BellOutlined,
  LogoutOutlined,
  SettingOutlined,
  KeyOutlined,
  QuestionCircleOutlined,
  GlobalOutlined,
  GithubOutlined
} from '@ant-design/icons';
import { useRouter } from 'next/router';
import Link from 'next/link';
import styled, { keyframes, css } from 'styled-components';
import Head from 'next/head';

const { Header, Sider, Content } = Layout;

// 动画效果
const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const slideIn = keyframes`
  from { transform: translateX(-20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`;

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

// 样式组件
const StyledLayout = styled(Layout)`
  min-height: 100vh;
  transition: all 0.3s;
`;

const SiderWrapper = styled.div`
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  height: 100vh;
  overflow: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s;
`;

const Logo = styled.div`
  height: 64px;
  display: flex;
  align-items: center;
  padding-left: 24px;
  color: white;
  font-size: 18px;
  font-weight: bold;
  background: rgba(255, 255, 255, 0.05);
  position: relative;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(
      90deg,
      rgba(255, 255, 255, 0),
      rgba(255, 255, 255, 0.2),
      rgba(255, 255, 255, 0)
    );
  }
`;

const LogoText = styled.span`
  background: linear-gradient(92deg, #ffffff, #b8b8b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: ${fadeIn} 1s ease-out;
`;

const StyledHeader = styled(Header)<{ $collapsed: boolean }>`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 10;
  transition: all 0.3s;
  margin-left: ${props => props.$collapsed ? '80px' : '256px'};
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const StyledContent = styled(Content)<{ $collapsed: boolean }>`
  margin: 24px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  min-height: calc(100vh - 112px);
  overflow: auto;
  transition: all 0.3s;
  margin-left: ${props => props.$collapsed ? '80px' : '256px'};
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  position: relative;
  
  /* 确保内容适应屏幕 */
  @media (max-width: 768px) {
    margin: 16px;
    padding: 16px;
  }
`;

const MenuButton = styled(Button)`
  transition: all 0.3s;
  
  &:hover {
    color: #1890ff;
    transform: scale(1.1);
  }
`;

const NavMenu = styled(Menu)`
  .ant-menu-item {
    transition: all 0.3s;
    margin: 8px 0;
    border-radius: 0 24px 24px 0;
    
    &:hover {
      transform: translateX(4px);
    }
  }
  
  .ant-menu-item-selected {
    position: relative;
    font-weight: 500;
    
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 4px;
      background: #1890ff;
      border-radius: 0 2px 2px 0;
    }
  }
`;

const AvatarWrapper = styled.div`
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    transform: scale(1.1);
  }
`;

const NotificationBadge = styled(Badge)`
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    transform: scale(1.1);
  }
  
  .ant-badge-count {
    box-shadow: 0 0 0 1px #fff;
  }
`;

const StyledFooter = styled.div`
  text-align: center;
  color: #999;
  font-size: 12px;
  padding: 16px 0;
`;

const MenuItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  
  .anticon {
    font-size: 16px;
  }
`;

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { token } = theme.useToken();

  // 检查用户是否已登录
  useEffect(() => {
    const authToken = localStorage.getItem('token');
    if (!authToken) {
      message.warning('请先登录');
      router.push('/login');
    } else {
      // 模拟获取用户数据
      setTimeout(() => {
        setLoading(false);
      }, 1000);
    }
  }, [router]);

  const handleLogout = () => {
    Modal.confirm({
      title: '确认退出登录',
      content: '您确定要退出当前账号吗？',
      okText: '确认',
      cancelText: '取消',
      onOk: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        message.success('已安全退出登录');
        router.push('/login');
      }
    });
  };

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: <Link href="/dashboard">仪表盘</Link>,
    },
    {
      key: '/test-cases',
      icon: <FileTextOutlined />,
      label: <Link href="/test-cases">测试用例</Link>,
    },
    {
      key: '/csv-data',
      icon: <UploadOutlined />,
      label: <Link href="/csv-data">CSV数据</Link>,
    },
    {
      key: '/knowledge',
      icon: <BookOutlined />,
      label: <Link href="/knowledge">知识分享</Link>,
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: <Link href="/users">用户管理</Link>,
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
      onClick: () => message.info('功能开发中')
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
      onClick: () => message.info('功能开发中')
    },
    {
      key: 'password',
      icon: <KeyOutlined />,
      label: '修改密码',
      onClick: () => message.info('功能开发中')
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout
    },
  ];

  const notificationItems = [
    {
      key: '1',
      label: '新测试用例已创建',
      onClick: () => message.info('功能开发中'),
    },
    {
      key: '2',
      label: '有新的知识分享文章',
      onClick: () => message.info('功能开发中'),
    },
    {
      key: '3',
      label: 'CSV数据分析完成',
      onClick: () => message.info('功能开发中'),
    },
  ];

  // 获取用户信息
  const getUserData = () => {
    try {
      const userData = localStorage.getItem('user');
      if (userData) {
        return JSON.parse(userData);
      }
      return { name: '测试用户', avatar: '' };
    } catch (error) {
      console.error('获取用户信息失败', error);
      return { name: '测试用户', avatar: '' };
    }
  };

  const user = getUserData();

  const avatarUrl = user.avatar || 'https://randomuser.me/api/portraits/men/1.jpg';

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: '#f0f2f5'
      }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return (
    <StyledLayout>
      <Head>
        <title>性能测试管理系统</title>
      </Head>
      <SiderWrapper style={{ width: collapsed ? 80 : 256 }}>
        <Sider 
          trigger={null} 
          collapsible 
          collapsed={collapsed}
          width={256}
          style={{
            height: '100%',
            overflow: 'auto',
            position: 'relative',
          }}
          theme="dark"
        >
          <Logo>
            <LogoText>
              {!collapsed ? '性能测试管理系统' : 'PTS'}
            </LogoText>
          </Logo>
          <NavMenu
            theme="dark"
            mode="inline"
            selectedKeys={[router.pathname]}
            items={menuItems.map(item => ({
              key: item.key,
              icon: item.icon,
              label: item.label,
              className: router.pathname === item.key ? 'ant-menu-item-active' : ''
            }))}
          />
        </Sider>
      </SiderWrapper>
      
      <Layout style={{ transition: 'all 0.2s' }}>
        <StyledHeader $collapsed={collapsed}>
          <MenuButton
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            size="large"
          />
          <HeaderRight>
            <Button 
              type="text" 
              icon={<QuestionCircleOutlined />} 
              size="large"
              onClick={() => message.info('帮助文档功能开发中')}
            />
            <Dropdown
              menu={{ 
                items: notificationItems.map(item => ({
                  key: item.key,
                  label: item.label,
                  onClick: item.onClick
                }))
              }}
              placement="bottomRight"
              arrow
            >
              <NotificationBadge count={3} size="small">
                <Button type="text" icon={<BellOutlined />} size="large" />
              </NotificationBadge>
            </Dropdown>
            <Dropdown
              menu={{ 
                items: userMenuItems.map(item => {
                  if (item.type === 'divider') {
                    return { type: 'divider' };
                  }
                  return {
                    key: item.key,
                    label: (
                      <MenuItem>
                        {item.icon}
                        {item.label}
                      </MenuItem>
                    ),
                    onClick: item.onClick
                  };
                })
              }}
              placement="bottomRight"
              arrow
            >
              <AvatarWrapper>
                <Avatar 
                  size={36} 
                  src={avatarUrl}
                  style={{ backgroundColor: token.colorPrimary, cursor: 'pointer' }}
                />
              </AvatarWrapper>
            </Dropdown>
          </HeaderRight>
        </StyledHeader>
        <StyledContent $collapsed={collapsed}>
          {children}
          <StyledFooter>
            性能测试管理系统 ©2023 - {new Date().getFullYear()} 版权所有
          </StyledFooter>
        </StyledContent>
      </Layout>
    </StyledLayout>
  );
};

export default AppLayout; 