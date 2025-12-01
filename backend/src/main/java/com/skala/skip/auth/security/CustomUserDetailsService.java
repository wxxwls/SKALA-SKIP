package com.skala.skip.auth.security;

import com.skala.skip.auth.entity.User;
import com.skala.skip.auth.exception.AccountLockedException;
import com.skala.skip.auth.exception.AuthErrorCode;
import com.skala.skip.auth.exception.AuthenticationException;
import com.skala.skip.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;

/**
 * Custom UserDetailsService implementation
 * Loads user from database by email
 * Ref: authentication_login_standard.md - Section 8.3
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CustomUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    /**
     * Load user by email (username in Spring Security context)
     * @param email User email
     * @return UserDetails
     * @throws UsernameNotFoundException if user not found
     */
    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        log.debug("Loading user by email: {}", email);

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("User not found with email: " + email));

        // Check if account is locked
        if (user.isLocked()) {
            log.warn("Attempt to login with locked account: {}", email);
            throw new AccountLockedException("Account is locked: " + email);
        }

        // Convert to Spring Security UserDetails
        return org.springframework.security.core.userdetails.User.builder()
                .username(user.getEmail())
                .password(user.getPassword())
                .authorities(Collections.singletonList(new SimpleGrantedAuthority(user.getUserRole())))
                .accountExpired(false)
                .accountLocked(user.isLocked())
                .credentialsExpired(false)
                .disabled(false)
                .build();
    }

    /**
     * Load full user entity by email
     * @param email User email
     * @return User entity
     */
    @Transactional(readOnly = true)
    public User loadUserEntityByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new AuthenticationException(AuthErrorCode.AUTH_009, "User not found: " + email));
    }
}
