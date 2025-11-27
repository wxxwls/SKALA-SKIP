package com.skala.skip.config;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Getter
@Setter
@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {

    private final Security security = new Security();
    private final Fastapi fastapi = new Fastapi();
    private final Aws aws = new Aws();
    private final IssuePool issuePool = new IssuePool();
    private final StakeholderSurvey stakeholderSurvey = new StakeholderSurvey();
    private final News news = new News();

    @Getter
    @Setter
    public static class Security {
        private String jwtSecret;
        private Long jwtExpiration;
        private Long jwtRefreshExpiration;
    }

    @Getter
    @Setter
    public static class Fastapi {
        private String baseUrl;
        private Integer timeout;
        private Integer retryCount;
    }

    @Getter
    @Setter
    public static class Aws {
        private final S3 s3 = new S3();

        @Getter
        @Setter
        public static class S3 {
            private String accessKeyId;
            private String accessKey;
            private String region;
            private String accessPointArn;
            private String accessPointUrl;
            private String accessPointName;
            private String accountId;
        }
    }

    @Getter
    @Setter
    public static class IssuePool {
        private Integer maxTopicCount;
    }

    @Getter
    @Setter
    public static class StakeholderSurvey {
        private Integer requiredIssueCount;
        private Integer minScore;
        private Integer maxScore;
    }

    @Getter
    @Setter
    public static class News {
        private Integer retentionYears;
    }
}
