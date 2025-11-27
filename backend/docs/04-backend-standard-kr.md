# 백엔드 개발 표준 (Backend Development Standard)

**ESG 이슈풀 구성 AI 시스템**
**Version 1.0**
**SKALA 2기 7조**

---

## 문서 개요

본 문서는 ESG 이중 중대성 이슈풀 자동 구성 서비스의 **백엔드 개발 표준**을 정의합니다.

**목적**: 여러 개발자가 AI를 활용해 동시 개발할 때, 최종 병합 시 충돌·불일치·에러가 발생하지 않도록 통일된 규칙을 제공합니다.

**적용 대상**: Spring Boot (Java) 및 FastAPI (Python) 백엔드 개발

---

## 1. 기술 스택 및 버전 고정

### 1.1 Spring Boot 스택

```json
{
  "framework": "Spring Boot 3.5.x",
  "java": "Java 17 LTS",
  "buildTool": "Gradle 8.x",
  "database": "PostgreSQL 15.x",
  "orm": "Spring Data JPA / Hibernate",
  "security": "Spring Security 6.x",
  "testing": "JUnit 5, Mockito"
}
```

### 1.2 FastAPI 스택

```json
{
  "framework": "FastAPI 0.110.x",
  "python": "Python 3.11",
  "database": "PostgreSQL 15.x",
  "orm": "SQLAlchemy 2.x",
  "vectorDB": "Qdrant 1.x",
  "validation": "Pydantic 2.x",
  "testing": "pytest 8.x"
}
```

### 1.3 버전 고정 규칙

- **Spring Boot**: `build.gradle`에서 정확한 버전 사용
- **FastAPI**: `requirements.txt`에서 정확한 버전 사용 (==)
- 라이브러리 업데이트 시 팀 승인 필수

---

## 2. 프로젝트 구조

### 2.1 Spring Boot 구조

```
com.esg.system/
├── config/              # 설정 클래스
│   ├── SecurityConfig.java
│   ├── JpaConfig.java
│   └── WebConfig.java
├── controller/          # REST API 컨트롤러
│   ├── IssuePoolController.java
│   ├── NewsController.java
│   └── CarbonController.java
├── dto/                 # Data Transfer Objects
│   ├── request/        # Request DTOs
│   │   ├── IssuePoolCreateRequest.java
│   │   └── IssueCreateRequest.java
│   └── response/       # Response DTOs
│       ├── IssuePoolResponse.java
│       └── IssueResponse.java
├── entity/              # JPA 엔티티
│   ├── IssuePool.java
│   ├── Issue.java
│   └── User.java
├── repository/          # JPA Repository
│   ├── IssuePoolRepository.java
│   └── IssueRepository.java
├── service/             # 비즈니스 로직
│   ├── IssuePoolService.java
│   └── impl/
│       └── IssuePoolServiceImpl.java
├── exception/           # 예외 클래스
│   ├── GlobalExceptionHandler.java
│   ├── BusinessException.java
│   └── ErrorCode.java
└── util/                # 유틸리티 클래스
    └── DateUtil.java
```

### 2.2 FastAPI 구조

```
app/
├── api/                 # API 라우터
│   ├── v1/
│   │   ├── issue_pool.py
│   │   ├── news.py
│   │   └── chatbot.py
│   └── __init__.py
├── core/                # 핵심 설정
│   ├── config.py       # 환경 설정
│   ├── security.py     # 인증/보안
│   └── database.py     # DB 연결
├── services/            # 비즈니스 로직
│   ├── issue_pool_service.py
│   ├── news_service.py
│   └── embedding_service.py
├── repositories/        # 데이터 접근 계층
│   ├── issue_pool_repository.py
│   └── vector_repository.py
├── models/              # SQLAlchemy 모델
│   ├── issue_pool.py
│   ├── news.py
│   └── user.py
├── schemas/             # Pydantic 스키마
│   ├── issue_pool.py
│   ├── news.py
│   └── common.py
├── llm/                 # LLM 관련
│   ├── prompts/        # 프롬프트 템플릿
│   ├── chains/         # LangChain 체인
│   └── agents/         # LangGraph 에이전트
├── batch/               # 배치 작업
│   ├── news_crawler.py
│   └── embedding_job.py
└── main.py
```

---

## 3. 네이밍 컨벤션

### 3.1 Java (Spring Boot)

#### 클래스명

```java
// Controller: <Domain><Action>Controller
public class IssuePoolController { }
public class NewsController { }

// Service: <Domain>Service / <Domain>ServiceImpl
public interface IssuePoolService { }
public class IssuePoolServiceImpl implements IssuePoolService { }

// Repository: <Domain>Repository
public interface IssuePoolRepository extends JpaRepository { }

// DTO: <Domain><Purpose>DTO
public class IssuePoolCreateRequest { }
public class IssuePoolResponse { }

// Entity: <Domain>
@Entity
public class IssuePool { }

// Exception: <Purpose>Exception
public class BusinessException extends RuntimeException { }
```

#### 변수·메서드명

```java
// 변수: camelCase
private String companyId;
private List<Issue> issueList;

// 메서드: camelCase (동사 시작)
public IssuePool generateIssuePool(String companyId) { }
public List<Issue> findActiveIssues() { }

// Boolean: is/has 시작
public boolean isActive() { }
public boolean hasPermission() { }

// 상수: UPPER_SNAKE_CASE
public static final int DEFAULT_PAGE_SIZE = 20;
public static final String ESG_STANDARD_VERSION = "GRI_2021";
```

### 3.2 Python (FastAPI)

#### 파일·모듈명

```python
# 파일: snake_case
# issue_pool_service.py
# news_repository.py
# embedding_pipeline.py
```

#### 클래스명

```python
# 클래스: PascalCase
class IssuePoolService:
    pass

class NewsRepository:
    pass

class IssuePoolCreateRequest(BaseModel):
    pass
```

#### 함수·변수명

```python
# 함수: snake_case (동사 시작)
def generate_issue_pool(company_id: str) -> IssuePool:
    pass

def fetch_recent_news(days: int) -> List[News]:
    pass

# 변수: snake_case
company_id = "ABC123"
issue_list = []
embedding_vector = []

# 상수: UPPER_SNAKE_CASE
DEFAULT_PAGE_SIZE = 20
MAX_ISSUE_COUNT = 100
ESG_STANDARD_VERSION = "GRI_2021"
```

---

## 4. Layered Architecture

### 4.1 레이어 책임

```
Controller/API Layer
    ↓ (DTO)
Service Layer
    ↓ (Entity/Model)
Repository Layer
    ↓
Database
```

#### Controller/API Layer
- HTTP 요청/응답 처리
- DTO 변환
- 입력 검증
- **비즈니스 로직 금지**

#### Service Layer
- 비즈니스 로직 구현
- 트랜잭션 관리
- 도메인 규칙 적용
- Repository 호출

#### Repository Layer
- 데이터 접근
- CRUD 연산
- 쿼리 작성
- **비즈니스 로직 금지**

---

## 5. API 개발 표준

### 5.1 REST API URL 규칙

```
# Format
/api/v1/{resource}/{id}/{action}

# Examples
GET    /api/v1/issue-pool/{companyId}
POST   /api/v1/issue-pool/{companyId}/generate
GET    /api/v1/news/feed?companyId=123&days=7
POST   /api/v1/chatbot/query
POST   /api/v1/carbon-emission/predict
```

**규칙**:
- kebab-case 사용
- 명사형 리소스명
- HTTP 메서드로 액션 표현 (GET, POST, PUT, PATCH, DELETE)
- 버전 관리 (/v1, /v2)

### 5.2 HTTP Method 사용

| Method | 용도 | 멱등성 |
|--------|------|--------|
| GET | 조회 (서버 상태 변경 없음) | O |
| POST | 생성, 액션 수행 | X |
| PUT | 전체 업데이트 | O |
| PATCH | 부분 업데이트 | X |
| DELETE | 삭제 | O |

### 5.3 표준 Response Wrapper

#### 성공 응답

```json
{
  "success": true,
  "data": {
    "issuePoolId": "IP-20250118-001",
    "companyId": "ABC123",
    "issues": [...]
  },
  "timestamp": "2025-01-18T10:30:00Z"
}
```

#### 실패 응답

```json
{
  "success": false,
  "error": {
    "code": "ISS001",
    "message": "Issue pool not found",
    "details": "Company ID: ABC123 has no issue pool",
    "timestamp": "2025-01-18T10:30:00Z"
  }
}
```

#### 페이지네이션 응답

```json
{
  "success": true,
  "data": {
    "items": [...],
    "meta": {
      "page": 1,
      "pageSize": 20,
      "totalCount": 150,
      "totalPages": 8
    }
  }
}
```

---

## 6. Spring Boot 개발 표준

### 6.1 Controller 작성

```java
@RestController
@RequestMapping("/api/v1/issue-pool")
@RequiredArgsConstructor
@Slf4j
public class IssuePoolController {

    private final IssuePoolService issuePoolService;

    @GetMapping("/{companyId}")
    public ResponseEntity<ApiResponse<IssuePoolResponse>> getIssuePool(
            @PathVariable String companyId) {

        log.info("Fetching issue pool for company: {}", companyId);

        IssuePoolResponse response = issuePoolService.getIssuePool(companyId);

        return ResponseEntity.ok(
            ApiResponse.success(response)
        );
    }

    @PostMapping("/{companyId}/generate")
    public ResponseEntity<ApiResponse<IssuePoolResponse>> generateIssuePool(
            @PathVariable String companyId,
            @Valid @RequestBody IssuePoolCreateRequest request) {

        log.info("Generating issue pool for company: {}", companyId);

        IssuePoolResponse response = issuePoolService.generateIssuePool(
            companyId,
            request
        );

        return ResponseEntity.ok(
            ApiResponse.success(response)
        );
    }
}
```

**규칙**:
- `@RestController` + `@RequestMapping` 사용
- `@RequiredArgsConstructor`로 생성자 주입
- `@Slf4j`로 로깅
- `@Valid`로 입력 검증
- ResponseEntity로 HTTP 상태 코드 명시

### 6.2 Service 작성

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class IssuePoolServiceImpl implements IssuePoolService {

    private final IssuePoolRepository issuePoolRepository;
    private final IssueRepository issueRepository;

    @Override
    public IssuePoolResponse getIssuePool(String companyId) {
        IssuePool issuePool = issuePoolRepository.findByCompanyId(companyId)
            .orElseThrow(() -> new BusinessException(
                ErrorCode.ISSUE_POOL_NOT_FOUND,
                "Company ID: " + companyId
            ));

        return IssuePoolResponse.from(issuePool);
    }

    @Override
    @Transactional
    public IssuePoolResponse generateIssuePool(
            String companyId,
            IssuePoolCreateRequest request) {

        // 1. 기존 이슈풀 확인
        issuePoolRepository.findByCompanyId(companyId)
            .ifPresent(existing -> {
                throw new BusinessException(
                    ErrorCode.ISSUE_POOL_ALREADY_EXISTS
                );
            });

        // 2. 이슈풀 생성
        IssuePool issuePool = IssuePool.builder()
            .companyId(companyId)
            .status(IssuePoolStatus.DRAFT)
            .build();

        issuePool = issuePoolRepository.save(issuePool);

        // 3. 이슈 생성 및 연결
        List<Issue> issues = createIssuesFromRequest(request, issuePool);
        issueRepository.saveAll(issues);

        log.info("Generated issue pool: {} with {} issues",
            issuePool.getId(), issues.size());

        return IssuePoolResponse.from(issuePool);
    }

    private List<Issue> createIssuesFromRequest(
            IssuePoolCreateRequest request,
            IssuePool issuePool) {
        // 구현 로직
        return new ArrayList<>();
    }
}
```

**규칙**:
- `@Service` + `@Transactional(readOnly = true)` 기본
- 쓰기 작업은 `@Transactional` 명시
- Repository 의존성 주입
- 예외는 BusinessException으로 통일
- 복잡한 로직은 private 메서드로 분리

### 6.3 Entity 작성

```java
@Entity
@Table(name = "issue_pools")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class IssuePool extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "company_id", nullable = false, length = 50)
    private String companyId;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    private IssuePoolStatus status;

    @OneToMany(mappedBy = "issuePool", cascade = CascadeType.ALL)
    private List<Issue> issues = new ArrayList<>();

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // 비즈니스 메서드
    public void activate() {
        this.status = IssuePoolStatus.ACTIVE;
    }

    public void addIssue(Issue issue) {
        this.issues.add(issue);
        issue.setIssuePool(this);
    }
}
```

**규칙**:
- 테이블명: snake_case, 복수형
- 컬럼명: snake_case
- Lombok `@Getter`, `@Builder` 사용
- `@NoArgsConstructor(access = AccessLevel.PROTECTED)` 필수
- 연관관계는 명확하게 명시
- 비즈니스 로직은 Entity 내부 메서드로

---

## 7. FastAPI 개발 표준

### 7.1 API Router 작성

```python
# api/v1/issue_pool.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from schemas.issue_pool import (
    IssuePoolCreateRequest,
    IssuePoolResponse
)
from services.issue_pool_service import IssuePoolService
from core.security import get_current_user

router = APIRouter(prefix="/api/v1/issue-pool", tags=["Issue Pool"])

@router.get("/{company_id}", response_model=IssuePoolResponse)
async def get_issue_pool(
    company_id: str,
    service: IssuePoolService = Depends()
):
    """
    Get issue pool for a company

    Args:
        company_id: Company identifier
        service: IssuePoolService dependency

    Returns:
        IssuePoolResponse
    """
    return await service.get_issue_pool(company_id)


@router.post(
    "/{company_id}/generate",
    response_model=IssuePoolResponse,
    status_code=status.HTTP_201_CREATED
)
async def generate_issue_pool(
    company_id: str,
    request: IssuePoolCreateRequest,
    service: IssuePoolService = Depends()
):
    """
    Generate new issue pool for a company

    Args:
        company_id: Company identifier
        request: Issue pool creation request
        service: IssuePoolService dependency

    Returns:
        IssuePoolResponse
    """
    return await service.generate_issue_pool(company_id, request)
```

### 7.2 Service 작성

```python
# services/issue_pool_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from models.issue_pool import IssuePool, Issue
from repositories.issue_pool_repository import IssuePoolRepository
from schemas.issue_pool import IssuePoolCreateRequest, IssuePoolResponse


class IssuePoolService:
    def __init__(
        self,
        repository: IssuePoolRepository
    ):
        self.repository = repository

    async def get_issue_pool(
        self,
        company_id: str
    ) -> IssuePoolResponse:
        """
        Get issue pool by company ID

        Args:
            company_id: Company identifier

        Returns:
            IssuePoolResponse

        Raises:
            HTTPException: If issue pool not found
        """
        issue_pool = await self.repository.find_by_company_id(company_id)

        if not issue_pool:
            raise HTTPException(
                status_code=404,
                detail=f"Issue pool not found for company: {company_id}"
            )

        return IssuePoolResponse.from_orm(issue_pool)

    async def generate_issue_pool(
        self,
        company_id: str,
        request: IssuePoolCreateRequest
    ) -> IssuePoolResponse:
        """
        Generate new issue pool

        Args:
            company_id: Company identifier
            request: Creation request

        Returns:
            IssuePoolResponse
        """
        # 1. 기존 이슈풀 확인
        existing = await self.repository.find_by_company_id(company_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Issue pool already exists for company: {company_id}"
            )

        # 2. 이슈풀 생성
        issue_pool = IssuePool(
            company_id=company_id,
            status="DRAFT"
        )

        # 3. 이슈 생성
        issues = self._create_issues_from_request(request, issue_pool)
        issue_pool.issues = issues

        # 4. 저장
        saved_pool = await self.repository.save(issue_pool)

        return IssuePoolResponse.from_orm(saved_pool)

    def _create_issues_from_request(
        self,
        request: IssuePoolCreateRequest,
        issue_pool: IssuePool
    ) -> List[Issue]:
        """Private helper method to create issues"""
        return []
```

### 7.3 Pydantic Schema 작성

```python
# schemas/issue_pool.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class IssuePoolStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class IssueBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., max_length=50)
    score: float = Field(..., ge=0, le=100)


class IssueCreateRequest(IssueBase):
    """Issue creation request schema"""
    pass


class IssueResponse(IssueBase):
    """Issue response schema"""
    id: int
    issue_pool_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class IssuePoolCreateRequest(BaseModel):
    """Issue pool creation request schema"""
    standard_types: List[str] = Field(
        ...,
        description="ESG standard types (GRI, SASB, TCFD)"
    )
    issues: List[IssueCreateRequest] = Field(
        default=[],
        description="Initial issues to create"
    )


class IssuePoolResponse(BaseModel):
    """Issue pool response schema"""
    id: int
    company_id: str
    status: IssuePoolStatus
    issues: List[IssueResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## 8. 예외 처리 표준

### 8.1 Spring Boot 예외 처리

```java
// ErrorCode.java (Enum)
@Getter
@RequiredArgsConstructor
public enum ErrorCode {
    // Common (CM)
    INVALID_INPUT_VALUE("CM001", "Invalid input value"),
    INTERNAL_SERVER_ERROR("CM999", "Internal server error"),

    // Issue Pool (ISS)
    ISSUE_POOL_NOT_FOUND("ISS001", "Issue pool not found"),
    ISSUE_POOL_ALREADY_EXISTS("ISS002", "Issue pool already exists"),

    // Authentication (AUTH)
    UNAUTHORIZED("AUTH001", "Unauthorized"),
    FORBIDDEN("AUTH002", "Forbidden");

    private final String code;
    private final String message;
}

// BusinessException.java
@Getter
public class BusinessException extends RuntimeException {
    private final ErrorCode errorCode;
    private final String details;

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
        this.details = null;
    }

    public BusinessException(ErrorCode errorCode, String details) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
        this.details = details;
    }
}

// GlobalExceptionHandler.java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(
            BusinessException e) {

        log.error("Business exception: {}", e.getMessage(), e);

        ErrorResponse error = ErrorResponse.builder()
            .code(e.getErrorCode().getCode())
            .message(e.getErrorCode().getMessage())
            .details(e.getDetails())
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity
            .status(HttpStatus.BAD_REQUEST)
            .body(ApiResponse.error(error));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception e) {
        log.error("Unexpected exception", e);

        ErrorResponse error = ErrorResponse.builder()
            .code(ErrorCode.INTERNAL_SERVER_ERROR.getCode())
            .message("An unexpected error occurred")
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(ApiResponse.error(error));
    }
}
```

---

## 9. 데이터베이스 표준

### 9.1 네이밍 규칙

| 항목 | 규칙 | 예시 |
|------|------|------|
| 테이블 | snake_case, 복수형 | `issue_pools`, `news_articles` |
| 컬럼 | snake_case | `company_id`, `created_at` |
| PK | `id` 또는 `<table>_id` | `id`, `issue_pool_id` |
| FK | `<referenced_table>_id` | `company_id`, `user_id` |
| Index | `idx_<table>_<column>` | `idx_issue_pools_company_id` |
| Constraint | `<type>_<table>_<column>` | `uk_users_email`, `fk_issues_pool` |

### 9.2 필수 컬럼

모든 테이블에 포함:

```sql
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
created_by VARCHAR(50),
updated_by VARCHAR(50)
```

---

## 10. 트랜잭션 관리

### 10.1 Spring Boot

```java
@Transactional(readOnly = true)  // 기본값 (읽기 전용)
public class MyService {

    @Transactional  // 쓰기 작업
    public void create() {
        // ...
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void separateTransaction() {
        // 별도 트랜잭션
    }
}
```

### 10.2 FastAPI (SQLAlchemy)

```python
async def create_issue_pool(session: AsyncSession, data: dict):
    async with session.begin():
        issue_pool = IssuePool(**data)
        session.add(issue_pool)
        await session.commit()
        await session.refresh(issue_pool)
        return issue_pool
```

---

## 11. 로깅 표준

### 11.1 로그 레벨

| Level | 용도 |
|-------|------|
| ERROR | 시스템 오류, 예외 |
| WARN | 경고 (복구 가능) |
| INFO | 주요 비즈니스 로직 흐름 |
| DEBUG | 상세 디버깅 정보 |
| TRACE | 매우 상세한 정보 |

### 11.2 로그 포맷

```java
// Spring Boot
log.info("Generating issue pool for company: {}", companyId);
log.error("Failed to generate issue pool: {}", e.getMessage(), e);
```

```python
# FastAPI
logger.info(f"Generating issue pool for company: {company_id}")
logger.error(f"Failed to generate issue pool: {str(e)}", exc_info=True)
```

---

## 12. 환경변수

### 12.1 Spring Boot (application.yml)

```yaml
spring:
  profiles:
    active: ${SPRING_PROFILE:local}
  datasource:
    url: ${DB_URL:jdbc:postgresql://localhost:5432/esgdb}
    username: ${DB_USERNAME:postgres}
    password: ${DB_PASSWORD:password}

app:
  api:
    base-url: ${API_BASE_URL:http://localhost:8000}
  security:
    jwt-secret: ${JWT_SECRET:changeme}
```

### 12.2 FastAPI (.env)

```bash
# .env.development
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/esgdb
VECTOR_DB_URL=http://localhost:6333
OPENAI_API_KEY=sk-...
JWT_SECRET=changeme

# .env.production
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/esgdb
VECTOR_DB_URL=http://qdrant:6333
OPENAI_API_KEY=${OPENAI_API_KEY}
JWT_SECRET=${JWT_SECRET}
```

---

## 13. 테스트 표준

### 13.1 Spring Boot

```java
@SpringBootTest
@Transactional
class IssuePoolServiceTest {

    @Autowired
    private IssuePoolService issuePoolService;

    @Autowired
    private IssuePoolRepository issuePoolRepository;

    @Test
    @DisplayName("이슈풀 생성 성공")
    void generateIssuePool_Success() {
        // Given
        String companyId = "ABC123";
        IssuePoolCreateRequest request = new IssuePoolCreateRequest();

        // When
        IssuePoolResponse response = issuePoolService.generateIssuePool(
            companyId,
            request
        );

        // Then
        assertThat(response).isNotNull();
        assertThat(response.getCompanyId()).isEqualTo(companyId);
    }
}
```

### 13.2 FastAPI (pytest)

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_generate_issue_pool_success(async_client: AsyncClient):
    # Given
    company_id = "ABC123"
    request_data = {
        "standard_types": ["GRI", "SASB"],
        "issues": []
    }

    # When
    response = await async_client.post(
        f"/api/v1/issue-pool/{company_id}/generate",
        json=request_data
    )

    # Then
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["data"]["company_id"] == company_id
```

---

## 14. Git & 커밋 메시지

### 14.1 브랜치 전략

- **main**: 운영 배포
- **feature/***: 기능 개발
- **fix/***: 버그 수정

### 14.2 커밋 메시지

```bash
<type>: <subject>

feat: 이슈풀 자동 생성 API 추가
fix: 이슈풀 조회 시 NPE 수정
refactor: IssuePoolService 레이어 분리
test: IssuePool 생성 테스트 추가
docs: API 문서 업데이트
```

---

## 15. AI 프롬프트 가이드

### 15.1 API 생성

```
[System]
You are a backend developer following SKALA ESG project standards.

[Task]
Create a new REST API endpoint: POST /api/v1/issue-pool/{companyId}/generate

[Requirements]
- Use Spring Boot with Layered Architecture
- Controller → Service → Repository
- Use @Valid for input validation
- Use BusinessException for errors
- Return standard ApiResponse wrapper
- Add logging with Slf4j
- Follow naming conventions (camelCase for methods)

[Response Format]
Provide complete code for:
1. Controller
2. Service (interface + impl)
3. Request/Response DTOs
4. Entity (if needed)
```

---

## 16. 금지 사항

❌ **절대 금지**:
- Controller에 비즈니스 로직
- 하드코딩된 URL, API 키
- printStackTrace() 사용
- DB 비밀번호 코드에 포함
- 트랜잭션 없는 쓰기 작업

✅ **반드시 준수**:
- Layered Architecture 준수
- 모든 API는 표준 Response Wrapper 사용
- 예외는 GlobalExceptionHandler에서 처리
- 환경변수로 설정 관리
- 로깅 필수

---

## 17. 체크리스트

API 개발 완료 전:

- [ ] Layered Architecture 준수
- [ ] 표준 Response Wrapper 사용
- [ ] 입력 검증 (@Valid 또는 Pydantic)
- [ ] 예외 처리 구현
- [ ] 로깅 추가
- [ ] 트랜잭션 설정 적절
- [ ] 테스트 코드 작성
- [ ] API 문서화
- [ ] 환경변수 사용 (하드코딩 없음)
- [ ] Git 커밋 메시지 규칙 준수

---

**문서 버전**: 1.0
**최종 수정일**: 2025-11-18
**작성자**: SKALA 2기 7조

---

## 21. ESG 프로젝트 특화 규칙

### 21.1 API 엔드포인트 구조 (FSD 기반)

#### 21.1.1 Issue Pool API
```java
// Issue Pool 생성 (20 Topic 제한)
POST /api/v1/issue-pool/{companyId}/generate
Response: { "topics": [...], "count": 18 }  // MAX 20

// 이해관계자 설문 제출
POST /api/v1/issue-pool/{companyId}/survey
Request: { "selectedIssues": [1,2,3,4,5], "scores": {...} }  // 5개 선택

// 중대성 평가 결과
GET /api/v1/issue-pool/{companyId}/materiality
Response: { "matrix": { "x": [...], "y": [...] }, "coreIssues": [...] }
```

#### 21.1.2 Report API
```java
// AI 초안 생성 (Report Assistant 전용)
POST /api/v1/report/{companyId}/draft
Request: { "year": 2024, "sections": ["governance", "strategy"] }

// 전년도 비교 데이터
GET /api/v1/report/{companyId}/compare?current=2024&previous=2023
```

#### 21.1.3 Carbon Credit API
```java
// 탄소배출권 거래 신호
GET /api/v1/carbon/signals?company={id}
Response: { "signal": "BUY"|"SELL"|"HOLD", "confidence": 0.85 }
```

### 21.2 에러 코드 체계 (FSD Section 10)

#### 21.2.1 ErrorCode Enum
```java
// ErrorCode.java
public enum ESGErrorCode {
    // 표준문서 (STD)
    STD_VAL_001("ESG-STD-VAL-001", "표준 문서 포맷 오류"),
    STD_VAL_002("ESG-STD-VAL-002", "표준 문서 버전 불일치"),
    
    // 내부분석 (INT)
    INT_VAL_001("ESG-INT-VAL-001", "KPI 데이터 형식 오류"),
    INT_VAL_002("ESG-INT-VAL-002", "Data Hub 연동 실패"),
    
    // 벤치마킹 (BMK)
    BMK_CRAWL_001("ESG-BMK-CRAWL-001", "타 기업 보고서 크롤링 실패"),
    BMK_VAL_001("ESG-BMK-VAL-001", "벤치마킹 데이터 포맷 오류"),
    
    // 미디어분석 (MED)
    MED_SEARCH_001("ESG-MED-SEARCH-001", "뉴스 검색 API 오류"),
    MED_VAL_001("ESG-MED-VAL-001", "뉴스 데이터 파싱 오류"),
    
    // 뉴스인텔리전스 (NWS)
    NWS_RETENTION_001("ESG-NWS-RETENTION-001", "2년 보관 정책 위반"),
    
    // 이해관계자설문 (SVY)
    SVY_VAL_001("ESG-SVY-VAL-001", "5개 이슈 선택 제한 위반"),
    SVY_VAL_002("ESG-SVY-VAL-002", "1-3점 평가 범위 초과"),
    
    // 중대성평가 (MAT)
    MAT_LIMIT_001("ESG-MAT-LIMIT-001", "20개 Topic 제한 초과"),
    MAT_VAL_001("ESG-MAT-VAL-001", "재무/영향 점수 범위 오류"),
    
    // 보고서작성 (RPT)
    RPT_AI_001("ESG-RPT-AI-001", "AI 초안 생성 실패"),
    RPT_VAL_001("ESG-RPT-VAL-001", "보고서 포맷 검증 실패"),
    
    // RAG Chatbot (CHAT)
    CHAT_RAG_001("ESG-CHAT-RAG-001", "RAG 컨텍스트 검색 실패"),
    CHAT_LLM_001("ESG-CHAT-LLM-001", "LLM API 호출 실패"),
    
    // 탄소배출권 (CRB)
    CRB_PRED_001("ESG-CRB-PRED-001", "가격 예측 모델 오류"),
    CRB_VAL_001("ESG-CRB-VAL-001", "탄소 데이터 형식 오류");
    
    private final String code;
    private final String message;
    
    ESGErrorCode(String code, String message) {
        this.code = code;
        this.message = message;
    }
}
```

#### 21.2.2 Exception Handler
```java
@ControllerAdvice
public class ESGExceptionHandler {
    
    @ExceptionHandler(TopicLimitExceededException.class)
    public ResponseEntity<ApiResponse<Void>> handleTopicLimit(
        TopicLimitExceededException ex) {
        return ResponseEntity.badRequest().body(
            ApiResponse.error(
                ESGErrorCode.MAT_LIMIT_001.getCode(),
                "20개 Topic 제한을 초과했습니다.",
                Map.of("current", ex.getCurrentCount(), "max", 20)
            )
        );
    }
    
    @ExceptionHandler(SurveyValidationException.class)
    public ResponseEntity<ApiResponse<Void>> handleSurveyValidation(
        SurveyValidationException ex) {
        return ResponseEntity.badRequest().body(
            ApiResponse.error(
                ESGErrorCode.SVY_VAL_001.getCode(),
                "5개 이슈만 선택 가능합니다.",
                Map.of("selected", ex.getSelectedCount())
            )
        );
    }
}
```

### 21.3 Domain Model (ESG 특화)

#### 21.3.1 Issue Pool Entity
```java
@Entity
@Table(name = "issue_pool")
public class IssuePool {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String companyId;
    
    @Column(nullable = false)
    private Integer year;
    
    @OneToMany(mappedBy = "issuePool", cascade = CascadeType.ALL)
    @Size(max = 20, message = "Topic은 최대 20개까지 생성 가능합니다")
    private List<Topic> topics = new ArrayList<>();
    
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}

@Entity
@Table(name = "topics")
public class Topic {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "issue_pool_id", nullable = false)
    private IssuePool issuePool;
    
    @Column(nullable = false)
    private String title;
    
    @Column(columnDefinition = "TEXT")
    private String description;
    
    @Column(name = "financial_score")
    @DecimalMin("0.0") @DecimalMax("10.0")
    private Double financialScore;  // X축 (재무 점수)
    
    @Column(name = "impact_score")
    @DecimalMin("0.0") @DecimalMax("10.0")
    private Double impactScore;  // Y축 (영향 점수)
    
    @Column(name = "is_core_issue")
    private Boolean isCoreIssue = false;  // 20개 핵심 이슈 여부
    
    @Column(name = "data_hub_linked")
    private Boolean dataHubLinked = false;  // Data Hub 연계 여부
}
```

#### 21.3.2 Stakeholder Survey Entity
```java
@Entity
@Table(name = "stakeholder_surveys")
public class StakeholderSurvey {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String companyId;
    
    @Column(nullable = false)
    private String stakeholderEmail;
    
    @ElementCollection
    @CollectionTable(name = "survey_issue_scores")
    @MapKeyColumn(name = "issue_id")
    @Column(name = "score")
    @Size(min = 5, max = 5, message = "정확히 5개 이슈를 선택해야 합니다")
    private Map<Long, Integer> issueScores = new HashMap<>();  // 1-3점 평가
    
    @Column(name = "submitted_at")
    private LocalDateTime submittedAt;
}
```

#### 21.3.3 News Intelligence Entity
```java
@Entity
@Table(name = "news_intelligence")
public class NewsIntelligence {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String companyId;
    
    @Column(columnDefinition = "TEXT")
    private String title;
    
    @Column(columnDefinition = "TEXT")
    private String content;
    
    @Column(name = "published_at")
    private LocalDateTime publishedAt;
    
    @Column(name = "collected_at")
    private LocalDateTime collectedAt;
    
    @Column(name = "retention_until")
    private LocalDateTime retentionUntil;  // 수집일 + 2년 자동 계산
    
    @PrePersist
    public void calculateRetention() {
        this.collectedAt = LocalDateTime.now();
        this.retentionUntil = this.collectedAt.plusYears(2);
    }
}
```

### 21.4 Business Logic Validation

#### 21.4.1 Topic Limit Validator
```java
@Service
@RequiredArgsConstructor
public class IssuePoolService {
    
    private static final int MAX_TOPIC_COUNT = 20;
    private static final int MAX_CORE_ISSUE_COUNT = 20;
    
    public IssuePoolResponse generateIssuePool(String companyId) {
        // AI로 Topic 생성
        List<Topic> generatedTopics = aiService.generateTopics(companyId);
        
        // 20개 제한 검증
        if (generatedTopics.size() > MAX_TOPIC_COUNT) {
            throw new TopicLimitExceededException(
                ESGErrorCode.MAT_LIMIT_001,
                generatedTopics.size()
            );
        }
        
        // 저장 및 반환
        IssuePool issuePool = issuePoolRepository.save(
            new IssuePool(companyId, generatedTopics)
        );
        
        return IssuePoolResponse.from(issuePool);
    }
}
```

#### 21.4.2 Survey Validator
```java
@Service
public class SurveyService {
    
    private static final int REQUIRED_ISSUE_COUNT = 5;
    private static final int MIN_SCORE = 1;
    private static final int MAX_SCORE = 3;
    
    public void submitSurvey(SurveyRequest request) {
        // 5개 이슈 선택 검증
        if (request.getIssueScores().size() != REQUIRED_ISSUE_COUNT) {
            throw new SurveyValidationException(
                ESGErrorCode.SVY_VAL_001,
                "정확히 5개 이슈를 선택해야 합니다"
            );
        }
        
        // 1-3점 범위 검증
        request.getIssueScores().values().forEach(score -> {
            if (score < MIN_SCORE || score > MAX_SCORE) {
                throw new SurveyValidationException(
                    ESGErrorCode.SVY_VAL_002,
                    "점수는 1-3점 범위여야 합니다"
                );
            }
        });
        
        // 저장
        stakeholderSurveyRepository.save(
            StakeholderSurvey.from(request)
        );
    }
}
```

### 21.5 Data Hub 연계

#### 21.5.1 Data Hub Integration Service
```java
@Service
@RequiredArgsConstructor
public class DataHubIntegrationService {
    
    private final RestTemplate restTemplate;
    
    @Value("${datahub.api.url}")
    private String dataHubUrl;
    
    public Optional<DataHubKPI> fetchKPI(String companyId, String kpiCode) {
        try {
            String url = String.format("%s/api/kpi/%s/%s", 
                dataHubUrl, companyId, kpiCode);
            
            DataHubKPI response = restTemplate.getForObject(
                url, DataHubKPI.class
            );
            
            return Optional.ofNullable(response);
            
        } catch (Exception e) {
            log.error("Data Hub 연동 실패: {}", e.getMessage());
            throw new DataHubException(
                ESGErrorCode.INT_VAL_002,
                "Data Hub에서 KPI 데이터를 가져올 수 없습니다"
            );
        }
    }
    
    public void markTopicAsDataHubLinked(Long topicId) {
        Topic topic = topicRepository.findById(topicId)
            .orElseThrow(() -> new EntityNotFoundException("Topic not found"));
        
        topic.setDataHubLinked(true);
        topicRepository.save(topic);
    }
}
```

### 21.6 Report Generation (Year-over-Year Comparison)

#### 21.6.1 Report Comparison Service
```java
@Service
@RequiredArgsConstructor
public class ReportComparisonService {
    
    public ReportComparisonResponse compareYears(
        String companyId, int currentYear, int previousYear) {
        
        Report currentReport = reportRepository
            .findByCompanyIdAndYear(companyId, currentYear)
            .orElseThrow(() -> new EntityNotFoundException(
                "현재 연도 보고서를 찾을 수 없습니다"
            ));
        
        Report previousReport = reportRepository
            .findByCompanyIdAndYear(companyId, previousYear)
            .orElseThrow(() -> new EntityNotFoundException(
                "전년도 보고서를 찾을 수 없습니다"
            ));
        
        // 전년 대비 변화 계산
        Map<String, ComparisonMetric> metrics = new HashMap<>();
        
        // 예: 탄소 배출량 비교
        metrics.put("carbonEmissions", ComparisonMetric.builder()
            .current(currentReport.getCarbonEmissions())
            .previous(previousReport.getCarbonEmissions())
            .change(calculateChange(
                currentReport.getCarbonEmissions(),
                previousReport.getCarbonEmissions()
            ))
            .build()
        );
        
        return ReportComparisonResponse.builder()
            .currentYear(currentYear)
            .previousYear(previousYear)
            .metrics(metrics)
            .build();
    }
    
    private Double calculateChange(Double current, Double previous) {
        if (previous == 0) return 0.0;
        return ((current - previous) / previous) * 100;
    }
}
```

### 21.7 Carbon Credit Signal Service

#### 21.7.1 Trading Signal Service
```java
@Service
@RequiredArgsConstructor
public class CarbonTradingSignalService {
    
    private final CarbonPredictionService predictionService;
    
    public enum TradingSignal {
        BUY, SELL, HOLD
    }
    
    public TradingSignalResponse generateSignal(String companyId) {
        // 가격 예측
        CarbonPricePrediction prediction = 
            predictionService.predictPrice(companyId);
        
        // 거래 신호 생성
        TradingSignal signal = determineSignal(prediction);
        
        return TradingSignalResponse.builder()
            .signal(signal)
            .confidence(prediction.getConfidence())
            .predictedPrice(prediction.getPrice())
            .currentPrice(prediction.getCurrentPrice())
            .recommendation(generateRecommendation(signal, prediction))
            .build();
    }
    
    private TradingSignal determineSignal(CarbonPricePrediction prediction) {
        double priceChange = prediction.getPrice() - prediction.getCurrentPrice();
        double changePercent = (priceChange / prediction.getCurrentPrice()) * 100;
        
        if (changePercent > 5.0 && prediction.getConfidence() > 0.7) {
            return TradingSignal.BUY;
        } else if (changePercent < -5.0 && prediction.getConfidence() > 0.7) {
            return TradingSignal.SELL;
        } else {
            return TradingSignal.HOLD;
        }
    }
}
```

### 21.8 AI Chatbot vs Report Assistant 분리

#### 21.8.1 Service Interface
```java
public interface AIAssistantService {
    AIResponse chat(String companyId, String userMessage);
    boolean canHandleReportWriting();
}

@Service("esgChatbot")
public class ESGChatbotService implements AIAssistantService {
    
    @Override
    public AIResponse chat(String companyId, String userMessage) {
        // RAG 기반 일반 ESG 질의응답
        List<String> context = ragService.retrieveContext(userMessage);
        
        String prompt = String.format("""
            [SYSTEM]
            You are an ESG expert chatbot.
            
            [CONTEXT]
            %s
            
            [USER QUESTION]
            %s
            
            [TASK]
            Answer the question based on context.
            """, String.join("\n", context), userMessage);
        
        return llmService.chat(prompt);
    }
    
    @Override
    public boolean canHandleReportWriting() {
        return false;  // ESG Chatbot은 보고서 작성 불가
    }
}

@Service("reportAssistant")
public class ReportAssistantService implements AIAssistantService {
    
    @Override
    public AIResponse chat(String companyId, String userMessage) {
        // 보고서 작성 전용
        if (!isReportWritingRequest(userMessage)) {
            throw new UnsupportedOperationException(
                "Report Assistant는 보고서 작성만 지원합니다. " +
                "일반 질문은 ESG Chatbot을 이용하세요."
            );
        }
        
        return generateReportDraft(companyId, userMessage);
    }
    
    @Override
    public boolean canHandleReportWriting() {
        return true;
    }
    
    private AIResponse generateReportDraft(String companyId, String request) {
        // 보고서 초안 생성 로직
        // ...
    }
}
```

### 21.9 News Retention Policy (2년 보관)

#### 21.9.1 Scheduled Cleanup
```java
@Component
@RequiredArgsConstructor
public class NewsRetentionScheduler {
    
    private final NewsIntelligenceRepository newsRepository;
    
    @Scheduled(cron = "0 0 2 * * ?")  // 매일 새벽 2시 실행
    public void cleanupExpiredNews() {
        LocalDateTime now = LocalDateTime.now();
        
        List<NewsIntelligence> expiredNews = 
            newsRepository.findByRetentionUntilBefore(now);
        
        log.info("만료된 뉴스 {}건 삭제 시작", expiredNews.size());
        
        newsRepository.deleteAll(expiredNews);
        
        log.info("뉴스 정리 완료");
    }
}
```

### 21.10 Benchmarking Crawling Service

#### 21.10.1 Report Crawler
```java
@Service
@RequiredArgsConstructor
public class BenchmarkingCrawlerService {
    
    public List<BenchmarkReport> crawlCompetitorReports(
        String industry, int year) {
        
        List<BenchmarkReport> reports = new ArrayList<>();
        
        try {
            // 타 기업 보고서 자동 크롤링
            List<String> reportUrls = findReportUrls(industry, year);
            
            for (String url : reportUrls) {
                BenchmarkReport report = crawlReport(url);
                reports.add(report);
            }
            
            return reports;
            
        } catch (Exception e) {
            log.error("벤치마킹 크롤링 실패: {}", e.getMessage());
            throw new BenchmarkingException(
                ESGErrorCode.BMK_CRAWL_001,
                "타 기업 보고서 크롤링에 실패했습니다"
            );
        }
    }
    
    private BenchmarkReport crawlReport(String url) throws IOException {
        Document doc = Jsoup.connect(url).get();
        
        return BenchmarkReport.builder()
            .url(url)
            .title(doc.select("title").text())
            .content(extractESGContent(doc))
            .crawledAt(LocalDateTime.now())
            .build();
    }
}
```

---

## 22. 체크리스트 (ESG 프로젝트)

### 22.1 Issue Pool 개발 체크리스트

- [ ] 20 Topic 제한 검증 로직 구현
- [ ] Topic 생성 시 MAX_TOPIC_COUNT 상수 사용
- [ ] 5개 이슈 선택 제한 검증
- [ ] 1-3점 평가 범위 검증
- [ ] Double Materiality Matrix 계산 로직
- [ ] Data Hub 연계 표시 필드 추가
- [ ] ESG 에러 코드 체계 적용

### 22.2 Report API 체크리스트

- [ ] 전년 대비 비교 API 구현
- [ ] Report Assistant와 ESG Chatbot 분리
- [ ] AI 초안 생성 실패 시 ESG-RPT-AI-001 에러 반환
- [ ] 보고서 포맷 검증 로직

### 22.3 News Intelligence 체크리스트

- [ ] 2년 보관 정책 자동 적용 (retention_until)
- [ ] 만료 뉴스 삭제 스케줄러 구현
- [ ] 뉴스 수집 시 collected_at 자동 기록

### 22.4 Carbon Credit 체크리스트

- [ ] 거래 신호 생성 로직 (BUY/SELL/HOLD)
- [ ] 신뢰도(confidence) 계산
- [ ] 가격 예측 모델 연동

### 22.5 공통 체크리스트

- [ ] 모든 도메인 에러에 ESG-<MODULE>-<TYPE>-<NUMBER> 형식 적용
- [ ] ApiResponse Wrapper에 error.code, error.message, error.details 포함
- [ ] RESTful API 경로 규칙 준수 (/api/v1/...)
- [ ] Transaction 관리 (@Transactional)
- [ ] 로깅 표준 준수 (SLF4J)

---

**이 섹션은 FSD(기능 상세 설계서) 기반 ESG 프로젝트 특화 규칙을 정의합니다.**
**기본 백엔드 표준(Section 1-20)과 함께 사용하세요.**

