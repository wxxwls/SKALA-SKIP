# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ESG Issue Pool Construction AI System (SKALA 2기 7조)**

Spring Boot backend for an ESG (Environmental, Social, Governance) Intelligence Platform that provides:
- Issue pool generation with 20 topic maximum constraint
- Stakeholder survey management (5 issues, 1-3 score range)
- Double materiality assessment and reporting
- News intelligence with 2-year retention policy
- Carbon credit trading signals
- Data Hub integration for KPI tracking

## Development Commands

### Build and Test
```bash
# Build the project
./gradlew build

# Run tests
./gradlew test

# Run a specific test class
./gradlew test --tests "com.skala.skip.ClassName"

# Run a specific test method
./gradlew test --tests "com.skala.skip.ClassName.testMethodName"

# Clean build
./gradlew clean build
```

### Running the Application
```bash
# Run the application
./gradlew bootRun

# Run with specific profile
./gradlew bootRun --args='--spring.profiles.active=dev'
```

### Code Quality
```bash
# Check dependencies
./gradlew dependencies

# Build without tests
./gradlew build -x test
```

## Architecture

### Layered Architecture Pattern
```
Controller Layer (REST endpoints, input validation, DTO conversion)
    ↓
Service Layer (business logic, transaction management, domain rules)
    ↓
Repository Layer (data access, JPA/MyBatis queries)
    ↓
Database (PostgreSQL with Flyway migrations)
```

**Critical**: Never put business logic in Controllers or data access logic in Services. Each layer has strict responsibilities.

### Package Structure
```
com.skala.skip/
├── common/         # 공통 모듈 (공통 예외, 공통 DTO, 유틸리티)
│   ├── exception/  # 공통 예외
│   ├── dto/        # 공통 DTO
│   └── util/       # 공통 유틸리티
├── config/         # 전역 설정 (Security, JPA, Web, Cache 등)
├── issue{도메인}/          # 이슈풀/중대성 평가 도메인
│   ├── controller/ # 이슈 관련 REST 컨트롤러
│   ├── dto/
│   │   ├── request/  # 이슈 요청 DTO
│   │   └── response/ # 이슈 응답 DTO
│   ├── entity/     # 이슈 도메인 엔티티
│   ├── exception/  # 이슈 도메인 전용 예외
│   └── service/
│       └── impl/   # 이슈 도메인 서비스 구현
├── news{도메인}/           # 뉴스 인텔리전스 도메인
├── report{도메인}/         # 보고서/리포트 도메인
├── carbon{도메인}/         # 탄소 크레딧 도메인
└── auth/           # 인증/인가 도메인
```

### Key Technologies
- **Framework**: Spring Boot 3.5.7
- **Java**: 17 LTS
- **Build**: Gradle 8.x
- **Database**: PostgreSQL 15.x
- **ORM**: JPA/Hibernate + MyBatis (complex queries)
- **Security**: Spring Security 6.x + JWT (jjwt 0.12.3)
- **Migration**: Flyway
- **Cache**: Redis
- **API Docs**: SpringDoc OpenAPI 3 + Swagger UI
- **File Processing**: Apache POI 5.3.0
- **Cloud Storage**: AWS SDK v2 S3
- **HTTP Client**: WebClient (WebFlux for FastAPI integration)

## Domain-Specific Rules

### ESG Error Code System
All errors follow the format: `ESG-<MODULE>-<TYPE>-<NUMBER>`

Modules:
- **STD**: Standard Documents
- **INT**: Internal Analysis / Data Hub
- **BMK**: Benchmarking / Competitor Analysis
- **MED**: Media Analysis
- **NWS**: News Intelligence
- **SVY**: Stakeholder Survey
- **MAT**: Materiality Assessment
- **RPT**: Report Generation
- **CHAT**: RAG Chatbot
- **CRB**: Carbon Credit

Example:
```java
ESGErrorCode.MAT_LIMIT_001  // "ESG-MAT-LIMIT-001: 20 Topic limit exceeded"
ESGErrorCode.SVY_VAL_001    // "ESG-SVY-VAL-001: Must select exactly 5 issues"
```

### Critical Business Constraints

#### 1. Issue Pool - 20 Topic Maximum
```java
@Entity
public class IssuePool {
    @OneToMany(mappedBy = "issuePool")
    @Size(max = 20, message = "Maximum 20 topics allowed")
    private List<Topic> topics;
}
```
- Always validate topic count before saving
- Throw `TopicLimitExceededException` if exceeded
- Use constant `MAX_TOPIC_COUNT = 20`

#### 2. Stakeholder Survey - Exactly 5 Issues, Scores 1-3
```java
@Entity
public class StakeholderSurvey {
    @Size(min = 5, max = 5)
    private Map<Long, Integer> issueScores;  // Value: 1-3 only
}
```
- Validate exact count: `issueScores.size() == 5`
- Validate score range: `1 <= score <= 3`
- Use `SVY_VAL_001` and `SVY_VAL_002` error codes

#### 3. News Intelligence - 2 Year Retention
```java
@Entity
public class NewsIntelligence {
    @Column(name = "retention_until")
    private LocalDateTime retentionUntil;

    @PrePersist
    public void calculateRetention() {
        this.collectedAt = LocalDateTime.now();
        this.retentionUntil = this.collectedAt.plusYears(2);
    }
}
```
- Auto-calculate retention on insert
- Implement scheduled cleanup job
- Delete records where `retentionUntil < now()`

#### 4. Data Hub Integration
- Topics can be linked to Data Hub for KPI tracking
- Set `dataHubLinked` flag when integration succeeds
- Throw `INT_VAL_002` if Data Hub connection fails

### Standard Response Format

All APIs must return wrapped responses:

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-01-18T10:30:00Z"
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "ESG-MAT-LIMIT-001",
    "message": "20 Topic limit exceeded",
    "details": "Current count: 25, Maximum: 20",
    "timestamp": "2025-01-18T10:30:00Z"
  }
}
```

### API Endpoint Patterns
```
/api/v1/issue-pool/{companyId}/generate       # POST - Generate issue pool
/api/v1/issue-pool/{companyId}/survey         # POST - Submit stakeholder survey
/api/v1/issue-pool/{companyId}/materiality    # GET - Get materiality matrix
/api/v1/report/{companyId}/draft              # POST - Generate AI report draft
/api/v1/report/{companyId}/compare            # GET - Year-over-year comparison
/api/v1/carbon/signals                        # GET - Trading signals (BUY/SELL/HOLD)
/api/v1/news/feed                             # GET - News feed with filters
```

## Code Conventions

### Naming
- **Classes**: PascalCase with suffix - `IssuePoolController`, `IssuePoolService`, `IssuePoolServiceImpl`
- **Methods**: camelCase, verb-first - `generateIssuePool()`, `findByCompanyId()`
- **Variables**: camelCase - `companyId`, `issueList`
- **Constants**: UPPER_SNAKE_CASE - `MAX_TOPIC_COUNT`, `DEFAULT_PAGE_SIZE`
- **Tables**: snake_case, plural - `issue_pools`, `news_articles`
- **Columns**: snake_case - `company_id`, `created_at`, `retention_until`

### Required Annotations
```java
@RestController
@RequestMapping("/api/v1/...")
@RequiredArgsConstructor  // Constructor injection
@Slf4j                    // Logging
public class SomeController { }

@Service
@Transactional(readOnly = true)  // Default for service
@RequiredArgsConstructor
@Slf4j
public class SomeServiceImpl { }

@Transactional  // Override for write operations
public void createSomething() { }

@Entity
@Table(name = "table_name")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class SomeEntity { }
```

### Validation
- Use `@Valid` on request DTOs in controllers
- Use Bean Validation annotations: `@NotNull`, `@Size`, `@Min`, `@Max`, `@DecimalMin`, `@DecimalMax`
- Implement business validation in service layer
- Throw `BusinessException` with appropriate `ESGErrorCode`

### Exception Handling
```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException e) {
        log.error("Business exception: {}", e.getMessage(), e);
        // Return standard error response
    }
}
```

### Logging
```java
log.info("Generating issue pool for company: {}", companyId);
log.error("Failed to generate issue pool: {}", e.getMessage(), e);
```
- INFO: Major business flows
- ERROR: Exceptions and system errors
- Never use `printStackTrace()`

### Database
- All tables must have `created_at` and `updated_at` columns
- Use `@PrePersist` and `@PreUpdate` for timestamp management
- Foreign keys: `{referenced_table}_id` (e.g., `company_id`, `issue_pool_id`)
- Indexes: `idx_{table}_{column}` (e.g., `idx_issue_pools_company_id`)
- Flyway migrations in `src/main/resources/db/migration/`
- Migration naming: `V{version}__{description}.sql` (e.g., `V1__init_schema.sql`)

## Service Separation

### ESG Chatbot vs Report Assistant
```java
@Service("esgChatbot")
public class ESGChatbotService {
    // RAG-based Q&A only
    // Cannot write reports
}

@Service("reportAssistant")
public class ReportAssistantService {
    // Report draft generation only
    // Year-over-year comparison
    // Format validation
}
```
Do NOT allow Report Assistant to answer general questions or ESG Chatbot to write reports.

## Environment Configuration

Configuration in `application.yml` uses environment variable substitution:
```yaml
spring:
  profiles:
    active: ${SPRING_PROFILE:local}
  datasource:
    url: ${DB_URL:jdbc:postgresql://localhost:5432/esgdb}
    username: ${DB_USERNAME:postgres}
    password: ${DB_PASSWORD:password}

app:
  security:
    jwt-secret: ${JWT_SECRET:changeme}
```

Never hardcode credentials or API keys.

## Reference Documents

The repository contains comprehensive standards documentation:
- `04-backend-standard-kr.md` - Full Korean backend standards (1,765 lines)
- `05-backend-standard-en.md` - English summary (380 lines)
- `06-backend-standard.json` - Structured specification

These documents define detailed rules for:
- Project structure and package organization
- Controller, Service, Repository implementation patterns
- Entity design with JPA/Hibernate
- DTO patterns (Request/Response separation)
- Exception handling hierarchy
- Transaction management
- Testing patterns (JUnit 5, Given-When-Then)
- FastAPI integration for AI/ML services

Refer to these documents for comprehensive implementation details and code examples.

## Testing

### JUnit 5 Pattern
```java
@SpringBootTest
@Transactional
class IssuePoolServiceTest {
    @Autowired
    private IssuePoolService issuePoolService;

    @Test
    @DisplayName("이슈풀 생성 성공")
    void generateIssuePool_Success() {
        // Given
        String companyId = "ABC123";
        IssuePoolCreateRequest request = new IssuePoolCreateRequest();

        // When
        IssuePoolResponse response = issuePoolService.generateIssuePool(companyId, request);

        // Then
        assertThat(response).isNotNull();
        assertThat(response.getCompanyId()).isEqualTo(companyId);
        assertThat(response.getTopics()).hasSizeLessThanOrEqualTo(20);
    }
}
```

## Prohibited Practices

- ❌ Business logic in Controller layer
- ❌ Hardcoded URLs, API keys, credentials
- ❌ `printStackTrace()` instead of logging
- ❌ Database passwords in code
- ❌ Write operations without `@Transactional`
- ❌ Skipping input validation
- ❌ Generic exceptions without error codes
- ❌ Missing response wrappers

## Integration Points

### FastAPI Backend
- WebClient for async HTTP calls to Python AI services
- Located at `${API_BASE_URL}` (configured via environment)
- Used for LLM operations, embeddings, RAG retrieval

### External Services
- **Redis**: Caching, session, JWT token storage
- **PostgreSQL**: Primary database
- **AWS S3**: Report file storage
- **Prometheus**: Metrics export via Actuator
- **Qdrant** (via FastAPI): Vector database for RAG

## Monitoring

Actuator endpoints enabled:
- `/actuator/health` - Health checks
- `/actuator/metrics` - Application metrics
- `/actuator/prometheus` - Prometheus scraping endpoint

## API Documentation

Swagger UI available at: `/swagger-ui.html` (when running)

OpenAPI 3 spec via SpringDoc automatically generated from controller annotations.

## Additional Spring Boot Development Standards

### Git Branching & Commit Standards
#### Branch Strategy (Main / Develop / Feature)
- **main**  
  Production-ready branch. Only release-ready, fully tested code is merged here. Represents the current production state.
- **develop**  
  Integration branch created from `main`. All feature and fix branches are created from `develop`. Represents the next release state.
- **feature/\***  
  New features or bug fixes. Created from `develop` and merged back into `develop` after completion via Pull Request and full test pass (unit + integration where applicable).

Notes:
- No dedicated `release/*` or `hotfix/*` branches are used.
- Production deployment is always performed from `main`.
- `develop` must remain in a releasable state (no broken build).

#### Workflow Summary
1. `main` → create `develop` (initial setup, one-time).
2. `develop` → create `feature/*` for new features or fixes.
3. Work on `feature/*` branch, keep it rebased or merged with latest `develop` when needed.
4. Create PR from `feature/*` → `develop`, require tests to pass and code review to complete.
5. After all planned features are merged and tested on `develop`, create a PR from `develop` → `main`.
6. Merge `develop` into `main` and tag the release on `main`.

#### Branch Naming Guidelines
- Use lowercase with hyphens.
- Examples:
  - `feature/issue-pool-generation`
  - `feature/fix-news-retention-bug`
  - `feature/add-materiality-matrix-api`

#### Commit Message Convention
```
&lt;type&gt;: &lt;short summary&gt;
```
Types include: `feat`, `fix`, `docs`, `refactor`, `style`, `test`, `chore`.

Examples:
- `feat: add issue pool generation endpoint`
- `fix: correct news retention date calculation`
- `refactor: extract topic validation logic`

### Spring Security Standards
#### Authentication & Authorization
- JWT-based authentication.
- Stateless session policy.
- Access token valid for 1 hour.
- Refresh tokens stored only in Redis/DB.
- Passwords must use BCrypt.

#### Filter Chain Rules
- Authentication → Authorization → Exception translation.
- CSRF disabled, CORS restricted to frontend domain.

### Validation Standards
- All input validation must be defined inside Request DTO classes using Bean Validation.
- Controllers must apply `@Valid`.
- Business rule validation must occur in Service layer.

### Exception Handling Standards
- Use @RestControllerAdvice.
- Categorize exceptions: Business, Validation, Authentication, System.
- System exceptions return 500 logs at ERROR level.
- Business exceptions return 400 logs at WARN level.

### Logging Standards
- Must use SLF4J.
- Never log sensitive data.
- Include identifiers: `companyId`, `issuePoolId`, `traceId`.

### External API / WebClient Standards
- All HTTP calls must use a centralized WebClient bean.
- Must include timeout, retry, and error mapping.
- No direct WebClient calls in controllers.

### JPA & Entity Rules
- Entities must extend BaseTimeEntity.
- No `@Builder` on Entities.
- Prefer unidirectional relationships.
- Avoid Cascade unless entity owns the lifecycle.

### Database Naming Standards
- Tables: snake_case plural.
- Columns: snake_case.
- Foreign key columns follow `{table}_id`.
- Index names: `idx_{table}_{column}`.

### Flyway Standards
- Never modify existing migration files.
- All DB schema changes must have versioned migrations.
- File naming: `V{number}__{description}.sql`.

### Testing Standards
- Minimum 80% coverage for service layer.
- Unit tests use Mockito.
- Integration tests use Testcontainers with PostgreSQL.

### Environment Configuration Standards
- No secrets in code.
- Use environment variables for all external credentials.
- Profiles: dev, prod.

This document defines how Claude Code (claude.ai/code) must work inside this repository.  
It enforces strict Spring Boot backend standards, architectural boundaries, and best practices aligned with SKALA ESG AI Platform requirements.

---

# 1. Project Overview

**ESG Issue Pool Construction AI System (SKALA Team 7)**

Spring Boot acts as the **control tower backend** for:

- ESG Issue Pool Generation (max 20 topics)
- Stakeholder Survey (exact 5 issues, score 1–3)
- Double Materiality Assessment
- News Intelligence (2‑year retention)
- Carbon Credit Trading Signals
- Data Hub (internal KPI) integration
- AI Report Drafting (via FastAPI)
- RAG ESG Chatbot (via FastAPI)

---

# 2. Build, Run, and Quality Commands

```bash
./gradlew build                 # Full build + tests
./gradlew test                  # Run all tests
./gradlew test --tests "A.B.C"  # Run specific test
./gradlew bootRun               # Run application
./gradlew bootRun --args='--spring.profiles.active=dev'
./gradlew build -x test         # Build without tests (avoid unless necessary)
./gradlew dependencies          # Dependency insight
```

Claude Code MUST default to **clean build with tests** for PR or CI workflows.

---

# 3. Architecture Standards

## 3.1 Layered Architecture (STRICT)

```
Controller → Service → Repository → PostgreSQL (Flyway-managed)
                  ↓
           WebClient Clients → FastAPI / External Services
```

Rules:

- **NO business logic in controllers**
- **NO DB access in service layer** (use repositories)
- **NO WebClient in controllers**
- **Spring Boot NEVER talks to VectorDB**
- **FastAPI NEVER talks to PostgreSQL**

---

## 3.2 Package Structure (Domain-Oriented)

```
com.skala.skip/
 ├─ common/
 │    ├─ exception/
 │    ├─ dto/
 │    └─ util/
 ├─ config/                     # Security, JPA, Redis, Web, Actuator
 ├─ issue/
 │    ├─ controller/
 │    ├─ dto/request, dto/response
 │    ├─ model (Entity + domain objects)
 │    ├─ repository
 │    ├─ service / service.impl
 │    ├─ validator
 │    └─ exception
 ├─ news/
 ├─ report/
 ├─ carbon/
 └─ auth/
```

Claude MUST replicate this structure when generating new domain modules.

---

# 4. Key Technologies (with detailed usage rules)

## 4.1 Observability & Monitoring  
Dependencies:
- `spring-boot-starter-actuator`
- `micrometer-registry-prometheus`

Rules:

- Expose only:
  - `/actuator/health`
  - `/actuator/metrics`
  - `/actuator/prometheus`
- Do NOT expose sensitive actuator endpoints.
- Add custom Micrometer timers/counters for:
  - Issue pool generation
  - Report draft creation
  - FastAPI call success/error count

AI Agent Guideline:  
For any long‑running or I/O heavy feature, wrap service logic with Micrometer timer.

---

## 4.2 Caching & Redis  
Dependencies:
- `spring-boot-starter-cache`
- `spring-boot-starter-data-redis`

Rules:

- Cache ONLY at **service layer** using `@Cacheable`, `@CachePut`, `@CacheEvict`.
- Good cache targets:
  - ESG Standards
  - KPI metadata
  - Report templates
- Redis is used for:
  - JWT Refresh Tokens
  - Session-like short-term data
  - Hot reference data
- Never use Redis as a system-of-record database.

Claude MUST make cache keys explicit.

---

## 4.3 Web Layer – MVC + WebFlux (WebClient Only)  
Dependencies:
- `spring-boot-starter-web`
- `spring-boot-starter-webflux` (for WebClient)

Rules:

- Controllers MUST be synchronous (MVC style).  
  No `Mono`/`Flux` return types in controllers.
- WebFlux is used **only for WebClient** to call:
  - FastAPI
  - Other HTTP services
- Async/Reactive usage:
  - Allowed internally for parallel external calls
  - BUT reactive types must NOT leak upward to controllers
- Never run blocking JPA operations on reactive threads.

---

## 4.4 Security & JWT  
Dependencies:
- `spring-boot-starter-security`
- `jjwt-api`, `jjwt-impl`, `jjwt-jackson`

Rules:

- Stateless sessions (`STATELESS`)
- Only a central `TokenProvider` handles token creation/validation
- Secrets must never appear in code or git
- Controllers/services must not parse JWT manually

---

## 4.5 Data Access – JPA + MyBatis + Flyway  
Dependencies:
- `spring-boot-starter-data-jpa`
- `mybatis-spring-boot-starter`
- `flyway-core`, `flyway-database-postgresql`
- `org.postgresql:postgresql`

Rules:

- Use JPA for most CRUD/standard queries
- Use MyBatis for:
  - Heavy read queries
  - Complex joins
  - Batch operations
- Flyway governs all schema changes:
  - Each change requires a new file: `V{number}__{description}.sql`
  - Never modify existing migrations

---

## 4.6 API Documentation – SpringDoc  
Dependency:
- `springdoc-openapi-starter-webmvc-ui`

Rules:

- Document every controller using `@Operation`, `@Parameter`, etc.
- Do not expose deprecated or outdated endpoints unless clearly marked

---

## 4.7 File Processing – Apache POI  
Dependencies:
- `poi`
- `poi-ooxml`

Rules:

- Create dedicated components such as `ExcelReportWriter`
- Avoid generating large workbooks in controllers
- Close workbooks/streams to prevent memory leaks

---

## 4.8 Storage – AWS S3  
Dependency:
- `software.amazon.awssdk:s3`

Rules:

- Wrap all S3 calls inside `S3StorageClient`
- Never hardcode bucket names/regions
- Handle retry/timeout/error mapping consistently

---

## 4.9 Development Convenience  
Dependencies:
- `lombok`
- `spring-boot-devtools`

Rules:

- Use Lombok only for DTO convenience and constructors
- Entities must NOT use `@Data` or `@Builder`

---

## 4.10 Testing  
Dependencies:
- `spring-boot-starter-test`
- `reactor-test`
- `mybatis-spring-boot-starter-test`
- `junit-platform-launcher`

Rules:

- Minimum 80% coverage on service layer
- Use Testcontainers for:
  - PostgreSQL
  - Redis
- Validate both DTO-level and domain-level rules

---

# 5. Domain-Specific Rules

### ESG Error Code Format  
```
ESG-<MODULE>-<TYPE>-<NUMBER>
```

Modules include: STD, INT, BMK, MED, NWS, SVY, MAT, RPT, CHAT, CRB.

### Issue Pool Rule  
Max 20 topics. Enforced in validator + service.

### Stakeholder Survey Rule  
Exactly 5 issues, each scored 1–3.

### News Intelligence  
Retention = 2 years, with scheduled cleanup.

### Response Wrapper  
All responses MUST follow:

```json
{ "success": true, "data": {...}, "timestamp": "..." }
```

Errors:

```json
{
  "success": false,
  "error": {
    "code": "ESG-MAT-LIMIT-001",
    "message": "...",
    "details": "...",
    "timestamp": "..."
  }
}
```

---

# 6. Code Conventions

## Naming

- Classes → PascalCase  
- Methods → camelCase  
- Constants → UPPER_SNAKE_CASE  
- Tables → snake_case plural  
- Columns → snake_case  

## Required Annotations

Showcase:
```java
@RestController
@RequestMapping("/api/v1/...") 
@RequiredArgsConstructor
@Slf4j
public class SomeController {}
```

```java
@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
@Slf4j
public class SomeServiceImpl {}
```

## JPA Rules

- Entities extend BaseTimeEntity
- No `@Builder` on entities
- Prefer unidirectional relationships
- Avoid unnecessary cascade

---

# 7. Testing Patterns

Use JUnit5 + Spring Boot Test + AssertJ.  
Example included already in file.

---

# 8. Prohibited Practices

- Business logic in controllers  
- Hardcoded URLs/credentials  
- `printStackTrace()`  
- Skipping `@Valid`  
- Missing response wrapper  
- Spring Boot connecting to VectorDB (forbidden)  
- FastAPI connecting to PostgreSQL (forbidden)  

---

# 9. Integration Points

- Redis for caching + tokens  
- S3 for file storage  
- Prometheus for metrics  
- FastAPI for AI tasks only  
- Never mix responsibilities across components  

---

# 10. Monitoring

Actuator endpoints enabled, Prometheus endpoint available.

---

# 11. Git Strategy

main / develop / feature branches (no release/hotfix branches).  
Commit message rules included previously.

---

# 12. Environment Configuration

Secrets injected via env vars.  
Profiles: dev, prod.

---

# End of File