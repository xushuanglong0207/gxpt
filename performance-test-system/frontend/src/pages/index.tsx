import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

// 简单的重定向页面
const Home: React.FC = () => {
  const router = useRouter();
  
  useEffect(() => {
    // 简单直接的重定向逻辑
    // 为确保能在所有环境中正常工作，直接重定向到login页面
    router.push('/login');
  }, []);
  
  return (
    <>
      <Head>
        <title>重定向中 - 性能测试系统</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta httpEquiv="refresh" content="0;url=/login" /> {/* HTML重定向回退 */}
      </Head>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div style={{ 
          background: 'rgba(255, 255, 255, 0.9)',
          padding: '20px',
          borderRadius: '8px',
          textAlign: 'center',
          maxWidth: '90%'
        }}>
          <h2>正在重定向到登录页面...</h2>
          <p>如果页面没有自动跳转，请<a href="/login" style={{ color: '#667eea', fontWeight: 'bold' }}>点击这里</a></p>
        </div>
      </div>
    </>
  );
};

export default Home; 