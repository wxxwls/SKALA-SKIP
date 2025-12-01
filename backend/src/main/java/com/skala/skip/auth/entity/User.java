package com.skala.skip.auth.entity;

import com.skala.skip.common.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/**
 * User entity for authentication and authorization.
 * Includes all fields required by authentication_login_standard.md
 */
@Entity
@Table(name = "users")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class User extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Long userId;

    @Column(name = "user_name", nullable = false, length = 100)
    private String userName;

    @Column(name = "email", nullable = false, unique = true, length = 255)
    private String email;

    @Column(name = "password", nullable = false, length = 255)
    private String password;

    @Column(name = "user_role", nullable = false, length = 50)
    private String userRole;

    @Column(name = "password_updated_at")
    private LocalDateTime passwordUpdatedAt;

    @Column(name = "first_login_flag", nullable = false)
    private Boolean firstLoginFlag;

    @Column(name = "account_locked", nullable = false)
    private Boolean accountLocked;

    @Column(name = "login_fail_count", nullable = false)
    private Integer loginFailCount;

    // ===== Static Factory Method =====

    /**
     * 새로운 사용자를 생성합니다.
     * @param userName 사용자 이름
     * @param email 이메일
     * @param password BCrypt로 암호화된 비밀번호
     * @param userRole 사용자 역할
     * @param firstLoginFlag 첫 로그인 여부
     * @return 새로운 User 엔티티
     */
    public static User create(String userName, String email, String password, String userRole, boolean firstLoginFlag) {
        User user = new User();
        user.userName = userName;
        user.email = email;
        user.password = password;
        user.userRole = userRole;
        user.firstLoginFlag = firstLoginFlag;
        user.accountLocked = false;
        user.loginFailCount = 0;
        return user;
    }

    // ===== Business Methods =====

    /**
     * Increment login failure count
     */
    public void incrementLoginFailCount() {
        this.loginFailCount = (this.loginFailCount == null ? 0 : this.loginFailCount) + 1;
    }

    /**
     * Reset login failure count on successful login
     */
    public void resetLoginFailCount() {
        this.loginFailCount = 0;
    }

    /**
     * Lock account due to repeated failures
     */
    public void lockAccount() {
        this.accountLocked = true;
    }

    /**
     * Unlock account (admin action)
     */
    public void unlockAccount() {
        this.accountLocked = false;
        this.loginFailCount = 0;
    }

    /**
     * Update password
     * @param newPassword BCrypt hashed password
     */
    public void updatePassword(String newPassword) {
        this.password = newPassword;
        this.passwordUpdatedAt = LocalDateTime.now();
        this.firstLoginFlag = false;
    }

    /**
     * Check if account is locked
     */
    public boolean isLocked() {
        return this.accountLocked != null && this.accountLocked;
    }

    /**
     * Check if user must change password on first login
     */
    public boolean requiresPasswordChange() {
        return this.firstLoginFlag != null && this.firstLoginFlag;
    }
}
