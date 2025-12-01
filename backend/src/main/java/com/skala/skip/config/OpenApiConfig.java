package com.skala.skip.config;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.security.SecurityScheme;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI Configuration
 * Configures Swagger UI with JWT Bearer token authentication
 */
@Configuration
@Slf4j
@OpenAPIDefinition(
        info = @Info(
                title = "SKALA ESG Intelligence Platform API",
                version = "1.0.0",
                description = "ESG Issue Pool Construction and Intelligence Platform API Documentation"
        )
)
@SecurityScheme(
        name = "Bearer Authentication",
        type = SecuritySchemeType.HTTP,
        bearerFormat = "JWT",
        scheme = "bearer",
        description = "Enter JWT token without 'Bearer ' prefix"
)
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        log.info("Configuring OpenAPI with JWT Bearer authentication");
        return new OpenAPI()
                .addSecurityItem(new SecurityRequirement().addList("Bearer Authentication"));
    }
}
