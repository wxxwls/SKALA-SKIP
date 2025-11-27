package com.skala.skip.common.exception;

import com.skala.skip.ai.exception.AiServiceException;
import com.skala.skip.auth.exception.AuthenticationException;
import com.skala.skip.auth.exception.InvalidCredentialsException;
import com.skala.skip.common.dto.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

/**
 * Global exception handler
 * Ref: backend-standard - Section 5
 */
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    /**
     * Handle AI Service exceptions (AI 서비스 연동 예외)
     */
    @ExceptionHandler(AiServiceException.class)
    public ResponseEntity<ApiResponse<Void>> handleAiServiceException(AiServiceException e) {
        log.error("AI Service exception: {} - {} (httpStatus: {}, responseBody: {})",
                e.getErrorCode().getCode(), e.getMessage(), e.getHttpStatus(), e.getResponseBody());

        HttpStatus status = determineAiServiceErrorStatus(e);

        return ResponseEntity
                .status(status)
                .body(ApiResponse.error(
                        e.getErrorCode().getCode(),
                        e.getErrorCode().getMessage(),
                        e.getDetails()
                ));
    }

    /**
     * AI 서비스 예외에 따른 HTTP 상태 코드 결정
     */
    private HttpStatus determineAiServiceErrorStatus(AiServiceException e) {
        ESGErrorCode errorCode = e.getErrorCode();

        if (errorCode == ESGErrorCode.AI_TIMEOUT) {
            return HttpStatus.GATEWAY_TIMEOUT;
        }
        if (errorCode == ESGErrorCode.AI_UNAVAILABLE) {
            return HttpStatus.SERVICE_UNAVAILABLE;
        }
        if (e.getHttpStatus() != null) {
            if (e.getHttpStatus() >= 500) {
                return HttpStatus.SERVICE_UNAVAILABLE;
            }
            if (e.getHttpStatus() == 404) {
                return HttpStatus.NOT_FOUND;
            }
        }
        return HttpStatus.SERVICE_UNAVAILABLE;
    }

    /**
     * Handle business exceptions (도메인 비즈니스 예외)
     */
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException e) {
        log.error("Business exception: {} - {}", e.getErrorCode().getCode(), e.getMessage(), e);

        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(
                        e.getErrorCode().getCode(),
                        e.getErrorCode().getMessage(),
                        e.getDetails()
                ));
    }

    /**
     * Handle invalid credentials exception (로그인 실패)
     * 남은 시도 횟수 정보 포함
     */
    @ExceptionHandler(InvalidCredentialsException.class)
    public ResponseEntity<ApiResponse<Void>> handleInvalidCredentialsException(InvalidCredentialsException e) {
        log.warn("Login failed: {} (remaining attempts: {})", e.getDetails(), e.getRemainingAttempts());

        String detail = e.getRemainingAttempts() != null
                ? String.format("%s (남은 시도 횟수: %d회)", e.getDetails(), e.getRemainingAttempts())
                : e.getDetails();

        return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.error(
                        e.getErrorCode().getCode(),
                        e.getErrorCode().getMessage(),
                        detail
                ));
    }

    /**
     * Handle authentication exceptions
     */
    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<ApiResponse<Void>> handleAuthenticationException(AuthenticationException e) {
        log.error("Authentication error: {} - {}", e.getErrorCode().getCode(), e.getMessage());

        return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.error(
                        e.getErrorCode().getCode(),
                        e.getErrorCode().getMessage(),
                        e.getDetails()
                ));
    }

    /**
     * Handle username not found exception
     */
    @ExceptionHandler(UsernameNotFoundException.class)
    public ResponseEntity<ApiResponse<Void>> handleUsernameNotFoundException(UsernameNotFoundException e) {
        log.error("User not found: {}", e.getMessage());

        return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.error(
                        "AUTH-009",
                        "User not found",
                        e.getMessage()
                ));
    }

    /**
     * Handle access denied exception
     */
    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ApiResponse<Void>> handleAccessDeniedException(AccessDeniedException e) {
        log.error("Access denied: {}", e.getMessage());

        return ResponseEntity
                .status(HttpStatus.FORBIDDEN)
                .body(ApiResponse.error(
                        "AUTH-005",
                        "Access denied - insufficient permissions",
                        e.getMessage()
                ));
    }

    /**
     * Handle validation exceptions
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidationException(MethodArgumentNotValidException e) {
        String details = e.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining(", "));

        log.warn("Validation error: {}", details);

        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(
                        "VAL-001",
                        "Validation failed",
                        details
                ));
    }

    /**
     * Handle generic exceptions (최종 fallback)
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGenericException(Exception e) {
        log.error("Unexpected error", e);

        // ESGErrorCode.INTERNAL_SERVER_ERROR 가 있다면 그 코드 사용
        return ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error(
                        ESGErrorCode.INTERNAL_SERVER_ERROR.getCode(),
                        "An unexpected error occurred",
                        e.getMessage()
                ));
    }
}