import React, { useState, MouseEvent } from 'react';
import { Form, Input, Button, Checkbox, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import { useRouter } from 'next/router';
import Head from 'next/head';

// 样式定义
const LoginContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
`;

const BackgroundCircle = styled.div`
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  
  &.circle1 {
    width: 300px;
    height: 300px;
    top: -100px;
    left: -100px;
  }
  
  &.circle2 {
    width: 500px;
    height: 500px;
    bottom: -200px;
    right: -200px;
  }
`;

const LoginCard = styled.div`
  background: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  padding: 40px;
  width: 400px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  z-index: 1;
`;

const Logo = styled.div`
  text-align: center;
  margin-bottom: 30px;
  
  img {
    height: 60px;
  }
`;

const Title = styled.h1`
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-weight: 600;
`;

const StyledForm = styled(Form)`
  .ant-form-item {
    margin-bottom: 20px;
  }
  
  .ant-input-affix-wrapper {
    padding: 12px;
    border-radius: 6px;
  }
  
  .ant-btn {
    height: 45px;
    border-radius: 6px;
  }
`;

const LoginButton = styled(Button)`
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
  width: 100%;
  
  &:hover, &:focus {
    background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
  }
`;

const ForgotPassword = styled.div`
  text-align: right;
  margin-bottom: 20px;
  
  a {
    color: #667eea;
    
    &:hover {
      color: #764ba2;
    }
  }
`;

const RegisterNow = styled.div`
  text-align: center;
  margin-top: 20px;
  
  a {
    color: #667eea;
    
    &:hover {
      color: #764ba2;
    }
  }
`;

// 直接登录页面组件
const DirectLogin: React.FC = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  
  // 表单提交处理
  const handleSubmit = (values: { email: string; password: string; remember: boolean }) => {
    setLoading(true);
    
    // 模拟登录请求
    setTimeout(() => {
      // 假设登录成功
      const mockToken = 'mock-jwt-token';
      const mockUser = {
        id: 1,
        name: '测试用户',
        email: values.email,
        role: 'admin'
      };
      
      // 存储登录信息
      localStorage.setItem('token', mockToken);
      localStorage.setItem('user', JSON.stringify(mockUser));
      
      message.success('登录成功！');
      
      // 跳转到仪表盘
      router.push('/dashboard');
      
      setLoading(false);
    }, 1500);
  };
  
  // 表单验证失败处理
  const onFinishFailed = (errorInfo: any) => {
    console.log('Failed:', errorInfo);
    message.error('请检查输入信息是否正确');
  };
  
  return (
    <>
      <Head>
        <title>登录 - 性能测试管理系统</title>
      </Head>
      <LoginContainer>
        <BackgroundCircle className="circle1" />
        <BackgroundCircle className="circle2" />
        
        <LoginCard>
          <Logo>
            {/* 可以替换为实际的logo */}
            <img src="/logo.png" alt="Logo" onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.onerror = null;
              target.src = 'https://via.placeholder.com/150x60?text=性能测试平台';
            }} />
          </Logo>
          
          <Title>直接登录页面</Title>
          
          <StyledForm
            name="login"
            initialValues={{ remember: true }}
            onFinish={handleSubmit}
            onFinishFailed={onFinishFailed}
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入您的邮箱!' },
                { type: 'email', message: '请输入有效的邮箱地址!' }
              ]}
            >
              <Input 
                prefix={<UserOutlined />} 
                placeholder="邮箱" 
                size="large"
              />
            </Form.Item>
            
            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入您的密码!' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
                size="large"
              />
            </Form.Item>
            
            <Form.Item>
              <Form.Item name="remember" valuePropName="checked" noStyle>
                <Checkbox>记住我</Checkbox>
              </Form.Item>
              
              <ForgotPassword>
                <a href="#" onClick={(e: MouseEvent<HTMLAnchorElement>) => {
                  e.preventDefault();
                  message.info('密码重置功能正在开发中');
                }}>
                  忘记密码?
                </a>
              </ForgotPassword>
            </Form.Item>
            
            <Form.Item>
              <LoginButton 
                type="primary" 
                htmlType="submit"
                loading={loading}
                size="large"
              >
                登录
              </LoginButton>
            </Form.Item>
            
            <RegisterNow>
              <span>还没有账号? </span>
              <a href="#" onClick={(e: MouseEvent<HTMLAnchorElement>) => {
                e.preventDefault();
                message.info('注册功能正在开发中');
              }}>
                立即注册
              </a>
            </RegisterNow>
          </StyledForm>
        </LoginCard>
      </LoginContainer>
    </>
  );
};

export default DirectLogin; 