package com.skala.skip.auth.repository;

import com.skala.skip.auth.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * User repository for authentication
 * Ref: authentication_login_standard.md - Section 8.3
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * Find user by email (used for login)
     * @param email User email
     * @return Optional of User
     */
    Optional<User> findByEmail(String email);

    /**
     * Check if email exists
     * @param email User email
     * @return true if exists, false otherwise
     */
    boolean existsByEmail(String email);
}
