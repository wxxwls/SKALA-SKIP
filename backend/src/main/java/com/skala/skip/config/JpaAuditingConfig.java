package com.skala.skip.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

/**
 * JPA Auditing Configuration
 * Separated from main application class to prevent
 * "JPA metamodel must not be empty" error in @WebMvcTest
 */
@Configuration
@EnableJpaAuditing
public class JpaAuditingConfig {
}
