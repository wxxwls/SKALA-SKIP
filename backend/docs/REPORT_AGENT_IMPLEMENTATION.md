# 보고서 초안 생성 기능 구현 문서

## 개요

Spring Boot에서 FastAPI로 AI 보고서 초안 생성 요청을 보내는 기능을 구현했습니다.  
이 문서는 구현된 각 컴포넌트의 **이유**와 **구현 방식**을 설명합니다.

---

## 1. 설정 파일 변경

### 1.1 application.yml

**위치**: `src/main/resources/application.yml`

**추가된 내용**:
```yaml
# FastAPI Base URL Configuration
fastapi:
  base-url: ${FASTAPI_BASE_URL:http://localhost:8000}
```

**이유**:
- FastAPI 서버의 기본 URL을 환경 변수로 관리하여 유연성 확보
- 개발/운영 환경별로 다른 URL 사용 가능
- 하드코딩 방지 (보안 및 유지보수성 향상)

**구현 방식**:
- 기존 `app.fastapi.base-url` 설정은 유지 (다른 용도로 사용 가능)
- 새로운 `fastapi.base-url` 설정 추가 (WebClient 전용)
- 환경 변수 `FASTAPI_BASE_URL`로 오버라이드 가능

### 1.2 application-dev.yml

**위치**: `src/main/resources/application-dev.yml`

**추가된 내용**:
```yaml
# FastAPI Base URL Configuration
fastapi:
  base-url: http://localhost:8000  # 필요 시 dev 전용 주소로 변경
```

**이유**:
- 개발 환경에서 로컬 FastAPI 서버(포트 8000) 사용
- 프로덕션과 분리된 설정 관리

**구현 방식**:
- dev 프로필에서 `fastapi.base-url` 오버라이드
- 주석으로 변경 가능성 명시

---

## 2. 공통 클래스 생성

### 2.1 ApiResponse.java

**위치**: `src/main/java/com/skala/skip/common/dto/ApiResponse.java`

**이유**:
- **표준화된 응답 형식**: 모든 API가 동일한 구조로 응답하여 프론트엔드 처리 일관성 확보
- **에러 처리 통일**: 성공/실패 응답을 동일한 구조로 반환
- **타임스탬프 포함**: 디버깅 및 로깅에 유용

**구현 방식**:
```java
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {
    private Boolean success;
    private T data;
    private ErrorResponse error;
    private LocalDateTime timestamp;

    public static <T> ApiResponse<T> success(T data) { ... }
    public static <T> ApiResponse<T> error(ErrorResponse error) { ... }
}
```

**특징**:
- 제네릭 타입 `<T>`로 다양한 데이터 타입 지원
- `@JsonInclude(NON_NULL)`로 null 필드 제외하여 응답 크기 최적화
- 정적 팩토리 메서드로 간편한 생성

**사용 예시**:
```java
// 성공 응답
return ResponseEntity.ok(ApiResponse.success(reportDraftResponse));

// 에러 응답 (GlobalExceptionHandler에서 처리)
return ResponseEntity.badRequest()
    .body(ApiResponse.error(errorResponse));
```

---

### 2.2 ErrorResponse.java

**위치**: `src/main/java/com/skala/skip/common/dto/ErrorResponse.java`

**이유**:
- **에러 정보 구조화**: 코드, 메시지, 상세 정보를 체계적으로 관리
- **디버깅 용이성**: 타임스탬프와 상세 정보로 문제 추적 가능
- **프론트엔드 처리**: 에러 코드로 클라이언트에서 적절한 처리 가능

**구현 방식**:
```java
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ErrorResponse {
    private String code;              // ESG-RPT-AI-001 형식
    private String message;           // 사용자 친화적 메시지
    private String details;           // 추가 상세 정보
    private LocalDateTime timestamp;  // 에러 발생 시각
}
```

**특징**:
- Builder 패턴으로 선택적 필드 설정 가능
- 타임스탬프로 에러 발생 시점 추적

---

### 2.3 ESGErrorCode.java

**위치**: `src/main/java/com/skala/skip/common/exception/ESGErrorCode.java`

**이유**:
- **에러 코드 표준화**: `ESG-<MODULE>-<TYPE>-<NUMBER>` 형식으로 일관성 유지
- **모듈별 분리**: RPT(Report), MAT(Materiality) 등 도메인별 관리
- **국제화 가능**: 에러 코드로 다국어 메시지 매핑 가능
- **로깅 및 모니터링**: 에러 코드로 통계 및 알림 설정 가능

**구현 방식**:
```java
@Getter
@RequiredArgsConstructor
public enum ESGErrorCode {
    // 보고서작성 (RPT)
    RPT_AI_001("ESG-RPT-AI-001", "AI 초안 생성 실패"),
    RPT_VAL_001("ESG-RPT-VAL-001", "보고서 포맷 검증 실패"),
    RPT_CLIENT_001("ESG-RPT-CLIENT-001", "FastAPI 클라이언트 호출 실패"),
    RPT_CLIENT_002("ESG-RPT-CLIENT-002", "FastAPI 응답 파싱 실패"),

    // 공통 시스템 에러
    INTERNAL_SERVER_ERROR("ESG-SYS-001", "내부 서버 오류가 발생했습니다.");
    
    private final String code;
    private final String message;
}
```

**에러 코드 명명 규칙**:
- `RPT_AI_001`: Report 모듈, AI 관련, 001번 에러
- `RPT_CLIENT_001`: Report 모듈, Client 호출 관련, 001번 에러
- `INTERNAL_SERVER_ERROR`: 시스템 공통 에러

**사용 예시**:
```java
throw new BusinessException(ESGErrorCode.RPT_AI_001, "FastAPI 응답 없음");
```

---

### 2.4 BusinessException.java

**위치**: `src/main/java/com/skala/skip/common/exception/BusinessException.java`

**이유**:
- **비즈니스 로직 예외 분리**: 시스템 예외와 비즈니스 예외를 구분
- **에러 코드 연동**: ESGErrorCode와 함께 사용하여 일관된 에러 처리
- **상세 정보 포함**: details 필드로 추가 컨텍스트 제공

**구현 방식**:
```java
@Getter
public class BusinessException extends RuntimeException {
    private final ESGErrorCode errorCode;
    private final String details;

    public BusinessException(ESGErrorCode errorCode) { ... }
    public BusinessException(ESGErrorCode errorCode, String details) { ... }
    public BusinessException(ESGErrorCode errorCode, String details, Throwable cause) { ... }
}
```

**특징**:
- `RuntimeException` 상속으로 체크 예외 불필요
- 에러 코드와 상세 정보를 함께 관리
- 원인 예외(cause) 포함 가능

**사용 예시**:
```java
// 간단한 에러
throw new BusinessException(ESGErrorCode.RPT_AI_001);

// 상세 정보 포함
throw new BusinessException(ESGErrorCode.RPT_AI_001, "FastAPI 응답 없음");

// 원인 예외 포함
throw new BusinessException(ESGErrorCode.RPT_CLIENT_001, "연결 실패", e);
```

---

### 2.5 GlobalExceptionHandler.java

**위치**: `src/main/java/com/skala/skip/common/exception/GlobalExceptionHandler.java`

**이유**:
- **중앙 집중식 예외 처리**: 모든 컨트롤러의 예외를 한 곳에서 처리
- **일관된 에러 응답**: 모든 API가 동일한 형식으로 에러 반환
- **로깅 통합**: 예외 발생 시 일관된 로깅 처리

**구현 방식**:
```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException e) {
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
        // ... 시스템 에러 처리
    }
}
```

**특징**:
- `@RestControllerAdvice`: 모든 컨트롤러에 적용
- `BusinessException`: 400 Bad Request로 처리 (비즈니스 로직 위반)
- `Exception`: 500 Internal Server Error로 처리 (시스템 오류)
- 모든 예외를 `ApiResponse` 형식으로 변환

**처리 흐름**:
```
Controller → Service → Exception 발생
    ↓
GlobalExceptionHandler가 예외 캐치
    ↓
ErrorResponse 생성
    ↓
ApiResponse.error()로 래핑
    ↓
HTTP 응답 반환
```

---

## 3. WebClient 설정

### 3.1 WebClientConfig.java

**위치**: `src/main/java/com/skala/skip/config/WebClientConfig.java`

**이유**:
- **중앙 집중식 HTTP 클라이언트**: 모든 외부 API 호출을 통일된 클라이언트로 관리
- **설정 재사용**: 타임아웃, 기본 헤더 등을 한 곳에서 관리
- **Bean으로 등록**: 의존성 주입으로 테스트 및 모킹 용이

**구현 방식**:
```java
@Configuration
public class WebClientConfig {

    @Value("${fastapi.base-url}")
    private String fastApiBaseUrl;

    @Bean
    public WebClient fastApiWebClient() {
        HttpClient httpClient = HttpClient.create()
                .responseTimeout(Duration.ofSeconds(30));

        return WebClient.builder()
                .baseUrl(fastApiBaseUrl)
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .defaultHeader("Content-Type", "application/json")
                .build();
    }
}
```

**특징**:
- `@Value`로 설정 파일에서 base-url 주입
- 30초 응답 타임아웃 설정
- 기본 Content-Type 헤더 설정
- Reactor 기반 비동기 HTTP 클라이언트

**사용 예시**:
```java
@RequiredArgsConstructor
public class ReportAgentClient {
    private final WebClient fastApiWebClient;  // 주입받아 사용
    
    public Mono<ReportDraftResponse> generateDraftReport(...) {
        return fastApiWebClient
                .post()
                .uri("/api/v1/report/{companyId}/draft", companyId)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(ReportDraftResponse.class);
    }
}
```

---

## 4. Report Agent 도메인 구현

### 4.1 DTO 클래스

#### 4.1.1 ReportDraftRequest.java

**위치**: `src/main/java/com/skala/skip/report/agent/dto/ReportDraftRequest.java`

**이유**:
- **입력 검증**: Bean Validation으로 요청 데이터 검증
- **타입 안정성**: 명확한 필드 정의로 오류 방지
- **문서화**: 필드명과 주석으로 API 스펙 명확화

**구현 방식**:
```java
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportDraftRequest {
    @NotBlank(message = "보고서 목적은 필수입니다.")
    private String goal;
    
    @NotBlank(message = "회사/ESG 요약은 필수입니다.")
    private String summary;
    
    @NotNull(message = "핵심 이슈 리스트는 필수입니다.")
    @NotEmpty(message = "핵심 이슈는 최소 1개 이상이어야 합니다.")
    private List<String> issues;
}
```

**검증 어노테이션**:
- `@NotBlank`: null, 빈 문자열, 공백만 있는 문자열 거부
- `@NotNull`: null 값 거부
- `@NotEmpty`: null 또는 빈 컬렉션 거부

**사용 예시**:
```java
@PostMapping("/{companyId}/draft")
public ResponseEntity<ApiResponse<ReportDraftResponse>> generateDraft(
        @PathVariable Long companyId,
        @Valid @RequestBody ReportDraftRequest request  // @Valid로 검증
) { ... }
```

---

#### 4.1.2 ReportDraftResponse.java

**위치**: `src/main/java/com/skala/skip/report/agent/dto/ReportDraftResponse.java`

**이유**:
- **응답 구조 명확화**: FastAPI 응답 형식과 일치
- **직렬화**: Jackson으로 JSON 변환

**구현 방식**:
```java
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportDraftResponse {
    private String draftContent;  // AI가 생성한 초안 본문
}
```

---

### 4.2 Exception 클래스

#### 4.2.1 ReportAgentException.java

**위치**: `src/main/java/com/skala/skip/report/agent/exception/ReportAgentException.java`

**이유**:
- **도메인별 예외**: Report Agent 전용 예외로 명확성 확보
- **응답 본문 보존**: FastAPI 에러 응답 본문을 보관하여 디버깅 용이
- **BusinessException 상속**: 전역 예외 핸들러에서 일관 처리

**구현 방식**:
```java
@Getter
public class ReportAgentException extends BusinessException {
    private final String responseBody;

    public ReportAgentException(ESGErrorCode errorCode, String responseBody) {
        super(errorCode, responseBody);
        this.responseBody = responseBody;
    }
}
```

**특징**:
- `BusinessException` 상속으로 전역 핸들러에서 자동 처리
- `responseBody`로 FastAPI 에러 응답 보관
- `ESGErrorCode.RPT_CLIENT_001` 사용

---

### 4.3 Client 클래스

#### 4.3.1 ReportAgentClient.java

**위치**: `src/main/java/com/skala/skip/report/agent/client/ReportAgentClient.java`

**이유**:
- **외부 API 호출 분리**: FastAPI 호출 로직을 별도 클래스로 분리
- **비동기 처리**: WebClient의 Mono로 비동기 호출
- **에러 처리**: 4xx/5xx 응답을 예외로 변환
- **로깅**: 호출 시작/성공/실패 로깅

**구현 방식**:
```java
@Component
@RequiredArgsConstructor
@Slf4j
public class ReportAgentClient {

    private final WebClient fastApiWebClient;

    public Mono<ReportDraftResponse> generateDraftReport(Long companyId, ReportDraftRequest request) {
        log.info("FastAPI 호출 시작 - companyId: {}, goal: {}, issues count: {}", ...);

        return fastApiWebClient
                .post()
                .uri("/api/v1/report/{companyId}/draft", companyId)
                .bodyValue(request)
                .retrieve()
                .onStatus(
                        status -> status.is4xxClientError() || status.is5xxServerError(),
                        response -> response
                                .bodyToMono(String.class)
                                .flatMap(body -> {
                                    log.error("FastAPI 호출 실패 - companyId: {}, status: {}, body: {}", ...);
                                    return Mono.error(new ReportAgentException(
                                            ESGErrorCode.RPT_CLIENT_001, 
                                            body
                                    ));
                                })
                )
                .bodyToMono(ReportDraftResponse.class)
                .doOnSuccess(response -> {
                    log.info("FastAPI 호출 성공 - companyId: {}, draftContent length: {}", ...);
                })
                .doOnError(error -> {
                    if (!(error instanceof ReportAgentException)) {
                        log.error("FastAPI 호출 중 예외 발생 - companyId: {}", companyId, error);
                    }
                });
    }
}
```

**핵심 로직**:
1. **요청 전송**: `POST /api/v1/report/{companyId}/draft`
2. **에러 처리**: `onStatus()`로 4xx/5xx 응답 감지 → `ReportAgentException` 변환
3. **응답 파싱**: `bodyToMono(ReportDraftResponse.class)`로 JSON → 객체 변환
4. **로깅**: `doOnSuccess()`, `doOnError()`로 성공/실패 로깅

**비동기 처리**:
- `Mono<ReportDraftResponse>` 반환으로 비동기 처리
- Service 레이어에서 `block()`으로 동기화 (추후 비동기로 변경 가능)

---

### 4.4 Service 클래스

#### 4.4.1 ReportAgentService.java

**위치**: `src/main/java/com/skala/skip/report/agent/service/ReportAgentService.java`

**이유**:
- **비즈니스 로직 레이어**: Controller와 Client 사이의 비즈니스 로직 처리
- **트랜잭션 관리**: `@Transactional`로 트랜잭션 경계 설정
- **예외 변환**: Client 예외를 BusinessException으로 변환
- **로깅**: 비즈니스 로직 흐름 로깅

**구현 방식**:
```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)  // 기본은 읽기 전용
@Slf4j
public class ReportAgentService {

    private final ReportAgentClient reportAgentClient;

    @Transactional  // 쓰기 작업 시 오버라이드
    public ReportDraftResponse generateDraft(Long companyId, ReportDraftRequest request) {
        log.info("보고서 초안 생성 요청 - companyId: {}, goal: {}, issues count: {}", ...);

        try {
            ReportDraftResponse response = reportAgentClient
                    .generateDraftReport(companyId, request)
                    .block();  // 비동기 → 동기 변환

            if (response == null) {
                throw new BusinessException(
                        ESGErrorCode.RPT_AI_001, 
                        "FastAPI로부터 응답을 받지 못했습니다."
                );
            }

            log.info("보고서 초안 생성 완료 - companyId: {}, draftContent length: {}", ...);
            return response;
            
        } catch (BusinessException e) {
            throw e;  // BusinessException은 그대로 전파
        } catch (Exception e) {
            log.error("보고서 초안 생성 실패 - companyId: {}", companyId, e);
            throw new BusinessException(
                    ESGErrorCode.RPT_AI_001, 
                    String.format("보고서 초안 생성 중 오류 발생: %s", e.getMessage()),
                    e
            );
        }
    }
}
```

**트랜잭션 전략**:
- 클래스 레벨: `@Transactional(readOnly = true)` - 기본은 읽기 전용
- 메서드 레벨: `@Transactional` - 쓰기 작업 시 오버라이드

**예외 처리 전략**:
1. `BusinessException`: 그대로 전파 (이미 적절한 에러 코드 포함)
2. 기타 예외: `BusinessException`으로 래핑하여 일관된 에러 처리

**block() 사용 이유**:
- 현재는 동기식 API로 설계 (Controller가 동기 응답 반환)
- 추후 비동기로 변경 시 `Mono` 반환으로 쉽게 전환 가능

---

### 4.5 Controller 클래스

#### 4.5.1 ReportAgentController.java

**위치**: `src/main/java/com/skala/skip/report/agent/controller/ReportAgentController.java`

**이유**:
- **REST API 엔드포인트**: HTTP 요청/응답 처리
- **입력 검증**: `@Valid`로 요청 데이터 검증
- **표준 응답**: `ApiResponse` 래퍼로 일관된 응답 형식
- **로깅**: API 호출 로깅

**구현 방식**:
```java
@RestController
@RequestMapping("/api/v1/report")
@RequiredArgsConstructor
@Slf4j
public class ReportAgentController {

    private final ReportAgentService reportAgentService;

    @PostMapping("/{companyId}/draft")
    public ResponseEntity<ApiResponse<ReportDraftResponse>> generateDraft(
            @PathVariable Long companyId,
            @Valid @RequestBody ReportDraftRequest request
    ) {
        log.info("보고서 초안 생성 API 호출 - companyId: {}", companyId);
        
        ReportDraftResponse response = reportAgentService.generateDraft(companyId, request);
        
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
```

**특징**:
- `@RestController`: JSON 응답 자동 변환
- `@RequestMapping`: 기본 경로 설정
- `@RequiredArgsConstructor`: 생성자 주입 (Lombok)
- `@Slf4j`: 로깅
- `@Valid`: Bean Validation 적용
- `ApiResponse.success()`: 표준 응답 래퍼 사용

**API 엔드포인트**:
```
POST /api/v1/report/{companyId}/draft
```

**요청 예시**:
```json
{
  "goal": "2025년 ESG 핵심 이슈 기반 보고서",
  "summary": "회사의 환경·사회·지배구조 주요 개선 현황 요약...",
  "issues": ["기후 변화 대응", "데이터 보안", "산업 안전"]
}
```

**응답 예시**:
```json
{
  "success": true,
  "data": {
    "draftContent": "# 2025년 ESG 핵심 이슈 기반 보고서\n\n..."
  },
  "timestamp": "2025-01-18T10:30:00"
}
```

---

## 5. 전체 아키텍처

### 5.1 레이어 구조

```
Controller Layer (ReportAgentController)
    ↓ (ReportDraftRequest)
Service Layer (ReportAgentService)
    ↓ (비즈니스 로직, 예외 처리)
Client Layer (ReportAgentClient)
    ↓ (HTTP 요청)
FastAPI Server
    ↓ (HTTP 응답)
Client Layer
    ↓ (ReportDraftResponse)
Service Layer
    ↓ (ReportDraftResponse)
Controller Layer
    ↓ (ApiResponse<ReportDraftResponse>)
HTTP Response
```

### 5.2 호출 흐름

1. **클라이언트 요청**
   ```
   POST /api/v1/report/1/draft
   Body: { "goal": "...", "summary": "...", "issues": [...] }
   ```

2. **Controller**
   - `@Valid`로 요청 검증
   - Service 호출

3. **Service**
   - Client 호출 (비동기)
   - `block()`으로 동기화
   - 예외 처리 및 로깅

4. **Client**
   - WebClient로 FastAPI 호출
   - 에러 응답 처리
   - 로깅

5. **FastAPI**
   - 보고서 초안 생성
   - 응답 반환

6. **응답 반환**
   - Controller에서 `ApiResponse.success()`로 래핑
   - JSON 응답 반환

### 5.3 예외 처리 흐름

```
Client에서 4xx/5xx 응답
    ↓
ReportAgentException 발생
    ↓
Service에서 catch
    ↓
BusinessException으로 변환
    ↓
Controller까지 전파
    ↓
GlobalExceptionHandler가 캐치
    ↓
ErrorResponse 생성
    ↓
ApiResponse.error()로 래핑
    ↓
HTTP 400 Bad Request 응답
```

---

## 6. backend.mdc 룰 준수 사항

### 6.1 패키지 구조
- ✅ `com.skala.skip.report.agent` 도메인 패키지 사용
- ✅ `controller`, `service`, `client`, `dto`, `exception` 하위 패키지 분리

### 6.2 어노테이션
- ✅ `@RestController`, `@RequestMapping` 사용
- ✅ `@RequiredArgsConstructor`로 생성자 주입
- ✅ `@Slf4j`로 로깅
- ✅ `@Valid`로 입력 검증
- ✅ `@Transactional`로 트랜잭션 관리

### 6.3 예외 처리
- ✅ `BusinessException` 사용
- ✅ `ESGErrorCode` enum 사용 (RPT 모듈)
- ✅ `GlobalExceptionHandler`로 중앙 처리

### 6.4 응답 형식
- ✅ `ApiResponse` 래퍼 사용
- ✅ 성공/실패 일관된 형식

### 6.5 로깅
- ✅ INFO: 주요 비즈니스 흐름
- ✅ ERROR: 예외 발생 시
- ✅ `printStackTrace()` 미사용

### 6.6 WebClient
- ✅ 중앙 집중식 WebClient Bean 사용
- ✅ 타임아웃 설정
- ✅ 에러 매핑

---

## 7. 향후 개선 사항

### 7.1 비동기 처리
현재는 `block()`으로 동기화했지만, 추후 비동기로 변경 가능:

```java
// 현재 (동기)
ReportDraftResponse response = client.generateDraftReport(...).block();

// 향후 (비동기)
public Mono<ReportDraftResponse> generateDraft(Long companyId, ReportDraftRequest request) {
    return reportAgentClient.generateDraftReport(companyId, request);
}
```

### 7.2 재시도 로직
WebClient에 재시도 로직 추가 가능:

```java
.retryWhen(Retry.backoff(3, Duration.ofSeconds(1)))
```

### 7.3 캐싱
동일한 요청에 대한 캐싱 추가 가능 (Redis 등)

---

## 8. 테스트 예시

### 8.1 API 테스트
```bash
curl -X POST http://localhost:8080/api/v1/report/1/draft \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "2025년 ESG 핵심 이슈 기반 보고서",
    "summary": "회사의 환경·사회·지배구조 주요 개선 현황 요약...",
    "issues": ["기후 변화 대응", "데이터 보안", "산업 안전"]
  }'
```

### 8.2 검증 실패 테스트
```bash
curl -X POST http://localhost:8080/api/v1/report/1/draft \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "",
    "summary": "",
    "issues": []
  }'
```

응답:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력 검증 실패",
    "details": "goal: 보고서 목적은 필수입니다."
  }
}
```

---

## 결론

이 구현은 **backend.mdc 룰을 준수**하며, **표준화된 아키텍처**를 따릅니다:

1. ✅ 레이어 분리 (Controller → Service → Client)
2. ✅ 표준 응답 형식 (ApiResponse)
3. ✅ 일관된 예외 처리 (BusinessException + ESGErrorCode)
4. ✅ 입력 검증 (Bean Validation)
5. ✅ 로깅 및 모니터링
6. ✅ 설정 외부화 (application.yml)

모든 컴포넌트가 **단일 책임 원칙**을 따르며, **테스트 가능**하고 **유지보수 가능**한 구조로 설계되었습니다.

