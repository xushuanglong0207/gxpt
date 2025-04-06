import React, { useEffect } from 'react';
import type { AppProps } from 'next/app';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/lib/locale/zh_CN';
import '@/styles/globals.css';
import { useRouter } from 'next/router';

// 自定义主题配置
const theme = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 4,
    fontSize: 14,
  },
  components: {
    Button: {
      controlHeight: 40,
      controlHeightLG: 48,
      controlHeightSM: 32,
    },
    Card: {
      boxShadow: '0 1px 2px -2px rgba(0, 0, 0, 0.16), 0 3px 6px 0 rgba(0, 0, 0, 0.12), 0 5px 12px 4px rgba(0, 0, 0, 0.09)',
    },
    Menu: {
      colorItemBgSelected: 'rgba(24, 144, 255, 0.1)',
    },
  },
};

function MyApp({ Component, pageProps }: AppProps) {
  const router = useRouter();
  
  useEffect(() => {
    // 如果是根路径，检查是否有登录token
    if (router.pathname === '/') {
      const token = localStorage.getItem('token');
      if (token) {
        // 已登录，重定向到仪表盘
        router.push('/dashboard');
      } else {
        // 未登录，显示登录页面（现在index.tsx已是登录页）
        console.log('未登录，显示登录页面');
      }
    }
  }, [router.pathname]);

  return (
    <ConfigProvider theme={theme} locale={zhCN}>
      <Component {...pageProps} />
    </ConfigProvider>
  );
}

export default MyApp; 