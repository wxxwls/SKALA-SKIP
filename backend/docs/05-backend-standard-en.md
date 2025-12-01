# Backend Development Standard

**ESG Issue Pool Construction AI System**
**Version 1.0**
**SKALA Team 7**

---

## Document Overview

This document defines the **Backend Development Standard** for the ESG Double Materiality Issue Pool Automatic Construction Service.

**Purpose**: To provide unified rules to prevent conflicts, inconsistencies, and errors during final code merging when multiple developers use AI for concurrent development.

**Target**: Spring Boot (Java) and FastAPI (Python) backend development

---

## 1. Tech Stack and Version Pinning

### 1.1 Spring Boot Stack

```json
{
  "framework": "Spring Boot 3.2.x",
  "java": "Java 17 LTS",
  "buildTool": "Gradle 8.x",
  "database": "PostgreSQL 15.x",
  "orm": "Spring Data JPA / Hibernate",
  "security": "Spring Security 6.x",
  "testing": "JUnit 5, Mockito"
}
```

### 1.2 FastAPI Stack

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

---

## 2. Layered Architecture

```
Controller/API Layer
    ↓ (DTO/Schema)
Service Layer
    ↓ (Entity/Model)
Repository Layer
    ↓
Database
```

### Layer Responsibilities

- **Controller/API**: HTTP handling, DTO conversion, input validation
- **Service**: Business logic, transaction management
- **Repository**: Data access, CRUD operations

---

## 3. Naming Conventions

### 3.1 Java (Spring Boot)

```java
// Classes
public class IssuePoolController { }  // <Domain><Type>
public interface IssuePoolService { }
public class IssuePoolServiceImpl implements IssuePoolService { }
public class IssuePoolCreateRequest { }

// Variables & Methods
private String companyId;  // camelCase
public IssuePool generateIssuePool() { }  // verb first

// Constants
public static final int DEFAULT_PAGE_SIZE = 20;  // UPPER_SNAKE_CASE
```

### 3.2 Python (FastAPI)

```python
# Files
issue_pool_service.py  # snake_case

# Classes
class IssuePoolService:  # PascalCase
    pass

# Functions & Variables
def generate_issue_pool(company_id: str):  # snake_case
    pass

# Constants
DEFAULT_PAGE_SIZE = 20  # UPPER_SNAKE_CASE
```

---

## 4. API Standards

### 4.1 REST API URL Rules

```
Format: /api/v1/{resource}/{id}/{action}

Examples:
GET    /api/v1/issue-pool/{companyId}
POST   /api/v1/issue-pool/{companyId}/generate
GET    /api/v1/news/feed?companyId=123&days=7
```

**Rules**:
- Use kebab-case
- Noun-based resource names
- HTTP methods for actions (GET, POST, PUT, PATCH, DELETE)
- Version management (/v1, /v2)

### 4.2 Standard Response Wrapper

**Success**:
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-01-18T10:30:00Z"
}
```

**Error**:
```json
{
  "success": false,
  "error": {
    "code": "ISS001",
    "message": "Issue pool not found",
    "details": "Company ID: ABC123",
    "timestamp": "2025-01-18T10:30:00Z"
  }
}
```

---

## 5. Exception Handling

### 5.1 Spring Boot

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(
            BusinessException e) {
        // Handle and return error response
    }
}
```

### 5.2 FastAPI

```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": str(exc.status_code),
                "message": exc.detail
            }
        }
    )
```

---

## 6. Database Standards

### 6.1 Naming Rules

| Item | Rule | Example |
|------|------|---------|
| Table | snake_case, plural | `issue_pools`, `news_articles` |
| Column | snake_case | `company_id`, `created_at` |
| PK | `id` or `<table>_id` | `id`, `issue_pool_id` |
| FK | `<referenced_table>_id` | `company_id`, `user_id` |

### 6.2 Required Columns

All tables must include:
```sql
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
```

---

## 7. Testing Standards

### 7.1 Spring Boot (JUnit)

```java
@SpringBootTest
@Transactional
class IssuePoolServiceTest {
    @Test
    @DisplayName("Generate issue pool successfully")
    void generateIssuePool_Success() {
        // Given
        // When
        // Then
    }
}
```

### 7.2 FastAPI (pytest)

```python
@pytest.mark.asyncio
async def test_generate_issue_pool_success(async_client):
    # Given
    # When
    # Then
    assert response.status_code == 201
```

---

## 8. Prohibited Practices

❌ **Forbidden**:
- Business logic in Controller
- Hardcoded URLs, API keys
- Using printStackTrace()
- Database passwords in code

✅ **Mandatory**:
- Follow Layered Architecture
- Use standard Response Wrapper
- Handle exceptions globally
- Manage configs via environment variables

---

**Document Version**: 1.0
**Last Modified**: 2025-11-18
**Author**: SKALA Team 7

---

## 21. ESG Project-Specific Rules

### 21.1 Error Code System (FSD-Based)

```java
public enum ESGErrorCode {
    // Standard Document (STD)
    STD_VAL_001("ESG-STD-VAL-001", "Standard document format error"),
    
    // Internal Analysis (INT)
    INT_VAL_001("ESG-INT-VAL-001", "KPI data format error"),
    INT_VAL_002("ESG-INT-VAL-002", "Data Hub integration failed"),
    
    // Benchmarking (BMK)
    BMK_CRAWL_001("ESG-BMK-CRAWL-001", "Report crawling failed"),
    
    // Survey (SVY)
    SVY_VAL_001("ESG-SVY-VAL-001", "Must select exactly 5 issues"),
    SVY_VAL_002("ESG-SVY-VAL-002", "Score must be between 1-3"),
    
    // Materiality Assessment (MAT)
    MAT_LIMIT_001("ESG-MAT-LIMIT-001", "Topic limit (20) exceeded"),
    
    // Report (RPT)
    RPT_AI_001("ESG-RPT-AI-001", "AI draft generation failed"),
    
    // Chatbot (CHAT)
    CHAT_RAG_001("ESG-CHAT-RAG-001", "RAG context retrieval failed"),
    
    // Carbon (CRB)
    CRB_PRED_001("ESG-CRB-PRED-001", "Price prediction model error");
}
```

### 21.2 Domain Constraints

```java
// 20 Topic Limit
@Entity
@Table(name = "issue_pool")
public class IssuePool {
    @OneToMany(cascade = CascadeType.ALL)
    @Size(max = 20, message = "Maximum 20 topics allowed")
    private List<Topic> topics;
}

// 5 Issue Selection in Survey
@Entity
public class StakeholderSurvey {
    @ElementCollection
    @Size(min = 5, max = 5, message = "Must select exactly 5 issues")
    private Map<Long, Integer> issueScores;  // Score: 1-3
}

// 2-Year News Retention
@Entity
public class NewsIntelligence {
    @Column(name = "retention_until")
    private LocalDateTime retentionUntil;
    
    @PrePersist
    public void setRetention() {
        this.retentionUntil = LocalDateTime.now().plusYears(2);
    }
}
```

### 21.3 API Endpoints

```java
// Issue Pool
POST /api/v1/issue-pool/{companyId}/generate  // Max 20 topics
POST /api/v1/issue-pool/{companyId}/survey    // 5 issues, 1-3 scores

// Report
POST /api/v1/report/{companyId}/draft
GET /api/v1/report/{companyId}/compare?current=2024&previous=2023

// Carbon
GET /api/v1/carbon/signals  // Returns BUY/SELL/HOLD signal
```

### 21.4 Service Separation

```java
@Service("esgChatbot")
public class ESGChatbotService {
    // General ESG Q&A only
    public boolean canHandleReportWriting() {
        return false;
    }
}

@Service("reportAssistant")
public class ReportAssistantService {
    // Report writing only
    public boolean canHandleReportWriting() {
        return true;
    }
}
```

### 21.5 Checklist

- [ ] 20 Topic limit validation
- [ ] 5 Issue selection in survey
- [ ] 1-3 score range validation
- [ ] ESG error code format: ESG-<MODULE>-<TYPE>-<NUMBER>
- [ ] 2-year news retention policy
- [ ] Year-over-year report comparison
- [ ] Data Hub linkage indicator
- [ ] Chatbot/Report Assistant separation

---

**This section defines ESG project-specific rules based on the Functional Specification Document (FSD).**

