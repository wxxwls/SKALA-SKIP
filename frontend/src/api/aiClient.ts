/**
 * AI Service API Client
 * Direct connection to Python FastAPI (port 8000)
 * Used for benchmark, media, and ESG standards APIs
 */

import axios from 'axios';

const aiClient = axios.create({
  baseURL: import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000, // AI 분석에 더 긴 타임아웃
  headers: {
    'Content-Type': 'application/json'
  }
});

// Response Interceptor
aiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error.response?.data?.detail
      || error.response?.data?.message
      || error.message
      || 'AI 서비스 요청 중 오류가 발생했습니다';

    return Promise.reject(new Error(errorMessage));
  }
);

export default aiClient;
