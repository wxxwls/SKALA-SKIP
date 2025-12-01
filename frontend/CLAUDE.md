# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ESG Double Materiality Issue Pool Construction AI System - Frontend**
- **Team**: SKALA Team 7 (2nd Generation)
- **Framework**: Vue 3 with TypeScript (Composition API)
- **Purpose**: Build a comprehensive ESG (Environmental, Social, Governance) analysis and reporting platform for automated double materiality assessment

## Tech Stack

### Core Technologies
- **Framework**: Vue 3.4.x with Composition API (`<script setup lang="ts">`)
- **Build Tool**: Vite 5.x
- **Language**: TypeScript 5.x (strict mode enabled)
- **State Management**: Pinia 2.x
- **Router**: Vue Router 4.x

### UI & Styling
- **Component Library**: Vuetify 3.x (buttons, modals, forms, cards)
- **Utility CSS**: TailwindCSS 3.x (layout, spacing, responsive design)
- **Icons**: Material Design Icons (@mdi/font)

### Data Visualization & Tables
- **Charts**: ECharts 5.x (line, bar, scatter, materiality matrix)
- **Data Grid**: AG Grid 31.x (sortable, filterable tables)

### HTTP & Testing
- **HTTP Client**: Axios 1.x (with interceptors)
- **Testing Framework**: Vitest 2.x + @vue/test-utils
- **Code Quality**: ESLint 8.x + Prettier 3.x

### Version Control Rules
- ✅ Use **exact versions** in package.json (no `^` or `~` prefixes)
- ✅ Always commit `yarn.lock`
- ✅ Library updates require team approval
- ✅ Use **yarn** instead of npm for all package management

## Project Structure

```
src/
├── api/                # API call modules
│   ├── axios.config.ts # Axios instance with interceptors
│   ├── auth.api.ts
│   ├── issuePool.api.ts
│   └── carbon.api.ts
├── assets/             # Static files (images, fonts, icons)
├── components/         # Reusable UI components
│   ├── common/        # Generic components (Button, Modal, Toast)
│   ├── chart/         # Chart components (LineChart, MaterialityMatrix)
│   └── card/          # Card-type components (IssueCard, CarbonSignalCard)
├── composables/       # Reusable Composition API logic
│   ├── useChart.ts    # Chart configuration helper
│   ├── useValidation.ts # Form validation rules
│   └── useESGError.ts # ESG error handling
├── constants/         # Constant definitions
│   └── esg.ts        # ESG_CONSTANTS, ESG_MODULES
├── layouts/           # Layout components
│   ├── DefaultLayout.vue
│   ├── AuthLayout.vue
│   └── BlankLayout.vue
├── plugins/           # Plugin configurations
│   └── vuetify.ts    # Vuetify theme & settings
├── router/            # Vue Router configuration
│   └── index.ts      # Routes with auth guards
├── stores/            # Pinia stores (domain-separated)
│   ├── authStore.ts
│   ├── issuePoolStore.ts
│   ├── newsStore.ts
│   └── carbonStore.ts
├── styles/            # Global styles
│   ├── variables.css # CSS custom properties
│   └── global.css    # Global styles + Tailwind imports
├── types/             # TypeScript type definitions
│   ├── esg.ts        # Issue, Topic, MaterialityData, CarbonSignal
│   └── error.ts      # ESGErrorCode enum, ESGError, ApiError
├── utils/             # Utility functions
├── views/             # Routable page components
│   ├── home/
│   ├── news/
│   ├── issuepool/
│   ├── report/
│   ├── carbon/
│   └── chatbot/
├── App.vue            # Root component
└── main.ts            # Application entry point
```

## Naming Conventions

### Files
| Type | Pattern | Example | Rules |
|------|---------|---------|-------|
| **Components** | `PascalCase.vue` | `IssueCard.vue` | Minimum 2 words, no single-word names |
| **Views** | `PascalCaseView.vue` | `IssuePoolView.vue` | Must end with "View" |
| **Stores** | `camelCaseStore.ts` | `issuePoolStore.ts` | Must end with "Store" |
| **API Modules** | `camelCase.api.ts` | `issuePool.api.ts` | Must end with ".api.ts" |
| **Composables** | `usePascalCase.ts` | `useChart.ts` | Must start with "use" |
| **Types** | `camelCase.ts` | `esg.ts`, `error.ts` | Lowercase with underscores if needed |

### Code Elements
```typescript
// ✅ Variables: camelCase
const issueList = ref<Issue[]>([]);
const selectedCompany = ref<string | null>(null);

// ✅ Functions: camelCase (start with verb)
function fetchIssueList() { }
function generateReport() { }
async function saveData() { }

// ✅ Booleans: is/has/can prefix
const isLoading = ref(false);
const hasPermission = computed(() => user.value?.role === 'admin');
const canEdit = ref(true);

// ✅ Constants: UPPER_SNAKE_CASE
const DEFAULT_PAGE_SIZE = 20;
const MAX_ISSUE_COUNT = 100;
const API_TIMEOUT = 30000;

// ✅ Props: camelCase with TypeScript types
const props = defineProps<{
  issueId: string;
  chartData: ChartDataset[];
  isVisible: boolean;
}>();

// ✅ Emits: kebab-case with TypeScript types
const emit = defineEmits<{
  'update:modelValue': [value: string];
  'issue-selected': [id: string];
  'close': [];
}>();

// ❌ Bad examples
const data = ref([]); // Too generic
const temp = ref(''); // Meaningless
function doSomething() { } // Vague
```

## Code Organization

### Component Structure (Mandatory Order)

```vue
<script setup lang="ts">
// Imports
import { ref, computed, onMounted } from 'vue';
import { useIssuePoolStore } from '@/stores/issuePoolStore';
import type { Issue } from '@/types/esg';

// Props/Emit definitions
const props = defineProps<{ id: string }>();
const emit = defineEmits<{ 'close': [] }>();

// Constants
const MAX_ITEMS = 10;
const DEBOUNCE_DELAY = 300;

// Composables/Stores
const store = useIssuePoolStore();
const { validateRequired } = useValidation();

// Reactive state (ref, reactive)
const items = ref<Issue[]>([]);
const loading = ref(false);
const searchQuery = ref('');

// Computed properties
const filteredItems = computed(() =>
  items.value.filter(x => x.active && x.title.includes(searchQuery.value))
);

// Methods/Functions
function handleClick() {
  emit('close');
}

async function loadData() {
  loading.value = true;
  try {
    items.value = await store.fetchIssues(props.id);
  } finally {
    loading.value = false;
  }
}

// Lifecycle hooks
onMounted(async () => {
  await loadData();
});
</script>

<template>
  <!-- Template content -->
</template>

<style scoped>
/* Component-specific styles */
</style>
```

### Formatting Rules
- **Indentation**: 2 spaces (no tabs)
- **Semicolons**: Required for all statements
- **Quotes**: Single quotes `'` preferred (double quotes for HTML attributes)
- **Line length**: 120 characters maximum
- **Trailing commas**: None (configured in Prettier)

## Architecture Patterns

### Container/Presentational Pattern

**Container Components (Views)**
- Located in `src/views/`
- Handle data fetching via Pinia store actions
- Manage business logic and state
- Pass data to presentational components via props

```vue
<!-- views/issuepool/IssuePoolView.vue (Container) -->
<script setup lang="ts">
const store = useIssuePoolStore();
const issues = computed(() => store.issues);

onMounted(() => {
  store.fetchIssues(companyId.value);
});

function handleIssueSelect(id: string) {
  router.push(`/issue/${id}`);
}
</script>

<template>
  <IssueList :issues="issues" @issue-selected="handleIssueSelect" />
</template>
```

**Presentational Components**
- Located in `src/components/`
- Receive data via props
- Emit events for user interactions
- No direct API calls or store access
- Pure UI rendering

```vue
<!-- components/card/IssueList.vue (Presentational) -->
<script setup lang="ts">
import type { Issue } from '@/types/esg';

defineProps<{
  issues: Issue[];
}>();

const emit = defineEmits<{
  'issue-selected': [id: string];
}>();
</script>

<template>
  <v-card v-for="issue in issues" :key="issue.id" @click="emit('issue-selected', issue.id)">
    <v-card-title>{{ issue.title }}</v-card-title>
  </v-card>
</template>
```

### State Management Rules (Pinia)

**Store Organization**
- ✅ One store per domain (auth, issuePool, news, carbon)
- ✅ Use Composition API style (`defineStore` with setup function)
- ✅ Structure: State → Getters → Actions

**Store Best Practices**
- ❌ No direct state mutation outside actions
- ❌ No direct API calls from components
- ✅ All async operations in store actions
- ✅ Error handling in store actions
- ✅ Loading states managed in stores

```typescript
// stores/issuePoolStore.ts
export const useIssuePoolStore = defineStore('issuePool', () => {
  // State
  const issues = ref<Issue[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const activeIssues = computed(() =>
    issues.value.filter(issue => issue.active)
  );

  // Actions
  async function fetchIssues(companyId: string) {
    loading.value = true;
    error.value = null;

    try {
      const data = await issuePoolApi.getIssues(companyId);
      issues.value = data;
    } catch (e) {
      error.value = (e as Error).message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  return {
    issues,
    loading,
    error,
    activeIssues,
    fetchIssues
  };
});
```

### API Integration

**API Module Structure**
```typescript
// api/issuePool.api.ts
import apiClient from './axios.config';
import type { Issue, IssueCreateRequest } from '@/types/esg';

const BASE_URL = '/api/v1/issue-pool';

export const issuePoolApi = {
  async getIssues(companyId: string): Promise<Issue[]> {
    const { data } = await apiClient.get(`${BASE_URL}/${companyId}`);
    return data.data;
  },

  async generateIssuePool(companyId: string): Promise<Issue[]> {
    const { data } = await apiClient.post(`${BASE_URL}/${companyId}/generate`);
    return data.data;
  }
};
```

**Axios Configuration**
```typescript
// api/axios.config.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

// Request Interceptor: Add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response Interceptor: Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## ESG Project-Specific Rules

### Constants (src/constants/esg.ts)

```typescript
export const ESG_CONSTANTS = {
  MAX_TOPIC_COUNT: 20,           // Maximum topics before stakeholder survey
  MAX_CORE_ISSUE_COUNT: 20,      // Maximum core issues after materiality assessment
  SURVEY_MAX_SELECTION: 5        // Maximum issues to select in stakeholder survey
} as const;

export const ESG_MODULES = [
  '① Standard Document Management',
  '② Internal Analysis (Data Hub)',
  '③ Benchmarking',
  '④ Media Analysis',
  '⑤ News Intelligence',
  '⑥ Stakeholder Survey',
  '⑦ Materiality Assessment',
  '⑧ Report Generation',
  '⑨ RAG Chatbot',
  '⑩ Carbon Credit'
] as const;
```

### UI Components Specifications

**IssueCard Component**
- Display ESG issue with title and description
- Show financial score and impact score
- Display Data Hub indicator chip when `dataHubLinked === true`
- List sources at bottom
- Emit `issue-selected` event on click

**MaterialityMatrix Component**
- ECharts scatter chart
- X-axis: Financial Materiality (0-10)
- Y-axis: Impact Materiality (0-10)
- Display 20 core issues as scatter points
- Color-code points by category
- Show tooltips with issue details

**SurveyForm Component**
- Exactly 5 issues must be selected (validate with `ESG_CONSTANTS.SURVEY_MAX_SELECTION`)
- Use `v-checkbox` with max selection constraint
- 1-3 score rating for each selected issue using `v-rating :length="3"`
- Disable further selection when 5 issues selected
- Display counter: "Selected: X / 5"

**CarbonSignalCard Component**
- Display signal chip: BUY (success/green), SELL (error/red), HOLD (grey)
- Show confidence percentage (0-100%)
- Display predicted price
- Show recommendation text

### Error Code System

**Format**: `ESG-<MODULE>-<TYPE>-<NUMBER>`

```typescript
// types/error.ts
export enum ESGErrorCode {
  // Standard Document Management
  STD_VAL_001 = 'ESG-STD-VAL-001', // Standard document format error
  STD_PAR_001 = 'ESG-STD-PAR-001', // Standard document parsing failed

  // Internal Analysis
  INT_VAL_001 = 'ESG-INT-VAL-001', // KPI data format error
  INT_PERM_001 = 'ESG-INT-PERM-001', // Internal document access denied

  // Survey
  SVY_VAL_001 = 'ESG-SVY-VAL-001', // Must select exactly 5 issues
  SVY_VAL_002 = 'ESG-SVY-VAL-002', // Score must be 1-3

  // Materiality Assessment
  MAT_SYS_001 = 'ESG-MAT-SYS-001', // Matrix calculation error
  MAT_LIMIT_001 = 'ESG-MAT-LIMIT-001', // 20 Topic limit exceeded

  // Report Generation
  RPT_PAR_001 = 'ESG-RPT-PAR-001', // Previous year report parsing failed
  RPT_AI_001 = 'ESG-RPT-AI-001', // AI draft generation failed

  // Chatbot
  CHAT_RAG_001 = 'ESG-CHAT-RAG-001', // RAG context retrieval failed

  // Carbon Credit
  CRB_PRED_001 = 'ESG-CRB-PRED-001' // Carbon price prediction error
}

export interface ESGError {
  code: ESGErrorCode;
  message: string;
  userMessage: string;
  actionable?: string;
}
```

### Design Tokens (styles/variables.css)

```css
:root {
  /* Brand Colors */
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

## Prohibited Practices

### ❌ Absolutely Forbidden
1. **Options API usage** - Only use Composition API with `<script setup>`
2. **Direct API calls from components** - Always use Pinia store actions
3. **Hardcoded URLs or config values** - Use environment variables
4. **Excessive `any` type usage** - Properly type all variables
5. **Meaningless variable names** - No `data`, `temp`, `test`, `foo`, `bar`
6. **Single-word component names** - Minimum 2 words (e.g., `UserCard` not `Card`)
7. **Tabs for indentation** - Use 2 spaces
8. **Missing TypeScript type annotations** - All props, emits, functions must be typed

## Mandatory Practices

### ✅ Must Follow
1. **TypeScript strict mode** - Explicit types for all props, emits, functions
2. **Props and Emit type definitions** - Use `defineProps<T>()` and `defineEmits<T>()`
3. **Error handling** - Use try-catch for all async operations
4. **Loading states** - Display loading indicators during async operations
5. **Container/Presentational pattern** - Separate data logic from UI
6. **ESLint and Prettier compliance** - Run before commits
7. **Validation** - Validate all user inputs
8. **Responsive design** - Consider mobile/tablet when needed

## Git Workflow

### Branch Strategy
- **main**: Production deployment branch (protected)
- **feature/\***: Feature development (e.g., `feature/issue-pool-generation`)
- **fix/\***: Bug fixes (e.g., `fix/chart-loading-error`)

### Commit Message Format
```
<type>: <subject>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation update
- style: Code formatting (no logic change)
- refactor: Code refactoring
- test: Test code addition
- chore: Build, package manager updates

Examples:
feat: add automatic issue pool generation
fix: resolve materiality matrix rendering issue
docs: update API integration guide
```

### Commit Rules
- Subject line: Max 50 characters
- Use imperative mood ("add" not "added")
- No period at end of subject
- Reference issue numbers if applicable

## Development Checklist

### Before Committing Components
- [ ] No TypeScript errors (`yarn build`)
- [ ] No ESLint errors (`yarn lint`)
- [ ] Props/Emit types defined with TypeScript
- [ ] Component name: PascalCase + minimum 2 words
- [ ] Correct file location (views vs components)
- [ ] API calls only through Pinia store actions
- [ ] Error handling implemented with try-catch
- [ ] Loading state displayed during async operations
- [ ] Responsive design considered (if applicable)
- [ ] Comments added for complex logic only
- [ ] Git commit message follows convention

### ESG-Specific Checklist
- [ ] ESG constants used (`ESG_CONSTANTS.MAX_TOPIC_COUNT`, etc.)
- [ ] 20 Topic limit validation in issue pool generation
- [ ] 5 Issue selection constraint in survey form
- [ ] 1-3 score range validation with `v-rating :length="3"`
- [ ] ESG error codes from `ESGErrorCode` enum
- [ ] Error handler uses `handleESGError` function
- [ ] Data Hub indicator chip displayed when `dataHubLinked === true`
- [ ] Carbon signal color mapping: BUY (success), SELL (error), HOLD (grey)
- [ ] Double Materiality Matrix with correct axes (Financial X, Impact Y)
- [ ] Navigator with 10 ESG modules

## Testing

### Framework & Tools
- **Framework**: Vitest 2.x
- **Utils**: @vue/test-utils
- **Coverage**: Minimum 80% for statements, branches, functions, lines
- **Test Files**: `*.test.ts` or `*.spec.ts`

### Testing Rules
- ✅ All new components must have unit tests
- ✅ All store actions must have tests
- ✅ Mock external dependencies (API calls, localStorage)
- ✅ Test both success and error scenarios
- ✅ Test edge cases (empty data, max limits, validation errors)

### Example Test
```typescript
// components/__tests__/IssueCard.test.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import IssueCard from '@/components/card/IssueCard.vue';

describe('IssueCard', () => {
  it('renders issue title correctly', () => {
    const wrapper = mount(IssueCard, {
      props: {
        issue: {
          id: '1',
          title: 'Climate Change Risk',
          description: 'Test description'
        }
      }
    });

    expect(wrapper.text()).toContain('Climate Change Risk');
  });

  it('emits issue-selected event when clicked', async () => {
    const wrapper = mount(IssueCard, {
      props: { issue: { id: '1', title: 'Test' } }
    });

    await wrapper.trigger('click');

    expect(wrapper.emitted('issue-selected')).toBeTruthy();
    expect(wrapper.emitted('issue-selected')?.[0]).toEqual(['1']);
  });
});
```

## AI Development Guidelines

### When Creating Components
```
[System]
You are a Vue 3 frontend developer following SKALA ESG project standards.

[Task]
Create a new component: IssueCard.vue

[Requirements]
- Use <script setup lang="ts">
- Follow PascalCase naming (minimum 2 words)
- Define Props with TypeScript types
- Define Emits with TypeScript types
- Use Vuetify 3 components for UI
- Follow 2 spaces indentation
- Add proper error handling
- Include loading states for async operations

[Constraints]
- No Options API
- No direct API calls in component
- No hardcoded values
- Must be reusable and presentational
- Follow Container/Presentational pattern
```

## Common Development Commands

```bash
# Development
yarn dev             # Start dev server (http://localhost:5173)
yarn build           # Build for production
yarn preview         # Preview production build

# Code Quality
yarn lint            # Run ESLint
yarn format          # Run Prettier

# Testing
yarn test            # Run tests
yarn test:coverage   # Run tests with coverage report

# Package Management
yarn add <package>   # Add a dependency
yarn add -D <package> # Add a dev dependency
yarn remove <package> # Remove a dependency
```

## Environment Variables

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8080
VITE_APP_TITLE=ESG IssuePool (Dev)

# .env.production
VITE_API_BASE_URL=https://api.esgskala.com
VITE_APP_TITLE=ESG IssuePool

# Usage in code
const apiUrl = import.meta.env.VITE_API_BASE_URL;
```

## Reference Documentation

- **Korean Standard**: `docs/01-frontend-standard-kr.md`
- **English Standard**: `docs/02-frontend-standard-en.md`
- **JSON Schema**: `docs/03-frontend-standard.json`

---

**Document Version**: 1.1
**Last Updated**: 2025-11-23
**Maintained By**: SKALA Team 7
