<template>
  <div class="login-screen">
    <!-- Left Side - Visual Section -->
    <div class="visual-section">
      <!-- Background Image - 서린빌딩 -->
      <div class="visual-background">
        <img :src="seorinBg" alt="서린빌딩" />
      </div>

      <!-- Semi-transparent overlay for text readability -->
      <div class="visual-overlay" />

      <!-- Content on Left Side -->
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

        <!-- Description -->
        <div class="description-title">SK ESG Intelligence Platform</div>

        <div class="description-subtitle">
          지속가능한 미래를 위한 스마트 솔루션
        </div>
      </div>
    </div>

    <!-- Right Side - Login Form -->
    <div class="form-section">
      <div class="form-wrapper">
        <!-- Welcome Text -->
        <div class="welcome-section">
          <div class="welcome-title">환영합니다</div>
          <div class="welcome-subtitle">임직원 계정으로 로그인하세요</div>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin">
          <!-- Username Input -->
          <div class="input-group">
            <label class="input-label">이메일</label>
            <input
              v-model="username"
              type="email"
              placeholder="이메일을 입력하세요 (예: user@sk.com)"
              class="input-field"
              :class="{ 'input-error': username && !isValidEmail(username) }"
              @focus="handleEmailFocus"
              @blur="handleEmailBlur"
            />
            <div v-if="username && !isValidEmail(username)" class="error-message">
              올바른 이메일 형식이 아닙니다
            </div>
          </div>

          <!-- Password Input -->
          <div class="input-group last">
            <label class="input-label">비밀번호</label>
            <input
              v-model="password"
              type="password"
              placeholder="비밀번호를 입력하세요"
              class="input-field"
              @focus="handlePasswordFocus"
              @blur="handlePasswordBlur"
            />
          </div>

          <!-- Login Button -->
          <button
            type="submit"
            :disabled="!username || !password || isLoading || !isValidEmail(username)"
            class="login-button"
            :class="{ 'login-button-active': username && password && isValidEmail(username) }"
          >
            <template v-if="isLoading">
              <div class="loading-spinner" />
              로그인 중...
            </template>
            <template v-else>
              <LogIn class="w-5 h-5" />
              로그인
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

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { LogIn } from 'lucide-vue-next'
import skAxLogo from '../assets/SK_AX-removebg-preview (1).png'
import seorinBg from '../assets/서린빌딩.webp'
import skipLogo from '../assets/SKIP-removebg-preview.png'
import esgMark from '../assets/ESG-removebg-preview.png'
import butterflyImg from '../assets/나비-removebg-preview.png'

const emit = defineEmits<{
  login: []
}>()

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const showEsg = ref(false)
const animationComplete = ref(false)
const butterflyReturned = ref(false)

onMounted(() => {
  setTimeout(() => {
    showEsg.value = true
  }, 500)

  setTimeout(() => {
    animationComplete.value = true
  }, 3500)

  setTimeout(() => {
    butterflyReturned.value = true
  }, 4000)
})

const isValidEmail = (email: string) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const handleLogin = () => {
  if (username.value && password.value && isValidEmail(username.value)) {
    isLoading.value = true
    setTimeout(() => {
      isLoading.value = false
      emit('login')
    }, 800)
  }
}

const handleEmailFocus = (e: FocusEvent) => {
  const target = e.target as HTMLInputElement
  if (!username.value || isValidEmail(username.value)) {
    target.style.borderColor = '#FF8F68'
    target.style.boxShadow = '0 0 0 4px rgba(255,143,104,0.1)'
  }
}

const handleEmailBlur = (e: FocusEvent) => {
  const target = e.target as HTMLInputElement
  if (username.value && !isValidEmail(username.value)) {
    target.style.borderColor = '#EF4444'
    target.style.boxShadow = '0 0 0 4px rgba(239,68,68,0.1)'
  } else {
    target.style.borderColor = '#E8EAED'
    target.style.boxShadow = 'none'
  }
}

const handlePasswordFocus = (e: FocusEvent) => {
  const target = e.target as HTMLInputElement
  target.style.borderColor = '#FF8F68'
  target.style.boxShadow = '0 0 0 4px rgba(255,143,104,0.1)'
}

const handlePasswordBlur = (e: FocusEvent) => {
  const target = e.target as HTMLInputElement
  target.style.borderColor = '#E8EAED'
  target.style.boxShadow = 'none'
}
</script>

<style scoped>
.login-screen {
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
  background: #FFFFFF;
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
  margin-bottom: 48px;
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
  height: 120px;
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
  color: #FFFFFF;
  margin-bottom: 20px;
  letter-spacing: -0.5px;
  text-shadow: 0 3px 8px rgba(0, 0, 0, 0.5);
}

.description-subtitle {
  font-size: 18px;
  font-weight: 500;
  color: #FFFFFF;
  line-height: 1.7;
  max-width: 500px;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
}

/* Form Section */
.form-section {
  width: 40%;
  height: 100%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.form-wrapper {
  width: 100%;
  max-width: 480px;
  padding: 60px;
}

.welcome-section {
  margin-bottom: 48px;
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  color: #1A1F2E;
  margin-bottom: 12px;
}

.welcome-subtitle {
  font-size: 15px;
  color: #6B7280;
  line-height: 1.6;
}

.input-group {
  margin-bottom: 24px;
}

.input-group.last {
  margin-bottom: 36px;
}

.input-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1A1F2E;
  margin-bottom: 10px;
}

.input-field {
  width: 100%;
  padding: 16px 18px;
  border-radius: 12px;
  border: 2px solid #E8EAED;
  font-size: 15px;
  color: #1A1F2E;
  outline: none;
  transition: all 0.2s;
  background: #FFFFFF;
}

.input-field.input-error {
  border-color: #EF4444;
}

.error-message {
  margin-top: 8px;
  font-size: 13px;
  color: #EF4444;
  font-weight: 500;
}

.login-button {
  width: 100%;
  padding: 18px;
  background: #E8EAED;
  border-radius: 12px;
  border: none;
  cursor: not-allowed;
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.login-button-active {
  background: linear-gradient(120deg, #FF8F68, #F76D47);
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(247, 109, 71, 0.35);
}

.login-button-active:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(247, 109, 71, 0.4);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFFFFF;
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
  font-size: 12px;
  color: #9CA3AF;
}
</style>
