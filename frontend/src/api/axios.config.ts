/**
 * Axios Configuration
 * Configured for Spring Boot backend integration
 * Backend ref: WebConfig.java (CORS configuration)
 */

import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 에러 메시지 한글 변환
const ERROR_MESSAGE_MAP: Record<string, string> = {
  'Invalid credentials': '이메일 또는 비밀번호가 올바르지 않습니다',
  'User not found': '존재하지 않는 사용자입니다',
  'Account is locked': '계정이 잠겼습니다. 관리자에게 문의하세요',
  'Token expired': '세션이 만료되었습니다. 다시 로그인해주세요',
  'Access denied': '접근 권한이 없습니다',
  'Password must be at least 8 characters with letters, numbers, and special characters':
    '비밀번호는 영문, 숫자, 특수문자를 포함하여 8자 이상이어야 합니다'
};

function translateErrorMessage(message: string): string {
  // 기본 메시지 변환
  for (const [key, value] of Object.entries(ERROR_MESSAGE_MAP)) {
    if (message.includes(key)) {
      return message.replace(key, value);
    }
  }
  return message;
}

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const requestUrl = error.config?.url || '';
    const isAuthRequest = requestUrl.includes('/auth/login');

    // 로그인 요청이 아닌 경우에만 401 처리
    if (error.response?.status === 401 && !isAuthRequest) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }

    // 에러 메시지 추출 (detail에 남은 횟수 정보 포함)
    const errorDetail = error.response?.data?.error?.detail;
    const errorMessage = error.response?.data?.error?.message
      || error.response?.data?.message
      || error.message
      || '요청 처리 중 오류가 발생했습니다';

    // detail이 있으면 detail 사용, 없으면 message 사용
    const rawMessage = errorDetail || errorMessage;
    const translatedMessage = translateErrorMessage(rawMessage);

    return Promise.reject(new Error(translatedMessage));
  }
);

export default apiClient;
