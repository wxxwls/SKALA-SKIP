<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { KeyRound, Eye, EyeOff, Check, X } from 'lucide-vue-next';
import { useAuthStore } from '@/stores';
import skAxLogo from '@/assets/SK_AX-removebg-preview (1).png';
import seorinBg from '@/assets/서린빌딩.webp';
import skipLogo from '@/assets/SKIP-removebg-preview.png';
import esgMark from '@/assets/ESG-removebg-preview.png';
import butterflyImg from '@/assets/나비-removebg-preview.png';

const butterflyReturned = ref(false);

// Password validation regex: at least 8 chars with letters, numbers, and special characters
const PASSWORD_REGEX = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
const FOCUS_BORDER_COLOR = 'var(--color-primary-light)';
const FOCUS_BOX_SHADOW = '0 0 0 4px rgba(255,143,104,0.1)';
const ERROR_BORDER_COLOR = 'var(--color-error)';
const ERROR_BOX_SHADOW = '0 0 0 4px rgba(239,68,68,0.1)';
const DEFAULT_BORDER_COLOR = 'var(--color-border)';

const authStore = useAuthStore();
const router = useRouter();

const newPassword = ref('');
const confirmPassword = ref('');
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);
const showEsg = ref(false);
const animationComplete = ref(false);

// Password validation checks
const hasMinLength = computed(() => newPassword.value.length >= 8);
const hasLetter = computed(() => /[A-Za-z]/.test(newPassword.value));
const hasNumber = computed(() => /\d/.test(newPassword.value));
const hasSpecialChar = computed(() => /[@$!%*#?&]/.test(newPassword.value));

const isValidNewPassword = computed(() => {
  return PASSWORD_REGEX.test(newPassword.value);
});

const isPasswordMatch = computed(() => {
  return newPassword.value === confirmPassword.value && confirmPassword.value !== '';
});

const isFormValid = computed(() => {
  return isValidNewPassword.value && isPasswordMatch.value;
});

onMounted(() => {
  setTimeout(() => {
    showEsg.value = true;
  }, 500);

  setTimeout(() => {
    animationComplete.value = true;
  }, 3500);

  setTimeout(() => {
    butterflyReturned.value = true;
  }, 4000);
});

async function handleSetPassword() {
  if (!isFormValid.value) return;

  const success = await authStore.setPassword(newPassword.value);

  if (success) {
    router.push('/');
  }
}

function handleInputFocus(e: FocusEvent, hasError: boolean = false) {
  const target = e.target as HTMLInputElement;
  if (!hasError) {
    target.style.borderColor = FOCUS_BORDER_COLOR;
    target.style.boxShadow = FOCUS_BOX_SHADOW;
  }
}

function handleInputBlur(e: FocusEvent, hasError: boolean = false) {
  const target = e.target as HTMLInputElement;
  if (hasError) {
    target.style.borderColor = ERROR_BORDER_COLOR;
    target.style.boxShadow = ERROR_BOX_SHADOW;
  } else {
    target.style.borderColor = DEFAULT_BORDER_COLOR;
    target.style.boxShadow = 'none';
  }
}
</script>

<template>
  <div class="change-password-container">
    <!-- Left Side - Visual Section -->
    <div class="visual-section">
      <!-- Background Image - 서린빌딩 -->
      <div class="visual-background">
        <img :src="seorinBg" alt="서린빌딩" />
      </div>

      <!-- Overlay -->
      <div class="visual-overlay" />

      <!-- Content -->
      <div class="visual-content">
        <!-- SK AX Logo (나비 없는 버전) -->
        <div class="sk-logo-container">
          <img :src="skAxLogo" alt="SK 주식회사 AX" class="sk-logo" />
        </div>

        <!-- SKIP with ESG Logo -->
        <div class="skip-logo-container">
          <div class="skip-part">
            <img :src="skipLogo" alt="SKIP" class="skip-logo-img" />
          </div>

          <!-- ESG Mark -->
          <div class="esg-container" :class="{ 'show': showEsg }">
            <img
              :src="esgMark"
              alt="ESG"
              class="esg-mark"
              :class="{ 'visible': showEsg }"
            />
            <!-- Butterfly draws ESG and flies to SK AX logo -->
            <img
              :src="butterflyImg"
              alt="나비"
              class="butterfly"
              :class="{ 'drawing': showEsg && !butterflyReturned, 'fly-to-sk': butterflyReturned }"
            />
          </div>
        </div>

        <div class="description-title">SK ESG Intelligence Platform</div>

        <div class="description-subtitle">
          지속가능한 미래를 위한 스마트 솔루션
        </div>
      </div>
    </div>

    <!-- Right Side - Change Password Form -->
    <div class="form-container">
      <div class="form-wrapper">
        <!-- Welcome Text -->
        <div class="welcome-section">
          <div class="welcome-title">비밀번호 설정</div>
          <div class="welcome-subtitle">
            최초 로그인을 위해 새로운 비밀번호를 설정해주세요
          </div>
        </div>

        <!-- Change Password Form -->
        <form @submit.prevent="handleSetPassword">
          <!-- New Password Input -->
          <div class="input-group">
            <label class="input-label">새 비밀번호</label>
            <div class="password-input-wrapper">
              <input
                v-model="newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                placeholder="새 비밀번호를 입력하세요"
                class="input-field"
                :class="{ 'input-error': newPassword && !isValidNewPassword }"
                @focus="(e) => handleInputFocus(e, newPassword !== '' && !isValidNewPassword)"
                @blur="(e) => handleInputBlur(e, newPassword !== '' && !isValidNewPassword)"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showNewPassword = !showNewPassword"
              >
                <Eye v-if="!showNewPassword" class="toggle-icon" />
                <EyeOff v-else class="toggle-icon" />
              </button>
            </div>

            <!-- Password Requirements -->
            <div v-if="newPassword" class="password-requirements">
              <div class="requirement" :class="{ valid: hasMinLength }">
                <Check v-if="hasMinLength" class="requirement-icon valid" />
                <X v-else class="requirement-icon invalid" />
                <span>최소 8자 이상</span>
              </div>
              <div class="requirement" :class="{ valid: hasLetter }">
                <Check v-if="hasLetter" class="requirement-icon valid" />
                <X v-else class="requirement-icon invalid" />
                <span>영문자 포함</span>
              </div>
              <div class="requirement" :class="{ valid: hasNumber }">
                <Check v-if="hasNumber" class="requirement-icon valid" />
                <X v-else class="requirement-icon invalid" />
                <span>숫자 포함</span>
              </div>
              <div class="requirement" :class="{ valid: hasSpecialChar }">
                <Check v-if="hasSpecialChar" class="requirement-icon valid" />
                <X v-else class="requirement-icon invalid" />
                <span>특수문자 포함 (@$!%*#?&)</span>
              </div>
            </div>
          </div>

          <!-- Confirm Password Input -->
          <div class="input-group">
            <label class="input-label">새 비밀번호 확인</label>
            <div class="password-input-wrapper">
              <input
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="새 비밀번호를 다시 입력하세요"
                class="input-field"
                :class="{ 'input-error': confirmPassword && !isPasswordMatch }"
                @focus="(e) => handleInputFocus(e, confirmPassword !== '' && !isPasswordMatch)"
                @blur="(e) => handleInputBlur(e, confirmPassword !== '' && !isPasswordMatch)"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <Eye v-if="!showConfirmPassword" class="toggle-icon" />
                <EyeOff v-else class="toggle-icon" />
              </button>
            </div>
            <div v-if="confirmPassword && !isPasswordMatch" class="error-message">
              비밀번호가 일치하지 않습니다
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="authStore.error" class="form-error-message">
            {{ authStore.error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="!isFormValid || authStore.isLoading"
            class="submit-button"
            :class="{ 'submit-button-active': isFormValid }"
          >
            <template v-if="authStore.isLoading">
              <div class="loading-spinner" />
              설정 중...
            </template>
            <template v-else>
              <KeyRound class="w-5 h-5" />
              비밀번호 설정
            </template>
          </button>
        </form>

        <!-- Copyright -->
        <div class="copyright">
          © 2025 SK 주식회사 AX. All rights reserved.
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.change-password-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  min-width: 1440px;
  min-height: 900px;
  position: relative;
  overflow: hidden;
}

/* Visual Section */
.visual-section {
  width: 60%;
  height: 100%;
  position: relative;
  background: var(--color-surface);
  overflow: hidden;
}

.visual-background {
  position: absolute;
  inset: 0;
}

.visual-background img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.visual-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.3) 0%, rgba(0, 0, 0, 0.5) 100%);
  z-index: 1;
}

.visual-content {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px;
}

/* SK Logo Container */
.sk-logo-container {
  position: relative;
  display: inline-block;
  margin-bottom: 32px;
}

.sk-logo {
  width: 200px;
  height: auto;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.15));
}

/* SKIP Logo Container */
.skip-logo-container {
  position: relative;
  display: flex;
  align-items: flex-start;
  margin-bottom: 48px;
  height: 160px;
}

.skip-part {
  position: relative;
}

.skip-logo-img {
  height: 260px;
  width: auto;
  filter: drop-shadow(0 4px 20px rgba(234, 0, 44, 0.3));
}

/* ESG Container - SK와 IP 사이 아래 */
.esg-container {
  position: absolute;
  left: 95px;
  top: 40px;
  width: 120px;
  height: 100px;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.esg-container.show {
  opacity: 1;
}

/* ESG Mark */
.esg-mark {
  position: absolute;
  left: 0;
  top: 0;
  width: 100px;
  height: auto;
  opacity: 0;
  clip-path: inset(0 100% 0 0);
  transition: clip-path 2s ease-out;
  filter: drop-shadow(0 2px 10px rgba(255, 143, 0, 0.4));
}

.esg-mark.visible {
  opacity: 1;
  clip-path: inset(0 0 0 0);
}

/* Butterfly Animation - ESG 그리기 후 대각선 오른쪽 아래로 이동 */
.butterfly {
  position: absolute;
  width: 60px;
  height: auto;
  left: -50px;
  top: 5px;
  z-index: 20;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
  opacity: 0;
}

.butterfly.drawing {
  opacity: 1;
  animation: butterflyDrawESG 3s ease-in-out forwards;
}

.butterfly.fly-to-sk {
  opacity: 1;
  animation: butterflyFlyToSK 1.5s ease-in-out forwards, butterflyIdleAtSK 2s ease-in-out 1.5s infinite;
}

/* 나비가 ESG를 부드럽게 그리는 애니메이션 */
@keyframes butterflyDrawESG {
  0% {
    left: -30px;
    top: 20px;
    transform: rotate(-5deg) scale(1);
    opacity: 0;
  }
  3% {
    opacity: 1;
  }
  /* E 시작 - 위에서 아래로 부드럽게 */
  8% {
    left: 5px;
    top: 8px;
    transform: rotate(8deg) scale(1);
  }
  15% {
    left: 15px;
    top: 25px;
    transform: rotate(-3deg) scale(1);
  }
  22% {
    left: 25px;
    top: 18px;
    transform: rotate(5deg) scale(1);
  }
  /* S 그리기 - 곡선으로 부드럽게 */
  32% {
    left: 40px;
    top: 12px;
    transform: rotate(10deg) scale(1);
  }
  42% {
    left: 50px;
    top: 22px;
    transform: rotate(-5deg) scale(1);
  }
  52% {
    left: 55px;
    top: 30px;
    transform: rotate(8deg) scale(1);
  }
  /* G 그리기 - 원형으로 부드럽게 */
  62% {
    left: 70px;
    top: 15px;
    transform: rotate(-3deg) scale(1);
  }
  72% {
    left: 80px;
    top: 25px;
    transform: rotate(6deg) scale(1);
  }
  82% {
    left: 88px;
    top: 20px;
    transform: rotate(-2deg) scale(1);
  }
  /* 완료 - 잠시 멈춤 */
  92% {
    left: 95px;
    top: 18px;
    transform: rotate(0deg) scale(1);
    opacity: 1;
  }
  100% {
    left: 95px;
    top: 18px;
    transform: rotate(0deg) scale(1);
    opacity: 1;
  }
}

/* 나비가 최종 위치로 한번에 부드럽게 날아가는 애니메이션 */
@keyframes butterflyFlyToSK {
  0% {
    left: 95px;
    top: 18px;
    transform: rotate(0deg) scale(1);
  }
  100% {
    left: -60px;
    top: -180px;
    transform: rotate(5deg) scale(1);
  }
}

/* 최종 위치에서 나비 idle 애니메이션 */
@keyframes butterflyIdleAtSK {
  0%, 100% {
    left: -60px;
    top: -180px;
    transform: rotate(5deg) translateY(0);
  }
  50% {
    left: -60px;
    top: -180px;
    transform: rotate(10deg) translateY(-8px);
  }
}

.description-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-surface);
  margin-bottom: 20px;
  letter-spacing: -0.5px;
  text-shadow: 0 3px 8px rgba(0, 0, 0, 0.5);
}

.description-subtitle {
  font-size: 18px;
  font-weight: 500;
  color: var(--color-surface);
  line-height: 1.7;
  max-width: 500px;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
}

/* Form Section */
.form-container {
  width: 40%;
  height: 100%;
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
}

.form-wrapper {
  width: 100%;
  max-width: 480px;
  padding: 60px;
}

.welcome-section {
  margin-bottom: 36px;
}

.welcome-title {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: 12px;
}

.welcome-subtitle {
  font-size: 15px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.input-group {
  margin-bottom: 24px;
}

.input-group:last-of-type {
  margin-bottom: 32px;
}

.input-label {
  display: block;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 10px;
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-field {
  width: 100%;
  padding: 16px 48px 16px 18px;
  border-radius: var(--radius-lg);
  border: 2px solid var(--color-border);
  font-size: 15px;
  color: var(--color-text-primary);
  outline: none;
  transition: all var(--transition-normal);
  background: var(--color-surface);
}

.input-field.input-error {
  border-color: var(--color-error);
}

.password-toggle {
  position: absolute;
  right: 16px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-icon {
  width: 20px;
  height: 20px;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
}

.password-toggle:hover .toggle-icon {
  color: var(--color-text-secondary);
}

.password-requirements {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-muted);
  padding: 4px 8px;
  background: var(--color-background);
  border-radius: var(--radius-sm);
}

.requirement.valid {
  color: var(--color-success);
  background: rgba(34, 197, 94, 0.1);
}

.requirement-icon {
  width: 14px;
  height: 14px;
}

.requirement-icon.valid {
  color: var(--color-success);
}

.requirement-icon.invalid {
  color: var(--color-text-muted);
}

.error-message {
  margin-top: 8px;
  font-size: 13px;
  color: var(--color-error);
  font-weight: var(--font-weight-medium);
}

.form-error-message {
  padding: 14px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-md);
  color: var(--color-error);
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  margin-bottom: 20px;
  text-align: center;
}

.submit-button {
  width: 100%;
  padding: 18px;
  background: var(--color-border);
  border-radius: var(--radius-lg);
  border: none;
  cursor: not-allowed;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-surface);
  transition: all var(--transition-slow);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.submit-button-active {
  background: var(--gradient-primary);
  cursor: pointer;
  box-shadow: var(--shadow-primary);
}

.submit-button-active:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(247, 109, 71, 0.4);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--color-surface);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.copyright {
  margin-top: 48px;
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}
</style>
