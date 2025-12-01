-- V1__init_schema.sql
-- Initial database schema for SKALA ESG Issue Pool AI System
-- IMPORTANT: Never modify this file after deployment. Create new migration files for changes.

-- ==============================================
-- Users Table
-- Authentication and authorization management
-- ==============================================
CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    password_updated_at TIMESTAMP,
    first_login_flag BOOLEAN NOT NULL DEFAULT FALSE,
    account_locked BOOLEAN NOT NULL DEFAULT FALSE,
    login_fail_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_role ON users(user_role);

-- Comments
COMMENT ON TABLE users IS '사용자 정보 테이블';
COMMENT ON COLUMN users.user_id IS '사용자 고유 ID';
COMMENT ON COLUMN users.user_name IS '사용자 이름';
COMMENT ON COLUMN users.email IS '이메일 (로그인 ID)';
COMMENT ON COLUMN users.password IS 'BCrypt 암호화된 비밀번호';
COMMENT ON COLUMN users.user_role IS '사용자 역할 (ADMIN, USER 등)';
COMMENT ON COLUMN users.password_updated_at IS '비밀번호 마지막 변경 일시';
COMMENT ON COLUMN users.first_login_flag IS '첫 로그인 여부 (true: 비밀번호 변경 필요)';
COMMENT ON COLUMN users.account_locked IS '계정 잠금 여부';
COMMENT ON COLUMN users.login_fail_count IS '로그인 실패 횟수';
COMMENT ON COLUMN users.created_at IS '생성 일시';
COMMENT ON COLUMN users.updated_at IS '수정 일시';
