package com.skala.skip.auth.controller;

import com.skala.skip.auth.dto.request.CreateUserRequest;
import com.skala.skip.auth.dto.response.CreateUserResponse;
import com.skala.skip.auth.service.AuthService;
import com.skala.skip.common.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * 관리자 컨트롤러
 * 사용자 관리 엔드포인트 처리
 */
@RestController
@RequestMapping("/api/v1/admin")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "관리자", description = "관리자 전용 사용자 관리 API")
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {

    private final AuthService authService;

    /**
     * 사용자 생성 (관리자 전용)
     * POST /api/v1/admin/users
     */
    @PostMapping("/users")
    @Operation(summary = "사용자 생성", description = "새로운 사용자 계정 생성 (관리자 전용)")
    public ResponseEntity<ApiResponse<CreateUserResponse>> createUser(
            @Valid @RequestBody CreateUserRequest request
    ) {
        log.info("사용자 생성 API 호출: {}", request.getEmail());

        CreateUserResponse response = authService.createUser(request);

        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
