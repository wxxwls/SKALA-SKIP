package com.skala.skip.report.dto.request;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportDraftRequest {

    @NotNull(message = "maxTokens는 필수입니다")
    @Min(value = 100, message = "maxTokens는 최소 100 이상이어야 합니다")
    @Max(value = 8000, message = "maxTokens는 최대 8000 이하여야 합니다")
    private Integer maxTokens;

    @NotBlank(message = "tone은 필수입니다")
    @Pattern(regexp = "^(formal|informal|professional|friendly)$",
            message = "tone은 formal, informal, professional, friendly 중 하나여야 합니다")
    private String tone;

    @NotBlank(message = "language는 필수입니다")
    @Pattern(regexp = "^(ko|en)$", message = "language는 ko 또는 en이어야 합니다")
    private String language;
}

