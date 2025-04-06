import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Checkbox, message, Typography, Spin } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useRouter } from 'next/router';
import styled, { keyframes } from 'styled-components';
import { authAPI } from '@/services/api';
import Head from 'next/head';

const { Title, Text } = Typography;

// 动画效果
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const float = keyframes`
  0% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
  100% { transform: translateY(0px); }
`;

// 样式组件
const LoginContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(120deg, #5f72bd 0%, #9b23ea 100%);
  position: relative;
  overflow: hidden;
`;

const BackgroundElement = styled.div`
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  
  &.circle1 {
    width: 600px;
    height: 600px;
    top: -200px;
    right: -100px;
  }
  
  &.circle2 {
    width: 400px;
    height: 400px;
    bottom: -150px;
    left: -150px;
  }
  
  &.floating {
    animation: ${float} 6s ease-in-out infinite;
  }
`;

const LoginCard = styled.div`
  width: 100%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  z-index: 1;
  animation: ${fadeIn} 0.8s ease-out;
`;

const LogoContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
`;

const Logo = styled.div`
  font-size: 28px;
  font-weight: bold;
  color: #5f72bd;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const StyledForm = styled(Form)`
  .ant-form-item {
    margin-bottom: 24px;
  }
  
  .ant-input-affix-wrapper {
    padding: 12px;
    border-radius: 8px;
    
    &:hover, &:focus, &-focused {
      border-color: #5f72bd;
      box-shadow: 0 0 0 2px rgba(95, 114, 189, 0.2);
    }
  }
  
  .ant-btn {
    height: 48px;
    border-radius: 8px;
    font-weight: 500;
  }
`;

const GradientButton = styled(Button)`
  background: linear-gradient(90deg, #5f72bd 0%, #9b23ea 100%);
  border: none;
  
  &:hover, &:focus {
    background: linear-gradient(90deg, #4f62ad 0%, #8b13da 100%);
  }
`;

const StyledCheckbox = styled(Checkbox)`
  .ant-checkbox-checked .ant-checkbox-inner {
    background-color: #5f72bd;
    border-color: #5f72bd;
  }
`;

const Login: React.FC = () => {
  const [form] = Form.useForm();
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  // 检查用户是否已登录
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      router.push('/dashboard');
    }
  }, [router]);

  // 处理表单提交
  const handleSubmit = async (values: { email: string; password: string; remember: boolean }) => {
    try {
      setLoading(true);
      // 直接模拟登录成功，跳过实际API调用
      // 实际项目中应使用: await authAPI.login(values);
      setTimeout(() => {
        // 保存token
        localStorage.setItem('token', 'mock-token-12345');
        
        // 保存用户信息
        const userData = {
          id: '1',
          name: '测试用户',
          email: values.email,
          avatar: 'https://randomuser.me/api/portraits/men/1.jpg',
          role: 'admin'
        };
        localStorage.setItem('user', JSON.stringify(userData));
        
        message.success('登录成功');
        router.push('/dashboard');
      }, 1500);
    } catch (error) {
      console.error('登录失败:', error);
      message.error('登录失败，请检查邮箱和密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>登录 - 性能测试管理系统</title>
      </Head>
      <LoginContainer>
        <BackgroundElement className="circle1 floating" />
        <BackgroundElement className="circle2 floating" />
        
        <LoginCard>
          <LogoContainer>
            <Logo>
              <span style={{ color: '#5f72bd' }}>性能测试</span>
              <span style={{ color: '#9b23ea' }}>管理系统</span>
            </Logo>
          </LogoContainer>
          
          <Title level={3} style={{ textAlign: 'center', marginBottom: '2rem' }}>
            登录您的账户
          </Title>
          
          <StyledForm
            form={form}
            name="login"
            initialValues={{ remember: true }}
            onFinish={handleSubmit}
            size="large"
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' }
              ]}
            >
              <Input 
                prefix={<UserOutlined />} 
                placeholder="请输入邮箱" 
                disabled={loading}
              />
            </Form.Item>
            
            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password 
                prefix={<LockOutlined />} 
                placeholder="请输入密码" 
                disabled={loading}
              />
            </Form.Item>
            
            <Form.Item name="remember" valuePropName="checked">
              <StyledCheckbox disabled={loading}>记住我</StyledCheckbox>
              <a 
                style={{ float: 'right', color: '#5f72bd' }}
                onClick={(e) => {
                  e.preventDefault();
                  message.info('密码重置功能正在开发中');
                }}
              >
                忘记密码?
              </a>
            </Form.Item>
            
            <Form.Item>
              <GradientButton 
                type="primary" 
                htmlType="submit" 
                block
                loading={loading}
              >
                {loading ? '登录中...' : '登录'}
              </GradientButton>
            </Form.Item>
            
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">暂无账号? </Text>
              <a 
                style={{ color: '#5f72bd' }}
                onClick={(e) => {
                  e.preventDefault();
                  message.info('注册功能正在开发中');
                }}
              >
                立即注册
              </a>
            </div>
          </StyledForm>
        </LoginCard>
      </LoginContainer>
    </>
  );
};

export default Login; 