package com.skala.skip.report.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportExportResponse {

    private String fileName;
    private String contentType;
    private byte[] fileContent;
}

