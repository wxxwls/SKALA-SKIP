package com.skala.skip.common.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {

    private Boolean success;
    private T data;
    private ErrorDetail error;
    private MetaResponse meta;
    private LocalDateTime timestamp;

    /**
     * Success response
     */
    public static <T> ApiResponse<T> success(T data) {
        LocalDateTime now = LocalDateTime.now();
        return ApiResponse.<T>builder()
                .success(true)
                .data(data)
                .meta(MetaResponse.builder()
                        .traceId(java.util.UUID.randomUUID().toString())
                        .build())
                .timestamp(now)
                .build();
    }

    /**
     * Success response without data
     */
    public static <T> ApiResponse<T> success() {
        LocalDateTime now = LocalDateTime.now();
        return ApiResponse.<T>builder()
                .success(true)
                .meta(MetaResponse.builder()
                        .traceId(java.util.UUID.randomUUID().toString())
                        .build())
                .timestamp(now)
                .build();
    }

    /**
     * Error response
     */
    public static <T> ApiResponse<T> error(String code, String message, String details) {
        LocalDateTime now = LocalDateTime.now();
        return ApiResponse.<T>builder()
                .success(false)
                .error(ErrorDetail.builder()
                        .code(code)
                        .message(message)
                        .detail(details)
                        .timestamp(now)
                        .build())
                .timestamp(now)
                .build();
    }

    /**
     * Error detail
     */
    @Getter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class ErrorDetail {
        private String code;
        private String message;
        private String detail;
        private LocalDateTime timestamp;
    }

}