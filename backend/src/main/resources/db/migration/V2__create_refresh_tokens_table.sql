-- V2__create_refresh_tokens_table.sql
-- Refresh Token 테이블 생성 (JWT 기반 Real Logout 구현)
-- IMPORTANT: Never modify this file after deployment. Create new migration files for changes.

-- ==============================================
-- Refresh Tokens Table
-- JWT Refresh Token 저장 및 관리
-- ==============================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token VARCHAR(512) NOT NULL UNIQUE,
    device_info VARCHAR(255),
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key Constraint
    CONSTRAINT fk_refresh_tokens_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
);

-- Indexes for refresh_tokens table
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_revoked ON refresh_tokens(revoked);

-- Comments
COMMENT ON TABLE refresh_tokens IS 'JWT Refresh Token 저장 테이블';
COMMENT ON COLUMN refresh_tokens.id IS 'Refresh Token 고유 ID';
COMMENT ON COLUMN refresh_tokens.user_id IS '사용자 ID (FK: users.user_id)';
COMMENT ON COLUMN refresh_tokens.token IS 'JWT Refresh Token 값';
COMMENT ON COLUMN refresh_tokens.device_info IS '디바이스 정보 (User-Agent 등)';
COMMENT ON COLUMN refresh_tokens.expires_at IS '토큰 만료 시간';
COMMENT ON COLUMN refresh_tokens.revoked IS '토큰 무효화 여부 (true: 로그아웃됨)';
COMMENT ON COLUMN refresh_tokens.created_at IS '생성 일시';
COMMENT ON COLUMN refresh_tokens.updated_at IS '수정 일시';
