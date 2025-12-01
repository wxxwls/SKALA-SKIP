# Frontend Development Standard

**ESG Issue Pool Construction AI System**
**Version 1.0**
**SKALA Team 7**

---

## Document Overview

This document defines the **Frontend Development Standard** for the ESG Double Materiality Issue Pool Automatic Construction Service.

**Purpose**: To provide unified rules to prevent conflicts, inconsistencies, and errors during final code merging when multiple developers use AI (Claude, GPT, etc.) for concurrent development.

**Target**: Vue 3-based frontend development

---

## 1. Tech Stack and Version Pinning

### 1.1 Core Tech Stack

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

### 1.2 Version Pinning Rules

- Use **exact versions** in package.json (no ^, ~ prefixes)
- **package-lock.json** must be committed
- Library updates require team approval

---

## 2. Project Structure

### 2.1 Directory Structure

```
src/
├── assets/              # Static files (images, fonts, etc.)
├── components/          # Reusable UI components
│   ├── common/         # Common components (Button, Modal, etc.)
│   ├── chart/          # Chart components
│   └── card/           # Card-type components
├── layouts/            # Layout components
│   ├── DefaultLayout.vue
│   ├── AuthLayout.vue
│   └── BlankLayout.vue
├── views/              # Routable pages
│   ├── home/
│   ├── news/
│   ├── issuepool/
│   ├── report/
│   ├── carbon/
│   └── chatbot/
├── stores/             # Pinia stores
│   ├── auth.ts
│   ├── issuePool.ts
│   ├── news.ts
│   └── carbon.ts
├── api/                # API call modules
│   ├── auth.api.ts
│   ├── issuePool.api.ts
│   └── carbon.api.ts
├── composables/        # Composition API reusable logic
│   ├── useChart.ts
│   └── useValidation.ts
├── router/             # Router configuration
│   └── index.ts
├── utils/              # Utility functions
├── types/              # TypeScript type definitions
├── styles/             # Global styles
│   ├── variables.css   # CSS variables
│   └── global.css
└── main.ts
```

---

## 3. Naming Conventions

### 3.1 File Names

- **Components**: `PascalCase.vue` (e.g., `IssueCard.vue`)
- **View Pages**: `PascalCase + View.vue` (e.g., `IssuePoolView.vue`)
- **Stores**: `camelCase + Store.ts` (e.g., `issuePoolStore.ts`)
- **API Modules**: `camelCase + .api.ts` (e.g., `carbonApi.ts`)
- **Composables**: `use + PascalCase.ts` (e.g., `useChart.ts`)

### 3.2 Variables & Functions

```typescript
// Variables: camelCase
const issueList = ref([]);
const selectedCompany = ref(null);

// Functions: camelCase (verb first)
function fetchIssueList() { }
function generateReport() { }

// Boolean: is/has/can prefix
const isLoading = ref(false);
const hasPermission = computed(() => true);

// Constants: UPPER_SNAKE_CASE
const DEFAULT_PAGE_SIZE = 20;
const MAX_ISSUE_COUNT = 100;
```

---

## 4. Coding Conventions

### 4.1 Composition API Usage

```vue
<script setup lang="ts">
// ✅ Recommended: <script setup> + Composition API
import { ref, computed, onMounted } from 'vue';

const count = ref(0);
const doubleCount = computed(() => count.value * 2);

onMounted(() => {
  console.log('Component mounted');
});
</script>
```

### 4.2 Code Order

```vue
<script setup lang="ts">
// 1. Imports
import { ref, computed } from 'vue';
import { useIssuePoolStore } from '@/stores/issuePool';

// 2. Props/Emit definitions
const props = defineProps<{ id: string }>();
const emit = defineEmits<{ 'close': [] }>();

// 3. Constants
const MAX_ITEMS = 10;

// 4. Composables/Stores
const store = useIssuePoolStore();

// 5. Reactive state
const items = ref([]);
const loading = ref(false);

// 6. Computed properties
const filteredItems = computed(() => items.value.filter(x => x.active));

// 7. Methods
function handleClick() {
  emit('close');
}

// 8. Lifecycle hooks
onMounted(async () => {
  await loadData();
});
</script>
```

### 4.3 Indentation & Formatting

- **Indentation**: 2 spaces (no tabs)
- **Semicolons**: Required (unified ESLint rule)
- **Quotes**: Single quotes `'` preferred
- **Line length**: 120 characters limit

---

## 5. State Management (Pinia)

### 5.1 Store Structure

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

  return {
    issues,
    loading,
    error,
    activeIssues,
    fetchIssues
  };
});
```

---

## 6. API Integration Standards

### 6.1 API Module Structure

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
  }
};
```

### 6.2 Error Handling

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
    showErrorToast('Failed to load data');
  } finally {
    loading.value = false;
  }
}
```

---

## 7. UI/UX Standards

### 7.1 Design System

- **UI Library**: Vuetify 3.x (buttons, modals, forms)
- **Layout/Styling**: TailwindCSS 3.x
- **Charts**: ECharts 5.x
- **Data Grid**: AG Grid 31.x

### 7.2 Design Tokens

```css
/* styles/variables.css */
:root {
  --color-primary: #FF7A00;
  --color-secondary: #2C3E50;
  --color-success: #4CAF50;
  --color-warning: #FFC107;
  --color-error: #F44336;

  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  --font-family: 'Pretendard', sans-serif;
  --font-size-sm: 12px;
  --font-size-md: 14px;
  --font-size-lg: 16px;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

---

## 8. Testing Standards

### 8.1 Unit Testing (Vitest)

```typescript
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import IssueCard from '@/components/IssueCard.vue';

describe('IssueCard', () => {
  it('renders issue title correctly', () => {
    const wrapper = mount(IssueCard, {
      props: {
        issue: {
          id: '1',
          title: 'Test Issue'
        }
      }
    });

    expect(wrapper.text()).toContain('Test Issue');
  });
});
```

---

## 9. Git & Commit Messages

### 9.1 Git Flow

- **main**: Production deployment branch
- **feature/***: Feature development (e.g., `feature/issue-pool`)
- **fix/***: Bug fixes (e.g., `fix/login-error`)

### 9.2 Commit Message Rules

```bash
<type>: <subject>

# Types
feat: New feature
fix: Bug fix
docs: Documentation update
style: Code formatting (semicolons, line breaks)
refactor: Code refactoring
test: Test code addition
chore: Build, package manager updates

# Examples
feat: add automatic issue pool generation
fix: resolve chart data loading error
docs: add README installation guide
```

---

## 10. AI Prompt Guidelines

### 10.1 Component Creation

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
- 2 spaces indentation
- Add TypeScript types

[Constraints]
- No Options API
- No direct API calls
- Must be reusable
```

---

## 11. Prohibited Practices

### 11.1 Forbidden

❌ **Absolutely forbidden**:
- Options API usage
- Direct API calls in components
- Hardcoded URLs, config values
- Excessive `any` type usage
- Meaningless variable names (data, temp, test)
- Single-word component names

### 11.2 Mandatory

✅ **Must follow**:
- TypeScript type annotations
- Props/Emit type definitions
- Error handling (try-catch)
- Loading state display
- Reusable component design
- Clear variable/function names

---

## 12. Checklist

Before completing component development:

- [ ] No TypeScript errors
- [ ] No ESLint errors
- [ ] Props/Emit types defined
- [ ] Component name: PascalCase + 2+ words
- [ ] Correct file location (views vs components)
- [ ] API calls only through Store
- [ ] Error handling & Loading state implemented
- [ ] Responsive design considered (if needed)
- [ ] Comments added (complex logic only)
- [ ] Git commit message rules followed

---

**Document Version**: 1.0
**Last Modified**: 2025-11-18
**Author**: SKALA Team 7

---

## 21. ESG Project-Specific Rules

### 21.1 UI Structure (FSD-Based)

**Navigator (Left Panel)**
```vue
<template>
  <nav class="navigator">
    <ul>
      <li>① Standard Document Management</li>
      <li>② Internal Analysis (Data Hub)</li>
      <li>③ Benchmarking</li>
      <li>④ Media Analysis</li>
      <li>⑤ News Intelligence</li>
      <li>⑥ Stakeholder Survey</li>
      <li>⑦ Materiality Assessment</li>
      <li>⑧ Report Generation</li>
      <li>⑨ RAG Chatbot</li>
      <li>⑩ Carbon Credit</li>
    </ul>
  </nav>
</template>
```

### 21.2 Topic Limit (20 Topics)

```typescript
// constants/esg.ts
export const ESG_CONSTANTS = {
  MAX_TOPIC_COUNT: 20,
  MAX_CORE_ISSUE_COUNT: 20,
  SURVEY_MAX_SELECTION: 5
} as const;

// Validation in component
const topics = ref<Topic[]>([]);

function validateTopicLimit() {
  if (topics.value.length > ESG_CONSTANTS.MAX_TOPIC_COUNT) {
    throw new Error(`Maximum ${ESG_CONSTANTS.MAX_TOPIC_COUNT} topics allowed`);
  }
}
```

### 21.3 Stakeholder Survey UI

```vue
<template>
  <div class="survey">
    <h2>Select 5 Issues (Required)</h2>
    
    <div v-for="issue in issues" :key="issue.id" class="issue-item">
      <v-checkbox 
        v-model="selectedIssues"
        :value="issue.id"
        :disabled="isMaxSelected && !isSelected(issue.id)"
      />
      
      <!-- Score: 1-3 -->
      <v-rating
        v-if="isSelected(issue.id)"
        v-model="scores[issue.id]"
        :length="3"
        active-color="primary"
      />
    </div>
    
    <p>Selected: {{ selectedIssues.length }} / 5</p>
  </div>
</template>

<script setup lang="ts">
const selectedIssues = ref<number[]>([]);
const scores = ref<Record<number, number>>({});

const isMaxSelected = computed(() => selectedIssues.value.length >= 5);
</script>
```

### 21.4 Error Code System

```typescript
// types/esgError.ts
export enum ESGErrorCode {
  STD_VAL_001 = 'ESG-STD-VAL-001',
  INT_VAL_002 = 'ESG-INT-VAL-002',
  SVY_VAL_001 = 'ESG-SVY-VAL-001',
  MAT_LIMIT_001 = 'ESG-MAT-LIMIT-001',
  RPT_AI_001 = 'ESG-RPT-AI-001',
  CHAT_RAG_001 = 'ESG-CHAT-RAG-001',
  CRB_PRED_001 = 'ESG-CRB-PRED-001'
}

// Error handler
function handleESGError(error: ApiError) {
  const message = getErrorMessage(error.code);
  showToast(message, 'error');
}
```

### 21.5 Data Hub Integration Indicator

```vue
<template>
  <v-chip 
    v-if="topic.dataHubLinked" 
    color="success" 
    size="small"
  >
    <v-icon start>mdi-database</v-icon>
    Data Hub
  </v-chip>
</template>
```

### 21.6 Carbon Trading Signals

```vue
<template>
  <v-card class="carbon-signal">
    <v-chip :color="signalColor">{{ signal }}</v-chip>
    <div>Confidence: {{ (confidence * 100).toFixed(0) }}%</div>
  </v-card>
</template>

<script setup lang="ts">
const signalColor = computed(() => {
  if (signal.value === 'BUY') return 'success';
  if (signal.value === 'SELL') return 'error';
  return 'grey';
});
</script>
```

### 21.7 Checklist

- [ ] 20 Topic limit constant used
- [ ] 5 Issue selection in survey (validation)
- [ ] 1-3 score rating component
- [ ] ESG error code enum implemented
- [ ] Data Hub indicator chip
- [ ] Carbon signal color coding (BUY: green, SELL: red, HOLD: grey)
- [ ] Year-over-year comparison chart
- [ ] Navigator with 10 modules

---

**This section defines ESG project-specific frontend rules based on FSD.**

