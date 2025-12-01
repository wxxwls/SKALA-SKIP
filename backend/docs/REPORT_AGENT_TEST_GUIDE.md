# 보고서 초안 생성 API 테스트 가이드

## 사전 준비

### 1. Spring Boot 서버 실행

```bash
cd backend
./gradlew bootRun --args='--spring.profiles.active=dev'
```

또는 IDE에서 `SkipApplication` 실행 (dev 프로필 활성화)

**기본 포트**: `8080` (application.yml에서 확인)

### 2. FastAPI 서버 실행 (선택사항)

현재 FastAPI 서버가 없어도 테스트는 가능하지만, 실제 응답을 받으려면 FastAPI 서버가 필요합니다.

FastAPI 서버가 실행되어 있어야 하는 경우:
- `http://localhost:8000`에서 FastAPI 서버 실행
- `/internal/v1/reports/{reportId}/sections/{sectionCode}/ai-draft` 엔드포인트 구현 필요

---

## Postman 테스트 설정

### 1. 요청 설정

**Method**: `POST`

**URL**: 
```
http://localhost:8080/api/v1/reports/{reportId}/sections/{sectionCode}/ai-draft
```

**예시**:
```
http://localhost:8080/api/v1/reports/123/sections/ENVIRONMENT/ai-draft
```

**Path Variables**:
- `reportId`: `123` (Long 타입)
- `sectionCode`: `ENVIRONMENT` (String 타입, 예: ENVIRONMENT, SOCIAL, GOVERNANCE)

### 2. Headers 설정

```
Content-Type: application/json
```

### 3. Body 설정

**Body 타입**: `raw` → `JSON` 선택

**Request Body 예시**:
```json
{
  "goal": "2025년 ESG 핵심 이슈 기반 보고서",
  "summary": "회사의 환경·사회·지배구조 주요 개선 현황 요약입니다. 탄소 중립 목표 달성을 위한 노력과 이해관계자 소통 강화를 추진하고 있습니다.",
  "issues": [
    "기후 변화 대응",
    "데이터 보안",
    "산업 안전",
    "인권 보호",
    "지배구조 투명성"
  ]
}
```

### 4. 전체 Postman 설정 스크린샷 참고

```
┌─────────────────────────────────────────────────────────┐
│ POST http://localhost:8080/api/v1/reports/123/sections/ │
│                    ENVIRONMENT/ai-draft                  │
├─────────────────────────────────────────────────────────┤
│ Headers:                                                │
│   Content-Type: application/json                        │
├─────────────────────────────────────────────────────────┤
│ Body (raw - JSON):                                       │
│ {                                                       │
│   "goal": "2025년 ESG 핵심 이슈 기반 보고서",            │
│   "summary": "회사의 환경·사회·지배구조...",              │
│   "issues": ["기후 변화 대응", "데이터 보안"]            │
│ }                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 예상 응답

### 성공 응답 (200 OK)

**FastAPI 서버가 정상 응답하는 경우**:
```json
{
  "success": true,
  "data": {
    "draftContent": "# 2025년 ESG 핵심 이슈 기반 보고서\n\n## 회사 개요\n..."
  },
  "timestamp": "2025-01-18T10:30:00"
}
```

### 에러 응답 (400 Bad Request)

**입력 검증 실패**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력 검증 실패",
    "details": "goal: 보고서 목적은 필수입니다.",
    "timestamp": "2025-01-18T10:30:00"
  }
}
```

**FastAPI 서버 연결 실패**:
```json
{
  "success": false,
  "error": {
    "code": "ESG-RPT-CLIENT-001",
    "message": "FastAPI 클라이언트 호출 실패",
    "details": "Connection refused: no further information",
    "timestamp": "2025-01-18T10:30:00"
  }
}
```

**FastAPI 서버 응답 없음**:
```json
{
  "success": false,
  "error": {
    "code": "ESG-RPT-AI-001",
    "message": "AI 초안 생성 실패",
    "details": "FastAPI로부터 응답을 받지 못했습니다.",
    "timestamp": "2025-01-18T10:30:00"
  }
}
```

---

## 테스트 시나리오

### 시나리오 1: 정상 요청

**요청**:
- `reportId`: `123`
- `sectionCode`: `ENVIRONMENT`
- `goal`: "2025년 ESG 핵심 이슈 기반 보고서"
- `summary`: "회사의 환경·사회·지배구조 주요 개선 현황..."
- `issues`: ["기후 변화 대응", "데이터 보안", "산업 안전"]

**예상 결과**: 200 OK, `draftContent` 포함

### 시나리오 2: 필수 필드 누락

**요청**:
```json
{
  "goal": "",
  "summary": "",
  "issues": []
}
```

**예상 결과**: 400 Bad Request, 검증 에러 메시지

### 시나리오 3: FastAPI 서버 미실행

**요청**: 정상 요청

**예상 결과**: 400 Bad Request, `ESG-RPT-CLIENT-001` 에러

### 시나리오 4: 다른 sectionCode 테스트

**요청**:
- `sectionCode`: `SOCIAL` 또는 `GOVERNANCE`

**예상 결과**: 200 OK (FastAPI가 sectionCode에 따라 다른 응답 반환 가능)

---

## curl 명령어로 테스트

Postman 대신 curl로도 테스트 가능:

```bash
curl -X POST http://localhost:8080/api/v1/reports/123/sections/ENVIRONMENT/ai-draft \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "2025년 ESG 핵심 이슈 기반 보고서",
    "summary": "회사의 환경·사회·지배구조 주요 개선 현황 요약입니다.",
    "issues": [
      "기후 변화 대응",
      "데이터 보안",
      "산업 안전"
    ]
  }'
```

---

## 문제 해결

### 1. Connection refused 에러

**원인**: FastAPI 서버가 실행되지 않음

**해결**:
- FastAPI 서버를 `http://localhost:8000`에서 실행
- 또는 `application-dev.yml`의 `fastapi.base-url` 확인

### 2. 404 Not Found

**원인**: URL 경로 오류

**해결**:
- URL이 정확한지 확인: `/api/v1/reports/{reportId}/sections/{sectionCode}/ai-draft`
- Spring Boot 서버가 실행 중인지 확인

### 3. 400 Bad Request (검증 에러)

**원인**: 요청 Body의 필수 필드 누락 또는 형식 오류

**해결**:
- `goal`, `summary`, `issues` 필드 모두 포함 확인
- `issues`는 빈 배열이 아닌 최소 1개 이상 포함
- JSON 형식 확인

### 4. 500 Internal Server Error

**원인**: 서버 내부 오류

**해결**:
- Spring Boot 로그 확인
- FastAPI 서버 로그 확인
- `application-dev.yml` 설정 확인

---

## 로그 확인

### Spring Boot 로그

성공 시:
```
INFO  - 보고서 초안 생성 API 호출 - reportId: 123, sectionCode: ENVIRONMENT
INFO  - 보고서 초안 생성 요청 - reportId: 123, sectionCode: ENVIRONMENT, goal: ..., issues count: 3
INFO  - FastAPI 호출 시작 - reportId: 123, sectionCode: ENVIRONMENT, goal: ..., issues count: 3
INFO  - FastAPI 호출 성공 - reportId: 123, sectionCode: ENVIRONMENT, draftContent length: 1234
INFO  - 보고서 초안 생성 완료 - reportId: 123, sectionCode: ENVIRONMENT, draftContent length: 1234
```

실패 시:
```
ERROR - FastAPI 호출 실패 - reportId: 123, sectionCode: ENVIRONMENT, status: 500 INTERNAL SERVER ERROR, body: {...}
ERROR - 보고서 초안 생성 실패 - reportId: 123, sectionCode: ENVIRONMENT
```

---

## 다음 단계

1. ✅ Postman으로 기본 테스트 완료
2. ✅ FastAPI 서버 연동 테스트
3. ✅ 다양한 sectionCode 테스트
4. ✅ 에러 케이스 테스트
5. ✅ Vue 프론트엔드 연동

