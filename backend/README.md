# Backend (Spring Boot) - ESG Issue Pool AI System

## 프로젝트 개요

이 프로젝트는 **ESG 이슈풀 구성 AI 시스템**의 백엔드 서버입니다.
Spring Boot 기반으로 구축되며, **API Gateway 및 공통 플랫폼** 역할을 수행합니다.

### 핵심 역할

- 모든 외부 API의 **단일 진입점** (Vue SPA는 오직 이 서버와만 통신)
- **PostgreSQL(RDBMS)에 대한 유일한 접근 주체**
- 인증/인가, 사용자 관리, 시스템 설정 등 공통 플랫폼 기능
- FastAPI AI 서비스 호출 및 결과 중계 (AI 분석, 임베딩, RAG 등)

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| Framework | Spring Boot 3.5 |
| Language | Java 17 |
| Build Tool | Gradle |
| ORM | Spring Data JPA + MyBatis |
| Migration | Flyway |
| Auth | Spring Security + JWT |
| Cache | Spring Data Redis |
| API Client | Spring WebFlux WebClient |
| Docs | springdoc-openapi (Swagger UI) |
| Test | JUnit 5, Mockito, Testcontainers |

---

## 개발 현황 및 TODO

### 도메인별 개발 상태

| 도메인 | 상태 | 설명 |
|--------|------|------|
| `auth` | ✅ 완료 | 로그인, JWT, 사용자 관리, 비밀번호 변경 |
| `report` | ✅ 완료 | 보고서 생성, AI 초안, Export (테스트 포함) |
| `chatbot` | 🔶 진행중 | FastAPI 연계 완료, 히스토리 저장 TODO |
| `issue` | 🔶 진행중 | 기본 구조만 존재, CRUD 구현 필요 |
| `materiality` | 🔶 진행중 | 기본 구조만 존재, 매트릭스 계산 TODO |
| `benchmark` | 🔶 진행중 | FastAPI 연계 완료, 문서 관리 TODO |
| `standards` | 🔶 진행중 | FastAPI 연계 완료, 표준 문서 CRUD TODO |
| `media` | 🔶 진행중 | FastAPI 연계 완료, 뉴스 저장 TODO |
| `carbon` | 🔶 진행중 | 기본 API만 존재, 시그널 분석 TODO |
| `news` | ❌ 미개발 | 뉴스 수집 배치, 2년 보관 정책 구현 필요 |
| `survey` | ❌ 미개발 | 설문 CRUD, 응답 수집, 집계 구현 필요 |

### 공통 모듈 상태

| 모듈 | 상태 | 설명 |
|------|------|------|
| `common/exception` | ✅ 완료 | GlobalExceptionHandler, 에러 코드 |
| `common/dto` | ✅ 완료 | ApiResponse, PageResponse |
| `config` | ✅ 완료 | Security, WebClient, OpenAPI, CORS |
| `ai/client` | ✅ 완료 | FastAPI 호출 클라이언트 |

---

## 프로젝트 구조 (현재)

```
src/main/java/com/skala/skip/
├── SkipApplication.java           # 메인 애플리케이션
│
├── config/                        # ✅ 전역 설정
│   ├── SecurityConfig.java
│   ├── WebClientConfig.java
│   ├── WebConfig.java
│   ├── OpenApiConfig.java
│   └── AppProperties.java
│
├── common/                        # ✅ 공통 모듈
│   ├── dto/                       # ApiResponse 등
│   └── exception/                 # GlobalExceptionHandler
│
├── ai/                            # ✅ FastAPI 연계
│   ├── client/                    # AI 서비스 호출 클라이언트들
│   ├── config/
│   ├── dto/
│   └── exception/
│
├── auth/                          # ✅ 인증/인가 (완료)
│   ├── controller/
│   │   ├── AuthController.java
│   │   └── AdminController.java
│   ├── service/
│   │   └── impl/
│   │       ├── AuthServiceImpl.java
│   │       └── LoginAttemptService.java
│   ├── repository/
│   │   └── UserRepository.java
│   ├── entity/
│   │   └── User.java
│   ├── dto/
│   │   ├── request/
│   │   └── response/
│   ├── security/
│   │   ├── JwtAuthenticationFilter.java
│   │   └── CustomUserDetailsService.java
│   ├── util/
│   │   └── JwtTokenProvider.java
│   └── exception/
│
├── report/                        # ✅ 보고서 (완료)
│   ├── controller/
│   ├── service/
│   ├── client/
│   ├── dto/
│   └── exception/
│
├── chatbot/                       # 🔶 챗봇 (진행중)
│   ├── controller/
│   ├── service/
│   └── dto/
│
├── issue/                         # 🔶 이슈풀 (진행중)
│   ├── controller/
│   ├── service/
│   └── dto/
│
├── materiality/                   # 🔶 중대성 평가 (진행중)
│   ├── controller/
│   ├── service/
│   └── dto/
│
├── benchmark/                     # 🔶 벤치마킹 (진행중)
│   ├── controller/
│   ├── service/
│   └── dto/
│
├── standards/                     # 🔶 ESG 표준 (진행중)
│   ├── controller/
│   ├── service/
│   └── dto/
│
├── media/                         # 🔶 미디어 분석 (진행중)
│   ├── controller/
│   ├── service/
│   └── dto/
│
└── carbon/                        # 🔶 탄소배출권 (진행중)
    ├── controller/
    ├── service/
    └── dto/
```

---

## TODO: 신규 개발 필요 파일 목록

### 1. News 도메인 (뉴스 인텔리전스) - ❌ 신규 개발 필요

**생성할 파일**:
```
src/main/java/com/skala/skip/news/
├── controller/
│   └── NewsController.java              # GET /api/v1/news, POST /api/v1/news/refresh
├── service/
│   ├── NewsService.java                 # 인터페이스
│   └── impl/
│       └── NewsServiceImpl.java         # 구현체
├── repository/
│   ├── NewsArticleRepository.java       # JPA Repository
│   └── NewsSentimentRepository.java
├── entity/
│   ├── NewsArticle.java                 # news_articles 테이블 매핑
│   └── NewsSentiment.java               # news_sentiments 테이블 매핑
├── dto/
│   ├── request/
│   │   └── NewsRefreshRequest.java
│   └── response/
│       ├── NewsListResponse.java
│       └── NewsDetailResponse.java
├── batch/
│   └── NewsCleanupJob.java              # 2년 지난 뉴스 삭제 스케줄러
└── exception/
    └── NewsErrorCode.java
```

**구현할 API**:
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/news` | 뉴스 목록 조회 (필터: 기간, 카테고리, 키워드) |
| GET | `/api/v1/news/{id}` | 뉴스 상세 조회 |
| POST | `/api/v1/news/refresh` | 뉴스 재수집 트리거 |

**비즈니스 규칙**:
- 뉴스 보관 기간: 2년 (자동 삭제 배치)
- 카테고리: 자사(OWN), 경쟁사(COMP), 규제(REG)

---

### 2. Survey 도메인 (설문) - ❌ 신규 개발 필요

**생성할 파일**:
```
src/main/java/com/skala/skip/survey/
├── controller/
│   └── SurveyController.java            # POST /api/v1/surveys, /responses
├── service/
│   ├── SurveyService.java
│   └── impl/
│       └── SurveyServiceImpl.java
├── repository/
│   ├── SurveyRepository.java
│   └── SurveyResponseRepository.java
├── entity/
│   ├── Survey.java                      # surveys 테이블
│   └── SurveyResponse.java              # survey_responses 테이블
├── dto/
│   ├── request/
│   │   ├── SurveyCreateRequest.java
│   │   └── SurveyResponseSubmitRequest.java
│   └── response/
│       ├── SurveyResponse.java
│       └── SurveyResultResponse.java
├── validator/
│   └── SurveyValidator.java             # 5개 이슈 선택, 1-3점 검증
└── exception/
    └── SurveyErrorCode.java             # SVY_VAL_001, SVY_VAL_002
```

**구현할 API**:
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/surveys` | 설문 생성 |
| GET | `/api/v1/surveys/{id}` | 설문 상세 조회 |
| POST | `/api/v1/surveys/{id}/responses` | 설문 응답 제출 |
| GET | `/api/v1/surveys/{id}/results` | 설문 결과 집계 |

**비즈니스 규칙**:
- 정확히 **5개 이슈** 선택 필수 → `SVY_VAL_001` 에러
- 점수 범위 **1-3점** → `SVY_VAL_002` 에러

---

### 3. Issue 도메인 확장 - 🔶 추가 개발 필요

**추가 생성할 파일**:
```
src/main/java/com/skala/skip/issue/
├── repository/
│   ├── IssuePoolRepository.java         # TODO
│   ├── IssueRepository.java             # TODO
│   └── IssueRefRepository.java          # TODO
├── entity/
│   ├── IssuePool.java                   # TODO: issue_pools 테이블
│   ├── Issue.java                       # TODO: issues 테이블
│   ├── IssueOriginMethod.java           # TODO: issue_origin_methods 테이블
│   └── IssueRef.java                    # TODO: issue_refs 테이블
├── validator/
│   └── IssuePoolValidator.java          # TODO: 최대 20개 Topic 검증
└── exception/
    └── IssueErrorCode.java              # TODO: MAT_LIMIT_001
```

**비즈니스 규칙**:
- 최대 **20개 Topic** 제한 → `ESG-MAT-LIMIT-001` 에러
- 이슈풀 상태: DRAFT → CONFIRMED → ARCHIVED

---

### 4. Materiality 도메인 확장 - 🔶 추가 개발 필요

**추가 생성할 파일**:
```
src/main/java/com/skala/skip/materiality/
├── repository/
│   └── IssueSurveyScoreRepository.java  # TODO
├── entity/
│   └── IssueSurveyScore.java            # TODO: issue_survey_scores 테이블
└── calculator/
    └── MaterialityCalculator.java       # TODO: Double Materiality 계산
```

---

### 5. Chatbot 도메인 확장 - 🔶 추가 개발 필요

**추가 생성할 파일**:
```
src/main/java/com/skala/skip/chatbot/
├── repository/
│   └── ChatbotHistoryRepository.java    # TODO
└── entity/
    └── ChatbotHistory.java              # TODO: chatbot_histories 테이블
```

---

## 개발 시작하기

### 1. 사전 요구사항

- Java 17+
- Gradle 8.x
- PostgreSQL 16
- Redis 7
- Docker (선택)

### 2. 환경 설정

```bash
cd backend

# 환경 변수 설정
export DATABASE_URL=jdbc:postgresql://localhost:5432/esg_db
export DATABASE_USERNAME=your_username
export DATABASE_PASSWORD=your_password
export REDIS_HOST=localhost
export REDIS_PORT=6379
export FASTAPI_BASE_URL=http://localhost:8000
export JWT_SECRET=your-jwt-secret-key
```

### 3. 빌드 및 실행

```bash
# 빌드 (테스트 포함)
./gradlew build

# 테스트만 실행
./gradlew test

# 특정 테스트 실행
./gradlew test --tests "com.skala.skip.report.service.ReportCreateServiceTest"

# 애플리케이션 실행
./gradlew bootRun --args='--spring.profiles.active=dev'
```

### 4. API 문서 확인

- Swagger UI: `http://localhost:8080/swagger-ui.html`

---

## 코딩 규칙

### 1. 계층 구조 및 의존성

```
Controller → Service → Repository
                ↓
            Client (FastAPI/외부 API)
```

- **Controller**: HTTP 요청/응답 처리, `@Valid` 필수, 비즈니스 로직 금지
- **Service**: 비즈니스 로직, 트랜잭션 관리, 도메인 규칙 검증
- **Repository**: JPA/MyBatis 기반 데이터 접근만
- **Client**: FastAPI, 외부 API, S3 연계

### 2. 패키지 구조 규칙 (신규 도메인 생성 시)

```
src/main/java/com/skala/skip/{domain}/
├── controller/
│   └── {Domain}Controller.java
├── service/
│   ├── {Domain}Service.java          # 인터페이스
│   └── impl/
│       └── {Domain}ServiceImpl.java  # 구현체
├── repository/
│   └── {Domain}Repository.java
├── entity/
│   └── {Domain}.java
├── dto/
│   ├── request/
│   │   └── {Domain}CreateRequest.java
│   └── response/
│       └── {Domain}Response.java
├── validator/                         # 선택사항
│   └── {Domain}Validator.java
└── exception/
    └── {Domain}ErrorCode.java
```

### 3. Controller 패턴

```java
@RestController
@RequestMapping("/api/v1/{domain}")
@RequiredArgsConstructor
@Slf4j
public class DomainController {
    private final DomainService domainService;

    @PostMapping
    public ResponseEntity<ApiResponse<DomainResponse>> create(
            @Valid @RequestBody DomainCreateRequest request) {
        return ResponseEntity.ok(ApiResponse.success(
            domainService.create(request)
        ));
    }
}
```

### 4. Service 패턴

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class DomainServiceImpl implements DomainService {

    @Override
    @Transactional
    public DomainResponse create(DomainCreateRequest request) {
        // 비즈니스 로직
    }
}
```

### 5. Entity 규칙

```java
@Entity
@Table(name = "domains")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Domain extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "domain_id")
    private Long id;

    // @Setter, @Data, @Builder 사용 금지
}
```

### 6. Response Envelope

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "traceId": "...",
    "timestamp": "2025-01-18T10:30:00Z"
  }
}
```

---

## 에러 코드 체계

형식: `ESG-<MODULE>-<TYPE>-<NUMBER>`

| Module | 설명 | 예시 |
|--------|------|------|
| STD | 표준 문서 | ESG-STD-PARSE-001 |
| INT | 내부 데이터 | ESG-INT-UPLOAD-001 |
| BMK | 벤치마킹 | ESG-BMK-FETCH-001 |
| MED | 미디어 분석 | ESG-MED-SENT-001 |
| NWS | 뉴스 인텔리전스 | ESG-NWS-RET-001 |
| SVY | 설문 | ESG-SVY-VAL-001 |
| MAT | 중대성 평가 | ESG-MAT-LIMIT-001 |
| RPT | 보고서 생성 | ESG-RPT-DRAFT-001 |
| CHAT | 챗봇 | ESG-CHAT-RAG-001 |
| CRB | 탄소배출권 | ESG-CRB-SIGNAL-001 |

---

## FastAPI 연계 가이드

### 1. 기존 AI Client 목록 (ai/client/)

현재 구현된 클라이언트:
- 벤치마크 분석
- 표준 문서 분석
- 미디어 분석
- 챗봇 RAG
- 보고서 초안 생성

### 2. FastAPI 내부 API 엔드포인트

| 용도 | Endpoint | 상태 |
|------|----------|------|
| 이슈풀 생성 | `POST /internal/v1/issue-pool/generate` | 🔶 연계 필요 |
| 보고서 초안 | `POST /internal/v1/report/generate-draft` | ✅ 완료 |
| 뉴스 분석 | `POST /internal/v1/media/analyze` | ✅ 완료 |
| 챗봇 질의 | `POST /internal/v1/chatbot/query` | ✅ 완료 |
| 탄소 시그널 | `POST /internal/v1/carbon/signals` | 🔶 연계 필요 |

---

## 체크리스트 (개발 전 확인)

### 신규 도메인 개발 시

- [ ] 패키지 구조 생성 (controller, service, repository, entity, dto, exception)
- [ ] Entity 클래스 작성 (BaseTimeEntity 상속)
- [ ] Repository 인터페이스 작성
- [ ] Service 인터페이스 및 구현체 작성
- [ ] Controller 작성 (@Valid 적용)
- [ ] Request/Response DTO 작성
- [ ] 에러 코드 정의
- [ ] Flyway 마이그레이션 파일 작성 (필요시)
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성

---

## 참고 문서

- [요구사항정의서(SRS)](../docs/srs.md)
- [기능상세설계서(FSD)](../docs/fsd.md)
- [개발표준정의서(DS)](../docs/ds.md)
- [API 명세서](../docs/api.md)
- [아키텍처 설계서](../docs/architecture.md)
- [ERD](../docs/erd.md)
