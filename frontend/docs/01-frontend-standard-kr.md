# 프론트엔드 개발 표준 (Frontend Development Standard)

**ESG 이슈풀 구성 AI 시스템**
**Version 1.0**
**SKALA 2기 7조**

---

## 문서 개요

본 문서는 ESG 이중 중대성 이슈풀 자동 구성 서비스의 **프론트엔드 개발 표준**을 정의합니다.

**목적**: 여러 개발자가 AI(Claude, GPT 등)를 활용해 동시 개발할 때, 최종 병합 시 충돌·불일치·에러가 발생하지 않도록 통일된 규칙을 제공합니다.

**적용 대상**: Vue 3 기반 프론트엔드 개발

---

## 1. 기술 스택 및 버전 고정

### 1.1 핵심 기술 스택

```json
{
  "framework": "Vue 3.4.x",
  "buildTool": "Vite 5.x",
  "stateManagement": "Pinia 2.x",
  "router": "Vue Router 4.x",
  "uiLibrary": ["Vuetify 3.x", "TailwindCSS 3.x"],
  "charts": "ECharts 5.x",
  "dataGrid": "AG Grid 31.x",
  "httpClient": "Axios 1.x",
  "language": "TypeScript 5.x"
}
```

### 1.2 버전 고정 규칙

- **package.json**에서 정확한 버전 사용 (^, ~ 사용 금지)
- **package-lock.json** 필수 커밋
- 라이브러리 업데이트 시 팀 승인 필수

---

## 2. 프로젝트 구조

### 2.1 디렉터리 구조

```
src/
├── assets/              # 정적 파일 (이미지, 폰트 등)
├── components/          # 재사용 가능한 UI 컴포넌트
│   ├── common/         # 공통 컴포넌트 (Button, Modal 등)
│   ├── chart/          # 차트 컴포넌트
│   └── card/           # 카드형 컴포넌트
├── layouts/            # 레이아웃 컴포넌트
│   ├── DefaultLayout.vue
│   ├── AuthLayout.vue
│   └── BlankLayout.vue
├── views/              # 라우팅 대상 페이지
│   ├── home/
│   ├── news/
│   ├── issuepool/
│   ├── report/
│   ├── carbon/
│   └── chatbot/
├── stores/             # Pinia 스토어
│   ├── auth.ts
│   ├── issuePool.ts
│   ├── news.ts
│   └── carbon.ts
├── api/                # API 호출 모듈
│   ├── auth.api.ts
│   ├── issuePool.api.ts
│   └── carbon.api.ts
├── composables/        # Composition API 재사용 로직
│   ├── useChart.ts
│   └── useValidation.ts
├── router/             # 라우터 설정
│   └── index.ts
├── utils/              # 유틸리티 함수
├── types/              # TypeScript 타입 정의
├── styles/             # 전역 스타일
│   ├── variables.css   # CSS 변수
│   └── global.css
└── main.ts
```

### 2.2 디렉터리 사용 원칙

| 디렉터리 | 용도 | 네이밍 규칙 |
|---------|------|------------|
| `views/` | 라우팅 페이지만 위치 | PascalCase + View.vue |
| `components/` | 재사용 가능 UI만 | PascalCase.vue |
| `layouts/` | 공통 레이아웃 | PascalCase + Layout.vue |
| `stores/` | Pinia 스토어 (도메인별 분리) | camelCase + Store.ts |
| `api/` | API 엔드포인트별 모듈 | camelCase + .api.ts |
| `composables/` | 재사용 비즈니스 로직 | use + PascalCase.ts |

---

## 3. 네이밍 컨벤션

### 3.1 파일명

- **컴포넌트**: `PascalCase.vue` (예: `IssueCard.vue`, `ChartWrapper.vue`)
- **View 페이지**: `PascalCase + View.vue` (예: `IssuePoolView.vue`)
- **Store**: `camelCase + Store.ts` (예: `issuePoolStore.ts`)
- **API 모듈**: `camelCase + .api.ts` (예: `carbonApi.ts`)
- **Composable**: `use + PascalCase.ts` (예: `useChart.ts`)

### 3.2 변수·함수명

```typescript
// 변수: camelCase
const issueList = ref([]);
const selectedCompany = ref(null);

// 함수: camelCase (동사 시작)
function fetchIssueList() { }
function generateReport() { }

// Boolean: is/has/can 시작
const isLoading = ref(false);
const hasPermission = computed(() => true);

// 상수: UPPER_SNAKE_CASE
const DEFAULT_PAGE_SIZE = 20;
const MAX_ISSUE_COUNT = 100;
```

### 3.3 컴포넌트명

```vue
<!-- 단일 단어 금지, 최소 2단어 -->
<!-- ✅ 권장 -->
<IssueCard />
<KpiSummary />
<CarbonChart />

<!-- ❌ 금지 -->
<Card />
<Chart />
```

### 3.4 Props/Emit 네이밍

```typescript
// Props: camelCase
const props = defineProps<{
  issueId: string;
  chartData: ChartDataset[];
  isVisible: boolean;
}>();

// Emit: kebab-case
const emit = defineEmits<{
  'update:modelValue': [value: string];
  'issue-selected': [id: string];
}>();
```

---

## 4. 코딩 컨벤션

### 4.1 Composition API 사용

```vue
<script setup lang="ts">
// ✅ 권장: <script setup> + Composition API
import { ref, computed, onMounted } from 'vue';

const count = ref(0);
const doubleCount = computed(() => count.value * 2);

onMounted(() => {
  console.log('Component mounted');
});
</script>
```

### 4.2 코드 순서

```vue
<script setup lang="ts">
// 1. Import
import { ref, computed } from 'vue';
import { useIssuePoolStore } from '@/stores/issuePool';

// 2. Props/Emit 정의
const props = defineProps<{ id: string }>();
const emit = defineEmits<{ 'close': [] }>();

// 3. 상수
const MAX_ITEMS = 10;

// 4. Composables/Stores
const store = useIssuePoolStore();

// 5. Reactive 상태
const items = ref([]);
const loading = ref(false);

// 6. Computed
const filteredItems = computed(() => items.value.filter(x => x.active));

// 7. 메서드
function handleClick() {
  emit('close');
}

// 8. 생명주기 훅
onMounted(async () => {
  await loadData();
});
</script>
```

### 4.3 들여쓰기 및 포맷팅

- **들여쓰기**: 2 spaces (탭 금지)
- **세미콜론**: 사용 (ESLint 규칙 통일)
- **따옴표**: 작은따옴표 `'` 우선
- **줄바꿈**: 120자 제한

---

## 5. 컴포넌트 설계 원칙

### 5.1 단일 책임 원칙 (SRP)

```vue
<!-- ✅ 권장: 하나의 역할만 -->
<template>
  <div class="issue-card">
    <h3>{{ issue.title }}</h3>
    <p>{{ issue.description }}</p>
  </div>
</template>

<!-- ❌ 금지: 여러 도메인 혼재 -->
<template>
  <div>
    <IssueList /> <!-- 이슈풀 도메인 -->
    <CarbonChart /> <!-- 탄소예측 도메인 -->
  </div>
</template>
```

### 5.2 Container/Presentational 패턴

```vue
<!-- Container (views/): 데이터 로딩 담당 -->
<script setup lang="ts">
const store = useIssuePoolStore();
const issues = computed(() => store.issues);

onMounted(() => {
  store.fetchIssues();
});
</script>

<template>
  <IssueList :issues="issues" @select="handleSelect" />
</template>

<!-- Presentational (components/): UI만 담당 -->
<script setup lang="ts">
defineProps<{
  issues: Issue[];
}>();

const emit = defineEmits<{
  'select': [id: string];
}>();
</script>
```

---

## 6. 상태 관리 (Pinia)

### 6.1 스토어 구조

```typescript
// stores/issuePoolStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Issue } from '@/types';

export const useIssuePoolStore = defineStore('issuePool', () => {
  // State
  const issues = ref<Issue[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const activeIssues = computed(() =>
    issues.value.filter(issue => issue.active)
  );

  const issueCount = computed(() => issues.value.length);

  // Actions
  async function fetchIssues(companyId: string) {
    loading.value = true;
    error.value = null;

    try {
      const data = await issuePoolApi.getIssues(companyId);
      issues.value = data;
    } catch (e) {
      error.value = (e as Error).message;
    } finally {
      loading.value = false;
    }
  }

  function clearIssues() {
    issues.value = [];
  }

  return {
    // State
    issues,
    loading,
    error,
    // Getters
    activeIssues,
    issueCount,
    // Actions
    fetchIssues,
    clearIssues
  };
});
```

### 6.2 스토어 사용 규칙

- **도메인별 분리**: 이슈풀, 뉴스, 탄소, 인증 등 도메인당 1개 스토어
- **컴포넌트에서 직접 API 호출 금지**: 반드시 Store Actions를 통해 호출
- **상태 직접 수정 금지**: Actions를 통해서만 상태 변경

---

## 7. 라우팅 규칙

### 7.1 라우트 정의

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/home/HomeView.vue'),
    meta: {
      title: 'Home',
      requiresAuth: true,
      layout: 'default'
    }
  },
  {
    path: '/issue-pool',
    name: 'IssuePool',
    component: () => import('@/views/issuepool/IssuePoolView.vue'),
    meta: {
      title: '이슈풀',
      requiresAuth: true
    }
  },
  {
    path: '/carbon/dashboard',
    name: 'CarbonDashboard',
    component: () => import('@/views/carbon/CarbonDashboardView.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
```

### 7.2 라우트 네이밍 규칙

- **path**: kebab-case (예: `/issue-pool`, `/carbon/trading`)
- **name**: PascalCase (예: `IssuePool`, `CarbonDashboard`)
- **meta.title**: 한글 또는 영문 (브라우저 탭 타이틀용)

---

## 8. API 연동 표준

### 8.1 API 모듈 구조

```typescript
// api/issuePool.api.ts
import axios from 'axios';
import type { Issue, IssueCreateRequest } from '@/types';

const BASE_URL = '/api/v1/issue-pool';

export const issuePoolApi = {
  async getIssues(companyId: string): Promise<Issue[]> {
    const { data } = await axios.get(`${BASE_URL}/${companyId}`);
    return data.data;
  },

  async generateIssuePool(companyId: string): Promise<Issue[]> {
    const { data } = await axios.post(`${BASE_URL}/${companyId}/generate`);
    return data.data;
  },

  async createIssue(request: IssueCreateRequest): Promise<Issue> {
    const { data } = await axios.post(`${BASE_URL}/issues`, request);
    return data.data;
  }
};
```

### 8.2 Axios 인스턴스 설정

```typescript
// api/axios.config.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 인증 실패 처리
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 8.3 에러 처리

```typescript
async function fetchData() {
  loading.value = true;
  error.value = null;

  try {
    const data = await issuePoolApi.getIssues(companyId.value);
    issues.value = data;
  } catch (e) {
    const err = e as Error;
    error.value = err.message;

    // 사용자에게 Toast 메시지 표시
    showErrorToast('데이터를 불러오는데 실패했습니다.');
  } finally {
    loading.value = false;
  }
}
```

---

## 9. UI/UX 표준

### 9.1 디자인 시스템

- **UI 라이브러리**: Vuetify 3.x (버튼, 모달, 입력폼 등)
- **레이아웃·스타일링**: TailwindCSS 3.x
- **차트**: ECharts 5.x
- **데이터 그리드**: AG Grid 31.x

### 9.2 디자인 토큰

```css
/* styles/variables.css */
:root {
  /* Colors */
  --color-primary: #FF7A00;
  --color-secondary: #2C3E50;
  --color-success: #4CAF50;
  --color-warning: #FFC107;
  --color-error: #F44336;
  --color-info: #2196F3;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* Typography */
  --font-family: 'Pretendard', sans-serif;
  --font-size-sm: 12px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 20px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

### 9.3 반응형 기준

```typescript
// Breakpoints
const breakpoints = {
  sm: 600,   // Mobile
  md: 960,   // Tablet
  lg: 1280,  // Desktop
  xl: 1920   // Large Desktop
};

// 기본 해상도: 1920×1080 (데스크톱)
// 모바일 우선순위: 낮음 (PC 최적화 우선)
```

---

## 10. 차트 표준 (ECharts)

### 10.1 공통 차트 옵션

```typescript
// composables/useChart.ts
export function useChartOptions() {
  const baseOptions = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      borderColor: 'transparent',
      textStyle: {
        color: '#fff'
      }
    },
    color: [
      '#FF7A00',
      '#2196F3',
      '#4CAF50',
      '#FFC107',
      '#F44336'
    ]
  };

  return { baseOptions };
}
```

### 10.2 차트 컴포넌트 예시

```vue
<script setup lang="ts">
import { ref, watch } from 'vue';
import * as echarts from 'echarts';
import { useChartOptions } from '@/composables/useChart';

const props = defineProps<{
  data: number[];
  labels: string[];
}>();

const chartRef = ref<HTMLElement>();
const { baseOptions } = useChartOptions();

let chartInstance: echarts.ECharts | null = null;

function initChart() {
  if (!chartRef.value) return;

  chartInstance = echarts.init(chartRef.value);

  const option = {
    ...baseOptions,
    xAxis: {
      type: 'category',
      data: props.labels
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: props.data,
      type: 'line',
      smooth: true
    }]
  };

  chartInstance.setOption(option);
}

watch(() => props.data, () => {
  initChart();
}, { deep: true });

onMounted(() => {
  initChart();
});

onBeforeUnmount(() => {
  chartInstance?.dispose();
});
</script>

<template>
  <div ref="chartRef" class="w-full h-96"></div>
</template>
```

---

## 11. 테이블 표준 (AG Grid)

### 11.1 기본 설정

```vue
<script setup lang="ts">
import { AgGridVue } from 'ag-grid-vue3';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

const columnDefs = ref([
  { field: 'issueId', headerName: '이슈 ID', sortable: true, filter: true },
  { field: 'title', headerName: '제목', sortable: true, filter: true },
  { field: 'category', headerName: '카테고리', sortable: true },
  {
    field: 'score',
    headerName: '점수',
    sortable: true,
    cellStyle: { textAlign: 'right' }
  }
]);

const rowData = ref([]);

const defaultColDef = {
  resizable: true,
  sortable: true,
  filter: true
};
</script>

<template>
  <ag-grid-vue
    class="ag-theme-alpine"
    style="height: 500px;"
    :columnDefs="columnDefs"
    :rowData="rowData"
    :defaultColDef="defaultColDef"
    :pagination="true"
    :paginationPageSize="20"
  />
</template>
```

---

## 12. Validation 규칙

### 12.1 입력 검증

```typescript
// composables/useValidation.ts
export function useValidation() {
  const validateRequired = (value: string) => {
    return !!value || '필수 입력 항목입니다.';
  };

  const validateEmail = (value: string) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(value) || '올바른 이메일 형식이 아닙니다.';
  };

  const validateMinLength = (min: number) => (value: string) => {
    return value.length >= min || `최소 ${min}자 이상 입력해주세요.`;
  };

  return {
    validateRequired,
    validateEmail,
    validateMinLength
  };
}
```

---

## 13. 환경변수 (.env)

### 13.1 환경변수 파일 구조

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8080
VITE_APP_TITLE=ESG IssuePool (Dev)

# .env.production
VITE_API_BASE_URL=https://api.esgskala.com
VITE_APP_TITLE=ESG IssuePool
```

### 13.2 환경변수 사용

```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL;
const appTitle = import.meta.env.VITE_APP_TITLE;
```

---

## 14. 테스트 표준

### 14.1 단위 테스트 (Vitest)

```typescript
// tests/components/IssueCard.test.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import IssueCard from '@/components/IssueCard.vue';

describe('IssueCard', () => {
  it('renders issue title correctly', () => {
    const wrapper = mount(IssueCard, {
      props: {
        issue: {
          id: '1',
          title: 'Test Issue',
          description: 'Test Description'
        }
      }
    });

    expect(wrapper.text()).toContain('Test Issue');
  });

  it('emits select event when clicked', async () => {
    const wrapper = mount(IssueCard, {
      props: {
        issue: { id: '1', title: 'Test' }
      }
    });

    await wrapper.trigger('click');

    expect(wrapper.emitted('select')).toBeTruthy();
    expect(wrapper.emitted('select')?.[0]).toEqual(['1']);
  });
});
```

---

## 15. Git & 커밋 메시지

### 15.1 Git Flow

- **main**: 운영 배포용 브랜치
- **develop**: 개발 운용 브랜치(모든 개발, 버그 수정 브랜치는 해당 브랜치의 파생)
- **feature/***: 기능 개발 (예: `feature/issue-pool`)
- **fix/***: 버그 수정 (예: `fix/login-error`)

### 15.2 커밋 메시지 규칙

```bash
<type>: <subject>

# Type
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅 (세미콜론, 줄바꿈 등)
refactor: 코드 리팩토링
test: 테스트 코드 추가
chore: 빌드, 패키지 매니저 수정

# 예시
feat: 이슈풀 자동 생성 기능 추가
fix: 차트 데이터 로딩 오류 수정
docs: README 설치 가이드 추가
```

---

## 16. ESLint & Prettier

### 16.1 ESLint 설정

```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'plugin:vue/vue3-recommended',
    '@vue/typescript/recommended',
    'prettier'
  ],
  rules: {
    'vue/multi-word-component-names': 'error',
    'vue/no-unused-vars': 'warn',
    '@typescript-eslint/no-explicit-any': 'warn',
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off'
  }
};
```

### 16.2 Prettier 설정

```json
{
  "semi": true,
  "singleQuote": true,
  "printWidth": 120,
  "tabWidth": 2,
  "trailingComma": "none",
  "arrowParens": "always"
}
```

---

## 17. AI 프롬프트 작성 가이드

### 17.1 컴포넌트 생성 시

```
[System]
You are a Vue 3 frontend developer following SKALA ESG project standards.

[Task]
Create a new component: IssueCard.vue

[Requirements]
- Use <script setup> with TypeScript
- Follow PascalCase naming
- Props: issue (Issue type)
- Emit: 'select' event with issue ID
- Use Vuetify for UI elements
- Follow spacing: 2 spaces indentation
- Add proper TypeScript types

[Constraints]
- No use of Options API
- No direct API calls in component
- Must be reusable and presentational
```

### 17.2 코드 수정 시

```
[Context]
File: src/views/issuepool/IssuePoolView.vue
Current implementation uses Options API

[Task]
Refactor to Composition API with <script setup>

[Requirements]
- Migrate all data to ref/reactive
- Convert methods to functions
- Use Pinia store for state management
- Keep existing functionality intact
- Follow project naming conventions
```

---

## 18. 주의사항 및 금지사항

### 18.1 금지사항

❌ **절대 금지**:
- Options API 사용
- 컴포넌트에서 직접 API 호출
- 하드코딩된 URL, 설정값
- `any` 타입 남용
- 의미 없는 변수명 (data, temp, test 등)
- 단일 단어 컴포넌트명

### 18.2 권장사항

✅ **반드시 준수**:
- TypeScript 타입 명시
- Props/Emit 타입 정의
- 에러 처리 (try-catch)
- Loading 상태 표시
- 재사용 가능한 컴포넌트 설계
- 명확한 변수·함수명

---

## 19. 체크리스트

컴포넌트 개발 완료 전 확인사항:

- [ ] TypeScript 타입 오류 없음
- [ ] ESLint 오류 없음
- [ ] Props/Emit 타입 정의됨
- [ ] 컴포넌트명 PascalCase + 2단어 이상
- [ ] 파일 위치 적절 (views vs components)
- [ ] API 호출은 Store를 통해서만
- [ ] 에러 처리 및 Loading 상태 구현
- [ ] 반응형 고려 (필요 시)
- [ ] 주석 작성 (복잡한 로직만)
- [ ] Git 커밋 메시지 규칙 준수

---

## 20. 참고 문서

- [개발표준 정의서 v1.0]([SKIP]_100.개발표준 정의서_v1.0.docx.pdf)
- [UI정의서 v1.2]([07조]_400. 서비스_분석 설계서_413_UI정의서_v1.2.pptx.pptx)
- [요구사항정의서 v0.1]([SKIP]_300. 요구사항정의서_v0.1.xlsx)
- Figma: https://www.figma.com/make/OEtzhysRKRi8DghdMd4Tzx/Receive-and-Build-Prompt

---

**문서 버전**: 1.0
**최종 수정일**: 2025-11-18
**작성자**: SKALA 2기 7조

---

## 21. ESG 프로젝트 특화 규칙

### 21.1 화면 구조 (FSD 기반)

#### Navigator 구조
- **좌측 Navigator**: 섹션 트리 구조
  - 리스크 관리
  - MANAGEMENT > 리스크 관리 방침
  - PERFORMANCE
- **중앙 영역**: 컨텐츠 표시
- **우측 영역**: Best Practice / 담당부서 작성란

#### 주요 화면별 레이아웃

**이슈풀 화면 (EIP-IP001-M0, EIP-IP002-M0)**
```
├── 좌측: ESG 표준 문서 목록 (GRI/SASB/ISSB/KCGS)
├── 중앙: 분석 결과 및 Topic 리스트
└── 우측: 선택된 Issue 상세 정보
```

**중대성 평가 화면**
```
├── Double Materiality Matrix (X: Financial, Y: Impact)
├── 구간: 3×3 또는 확장 가능
└── Topic별 좌표 표시 + Core Issue 하이라이트
```

**보고서 작성 화면 (EIP-RP001-M0 ~ EIP-RP003-M0)**
```
├── 좌측: Navigator (섹션 트리)
├── 중앙: 전년도 원문 vs AI 생성 초안 비교 (Diff View)
└── 우측: 담당부서 의견 + 개선/수정 필요사항
```

**ESG 챗봇 vs 보고서 작성 AI**
- ESG 챗봇 (EIP-AI002-M0): 일반 ESG Q&A용
- 보고서 작성 AI: 보고서 섹션 편집 전용 (별도 모듈)

### 21.2 Topic 제한 규칙

```typescript
// constants/esg.ts
export const ESG_CONSTANTS = {
  MAX_TOPIC_COUNT: 20,  // 이해관계자 설문 전 최대 Topic 수
  MAX_CORE_ISSUE_COUNT: 20,  // 최종 핵심 이슈 수
  SURVEY_MAX_SELECTION: 5  // 설문 시 최대 선택 가능 이슈 수
} as const;
```

**UI 반영**:
- Topic 리스트가 20개 초과 시 경고 메시지 표시
- Score 기준 상위 20개만 자동 선택
- 사용자가 21개 이상 선택 시도 시 차단

### 21.3 이해관계자 설문 UI

```vue
<template>
  <div class="stakeholder-survey">
    <!-- 중요 이슈 선택 (최대 5개) -->
    <section class="issue-selection">
      <h3>중요하다고 생각하는 이슈 5개 선택</h3>
      <v-checkbox-group
        v-model="selectedIssues"
        :max="5"
        :disabled="selectedIssues.length >= 5"
      >
        <v-checkbox
          v-for="topic in topics"
          :key="topic.id"
          :value="topic.id"
          :label="topic.title"
        />
      </v-checkbox-group>
    </section>

    <!-- 선택된 이슈별 평가 (1-3점 척도) -->
    <section v-for="issueId in selectedIssues" :key="issueId">
      <h4>{{ getTopicTitle(issueId) }}</h4>
      
      <!-- 현재/미래 영향 수준 -->
      <v-radio-group label="영향 수준 (현재/미래)">
        <v-radio :value="1" label="1점: 낮음" />
        <v-radio :value="2" label="2점: 중간" />
        <v-radio :value="3" label="3점: 높음" />
      </v-radio-group>

      <!-- 영향 규모 -->
      <v-radio-group label="영향 규모">
        <v-radio :value="1" label="1점: 제한적" />
        <v-radio :value="2" label="2점: 중간" />
        <v-radio :value="3" label="3점: 대규모" />
      </v-radio-group>

      <!-- 영향 범위 (이해관계자 그룹) -->
      <v-checkbox-group label="영향 범위 (복수 선택)">
        <v-checkbox value="supplier" label="협력사" />
        <v-checkbox value="customer" label="고객" />
        <v-checkbox value="investor" label="투자자" />
        <v-checkbox value="community" label="지역사회" />
        <v-checkbox value="employee" label="구성원" />
      </v-checkbox-group>
    </section>
  </div>
</template>
```

### 21.4 탄소배출권 차트 UI

```vue
<template>
  <div class="carbon-chart-container">
    <div ref="chartRef" class="w-full h-96"></div>
    
    <!-- 추천 상태 표시 -->
    <div class="signal-indicator">
      <v-chip
        :color="signalColor"
        :text="signalText"
      />
      <p class="mt-2">{{ signalDescription }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts';
import { ref, computed, onMounted } from 'vue';

const props = defineProps<{
  priceData: Array<{ date: string; price: number }>;
  signal: 'BUY' | 'SELL' | 'HOLD';
}>();

const signalColor = computed(() => {
  switch (props.signal) {
    case 'BUY': return 'success';
    case 'SELL': return 'error';
    case 'HOLD': return 'warning';
  }
});

const signalText = computed(() => {
  switch (props.signal) {
    case 'BUY': return '매수 관심';
    case 'SELL': return '매도 관심';
    case 'HOLD': return '관망';
  }
});
</script>
```

### 21.5 에러 처리 (ESG 도메인)

```typescript
// types/error.ts
export enum ESGErrorCode {
  // 표준 분석 (STD)
  STD_VAL_001 = 'ESG-STD-VAL-001',  // 표준 문서 포맷 오류
  STD_PAR_001 = 'ESG-STD-PAR-001',  // 표준 문서 파싱 실패
  
  // 내부 분석 (INT)
  INT_VAL_001 = 'ESG-INT-VAL-001',  // KPI 데이터 형식 오류
  INT_PERM_001 = 'ESG-INT-PERM-001',  // 내부 문서 접근 권한 없음
  
  // 벤치마킹 (BMK)
  BMK_EXT_001 = 'ESG-BMK-EXT-001',  // 경쟁사 보고서 크롤링 실패
  
  // 미디어 분석 (MED)
  MED_AI_001 = 'ESG-MED-AI-001',  // 감성 분석 실패
  
  // 뉴스 인텔리전스 (NWS)
  NWS_EXT_001 = 'ESG-NWS-EXT-001',  // 뉴스 API 호출 실패
  
  // 설문 (SVY)
  SVY_VAL_001 = 'ESG-SVY-VAL-001',  // 설문 응답 데이터 형식 오류
  
  // 중대성 평가 (MAT)
  MAT_SYS_001 = 'ESG-MAT-SYS-001',  // Matrix 계산 오류
  
  // 보고서 생성 (RPT)
  RPT_PAR_001 = 'ESG-RPT-PAR-001',  // 전년도 보고서 파싱 실패
  RPT_AI_001 = 'ESG-RPT-AI-001',  // AI 초안 생성 실패
  
  // ESG 챗봇 (CHAT)
  CHAT_AI_001 = 'ESG-CHAT-AI-001',  // RAG 검색 실패
  
  // 탄소배출권 (CRB)
  CRB_EXT_001 = 'ESG-CRB-EXT-001'  // 가격 API 호출 실패
}

export interface ESGError {
  code: ESGErrorCode;
  message: string;
  userMessage: string;  // 사용자에게 표시할 메시지
  actionable?: string;  // 사용자가 할 수 있는 액션
}
```

```typescript
// composables/useESGError.ts
export function useESGError() {
  const handleError = (error: ESGError) => {
    // 로그 기록
    console.error(`[${error.code}] ${error.message}`);
    
    // 사용자에게 Toast 메시지 표시
    showToast({
      type: 'error',
      message: error.userMessage,
      action: error.actionable
    });
  };

  return { handleError };
}
```

### 21.6 Data Hub 연계 표시

```vue
<template>
  <div class="data-hub-indicator">
    <v-icon v-if="isFromDataHub" color="info">mdi-database-sync</v-icon>
    <span v-if="isFromDataHub" class="text-caption">
      ESG Data Hub 동기화 데이터
    </span>
  </div>
</template>
```

---

**문서 버전**: 1.0.1 (FSD 반영)
**최종 수정일**: 2025-11-18
**작성자**: SKALA 2기 7조
