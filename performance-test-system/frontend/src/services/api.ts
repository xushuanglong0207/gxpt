import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
import { message } from 'antd';

// API基础URL
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';

// 创建axios实例
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const { response } = error;
    
    if (response) {
      // 处理常见的HTTP错误
      if (response.status === 401) {
        message.error('登录已过期，请重新登录');
        localStorage.removeItem('token');
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      } else if (response.status === 403) {
        message.error('没有权限访问该资源');
      } else if (response.status === 404) {
        message.error('请求的资源不存在');
      } else if (response.status === 500) {
        message.error('服务器内部错误');
      } else {
        message.error(response.data?.message || '请求失败');
      }
    } else {
      message.error('网络错误，请检查您的网络连接');
    }
    
    return Promise.reject(error);
  }
);

// 通用请求方法
const request = <T = any>(config: AxiosRequestConfig): Promise<T> => {
  return api(config)
    .then((response: AxiosResponse<T>) => response.data)
    .catch((error) => {
      return Promise.reject(error);
    });
};

// 身份验证相关API
export const authApi = {
  login: (data: { email: string; password: string }) => 
    request<{ token: string; user: any }>({
      url: '/auth/login',
      method: 'post',
      data,
    }),
  
  register: (data: { name: string; email: string; password: string }) => 
    request<{ token: string; user: any }>({
      url: '/auth/register',
      method: 'post',
      data,
    }),
  
  forgotPassword: (data: { email: string }) => 
    request<{ message: string }>({
      url: '/auth/forgot-password',
      method: 'post',
      data,
    }),
  
  resetPassword: (data: { token: string; password: string }) => 
    request<{ message: string }>({
      url: '/auth/reset-password',
      method: 'post',
      data,
    }),
  
  getMe: () => 
    request<{ user: any }>({
      url: '/auth/me',
      method: 'get',
    }),
  
  logout: () => {
    localStorage.removeItem('token');
    return Promise.resolve();
  },
};

// 测试用例相关API
export const testCaseApi = {
  getAll: (params?: { page?: number; limit?: number; search?: string; status?: string; priority?: string }) => 
    request<{ total: number; items: any[] }>({
      url: '/test-cases',
      method: 'get',
      params,
    }),
  
  getById: (id: string) => 
    request<{ testCase: any }>({
      url: `/test-cases/${id}`,
      method: 'get',
    }),
  
  create: (data: any) => 
    request<{ testCase: any }>({
      url: '/test-cases',
      method: 'post',
      data,
    }),
  
  update: (id: string, data: any) => 
    request<{ testCase: any }>({
      url: `/test-cases/${id}`,
      method: 'put',
      data,
    }),
  
  delete: (id: string) => 
    request<{ message: string }>({
      url: `/test-cases/${id}`,
      method: 'delete',
    }),
  
  batchImport: (data: any[]) => 
    request<{ count: number }>({
      url: '/test-cases/import',
      method: 'post',
      data,
    }),
  
  export: (ids: string[]) => 
    request<{ testCases: any[] }>({
      url: `/test-cases/export/${ids.join(',')}`,
      method: 'get',
    }),
};

// 仪表盘相关API
export const dashboardApi = {
  getSummary: () => 
    request<{ 
      testCasesCount: number; 
      passedTestsCount: number; 
      failedTestsCount: number; 
      pendingTestsCount: number; 
    }>({
      url: '/dashboard/summary',
      method: 'get',
    }),
  
  getRecentActivities: () => 
    request<{ activities: any[] }>({
      url: '/dashboard/recent-activities',
      method: 'get',
    }),
  
  getPerformanceMetrics: () => 
    request<{ metrics: any[] }>({
      url: '/dashboard/performance-metrics',
      method: 'get',
    }),
};

// 用于模拟API响应的方法（开发阶段使用）
export const mockResponse = <T>(data: T, delay: number = 500): Promise<T> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(data);
    }, delay);
  });
};

export default {
  request,
  authApi,
  testCaseApi,
  dashboardApi,
  mockResponse,
}; 