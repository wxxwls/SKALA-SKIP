/**
 * Application Messages Constants
 * Centralized message definitions to avoid hardcoding
 */

export const AUTH_MESSAGES = {
  LOGIN_FAILED: '로그인에 실패했습니다',
  LOGIN_SUCCESS: '로그인에 성공했습니다',
  LOGOUT_SUCCESS: '로그아웃되었습니다',
  UNAUTHORIZED: '인증이 필요합니다',
  SESSION_EXPIRED: '세션이 만료되었습니다',
  INVALID_CREDENTIALS: '이메일 또는 비밀번호가 올바르지 않습니다',
  PASSWORD_CHANGED: '비밀번호가 변경되었습니다',
  PASSWORD_CHANGE_FAILED: '비밀번호 변경에 실패했습니다'
} as const;

export const VALIDATION_MESSAGES = {
  REQUIRED_FIELD: '필수 입력 항목입니다',
  INVALID_EMAIL: '올바른 이메일 형식이 아닙니다',
  INVALID_PASSWORD: '비밀번호 형식이 올바르지 않습니다',
  PASSWORD_MISMATCH: '비밀번호가 일치하지 않습니다',
  MIN_LENGTH: '최소 {0}자 이상 입력해주세요',
  MAX_LENGTH: '최대 {0}자까지 입력 가능합니다'
} as const;

export const ERROR_MESSAGES = {
  NETWORK_ERROR: '네트워크 오류가 발생했습니다',
  SERVER_ERROR: '서버 오류가 발생했습니다',
  UNKNOWN_ERROR: '알 수 없는 오류가 발생했습니다',
  REQUEST_TIMEOUT: '요청 시간이 초과되었습니다'
} as const;
