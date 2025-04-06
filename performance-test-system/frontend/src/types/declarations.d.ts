// 模块声明
declare module 'antd';
declare module '@ant-design/icons';
declare module 'next/router';
declare module 'next/head';
declare module 'styled-components';
declare module 'echarts-for-react';

// React 类型扩展
declare namespace React {
  interface MouseEvent<T = Element> {
    target: T;
    preventDefault(): void;
    stopPropagation(): void;
  }
  
  // 其他类型扩展可根据需要添加
} 