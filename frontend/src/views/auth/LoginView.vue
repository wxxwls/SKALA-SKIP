<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { LogIn, Volume2, VolumeX } from 'lucide-vue-next';
import { useAuthStore } from '@/stores';
import skAxLogo from '@/assets/SK_AX-removebg-preview (1).png';
import seorinBg from '@/assets/서린빌딩.webp';
import skipLogo from '@/assets/SKIP-removebg-preview.png';
import esgMark from '@/assets/ESG-removebg-preview.png';
import butterflyImg from '@/assets/나비-removebg-preview.png';

// 인트로 애니메이션 상태
const showIntro = ref(false);
const introComplete = ref(false);
const showIntroLogo = ref(false);
const showIntroText = ref(false);
const showIntroSubtext = ref(false);

// 배경 음악 상태
const bgMusic = ref<HTMLAudioElement | null>(null);
const isMusicPlaying = ref(false);
const isMuted = ref(false);

// 나비 애니메이션 상태
const butterflyReturned = ref(false);

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const FOCUS_BORDER_COLOR = 'var(--color-primary-light)';
const FOCUS_BOX_SHADOW = '0 0 0 4px rgba(255,143,104,0.1)';
const ERROR_BORDER_COLOR = 'var(--color-error)';
const ERROR_BOX_SHADOW = '0 0 0 4px rgba(239,68,68,0.1)';
const DEFAULT_BORDER_COLOR = 'var(--color-border)';

const authStore = useAuthStore();
const router = useRouter();

const email = ref('');
const password = ref('');
const showEsg = ref(false);
const animationComplete = ref(false);

const isValidEmail = computed(() => {
  return EMAIL_REGEX.test(email.value);
});

const isFormValid = computed(() => {
  return email.value && password.value && isValidEmail.value;
});

// 세션당 1회만 인트로 표시
const INTRO_SHOWN_KEY = 'skip_intro_shown';

// 배경 음악 초기화
function initMusic() {
  bgMusic.value = new Audio('/회사의 노래.mp3');
  bgMusic.value.loop = true;
  bgMusic.value.volume = 0.3;
}

// 음소거 토글
function toggleMute() {
  if (!bgMusic.value) return;

  if (isMuted.value) {
    bgMusic.value.muted = false;
    isMuted.value = false;
  } else {
    bgMusic.value.muted = true;
    isMuted.value = true;
  }
}

// 음악 자동 재생 시도
function tryAutoPlay() {
  if (!bgMusic.value) return;

  bgMusic.value.play().then(() => {
    isMusicPlaying.value = true;
  }).catch(() => {
    // 자동 재생 실패 시 사용자 상호작용 대기
    const handleFirstInteraction = () => {
      if (bgMusic.value && !isMusicPlaying.value) {
        bgMusic.value.play().then(() => {
          isMusicPlaying.value = true;
        }).catch(err => {
          console.log('Music play failed:', err);
        });
      }
      document.removeEventListener('click', handleFirstInteraction);
      document.removeEventListener('keydown', handleFirstInteraction);
    };
    document.addEventListener('click', handleFirstInteraction);
    document.addEventListener('keydown', handleFirstInteraction);
  });
}

onMounted(() => {
  // 음악 초기화
  initMusic();

  const introShown = sessionStorage.getItem(INTRO_SHOWN_KEY);

  if (!introShown) {
    // 인트로 애니메이션 시작
    showIntro.value = true;
    sessionStorage.setItem(INTRO_SHOWN_KEY, 'true');

    // 음악 자동 재생 시도
    tryAutoPlay();

    // SK 로고 페이드인
    setTimeout(() => {
      showIntroLogo.value = true;
    }, 300);

    // "Imagine, AX" 텍스트 타이핑 효과
    setTimeout(() => {
      showIntroText.value = true;
    }, 800);

    // 서브텍스트 페이드인
    setTimeout(() => {
      showIntroSubtext.value = true;
    }, 1800);

    // 인트로 종료 및 로그인 화면 전환
    setTimeout(() => {
      introComplete.value = true;
    }, 4000);

    // 인트로 완전히 숨기기
    setTimeout(() => {
      showIntro.value = false;
      startLoginAnimations();
    }, 4800);
  } else {
    // 인트로 이미 봤으면 바로 로그인 화면
    introComplete.value = true;
    showIntro.value = false;
    startLoginAnimations();
    // 음악 자동 재생 시도
    tryAutoPlay();
  }
});

// 컴포넌트 언마운트 시 음악 정리
onUnmounted(() => {
  if (bgMusic.value) {
    bgMusic.value.pause();
    bgMusic.value = null;
  }
});

function startLoginAnimations() {
  // Start butterfly animation after a short delay
  setTimeout(() => {
    showEsg.value = true;
  }, 500);

  // Mark animation as complete after butterfly finishes drawing ESG
  setTimeout(() => {
    animationComplete.value = true;
  }, 3500);

  // Butterfly returns to SK logo after drawing
  setTimeout(() => {
    butterflyReturned.value = true;
  }, 4000);
}

async function handleLogin() {
  if (!isFormValid.value) return;

  const success = await authStore.login(email.value, password.value);
  if (success) {
    if (authStore.isFirstLogin) {
      router.push('/change-password');
    } else {
      router.push('/');
    }
  }
}

function handleEmailFocus(e: FocusEvent) {
  const target = e.target as HTMLInputElement;
  if (!email.value || isValidEmail.value) {
    target.style.borderColor = FOCUS_BORDER_COLOR;
    target.style.boxShadow = FOCUS_BOX_SHADOW;
  }
}

function handleEmailBlur(e: FocusEvent) {
  const target = e.target as HTMLInputElement;
  if (email.value && !isValidEmail.value) {
    target.style.borderColor = ERROR_BORDER_COLOR;
    target.style.boxShadow = ERROR_BOX_SHADOW;
  } else {
    target.style.borderColor = DEFAULT_BORDER_COLOR;
    target.style.boxShadow = 'none';
  }
}

function handlePasswordFocus(e: FocusEvent) {
  const target = e.target as HTMLInputElement;
  target.style.borderColor = FOCUS_BORDER_COLOR;
  target.style.boxShadow = FOCUS_BOX_SHADOW;
}

function handlePasswordBlur(e: FocusEvent) {
  const target = e.target as HTMLInputElement;
  target.style.borderColor = DEFAULT_BORDER_COLOR;
  target.style.boxShadow = 'none';
}
</script>

<template>
  <!-- Intro Animation Screen -->
  <Transition name="intro-fade">
    <div v-if="showIntro" class="intro-screen">
      <!-- Abstract Background Effect -->
      <div class="intro-bg">
        <div class="intro-gradient" />
        <div class="intro-wave wave-1" />
        <div class="intro-wave wave-2" />
        <div class="intro-wave wave-3" />
      </div>

      <!-- Content -->
      <div class="intro-content">
        <!-- SK Logo -->
        <div class="intro-logo" :class="{ 'show': showIntroLogo }">
          <img :src="skAxLogo" alt="SK 주식회사 AX" />
        </div>

        <!-- Main Text: Imagine, AX -->
        <div class="intro-main-text" :class="{ 'show': showIntroText }">
          <span class="imagine">Imagine,</span>
          <span class="ax">AX</span>
        </div>

        <!-- Subtext -->
        <div class="intro-subtext" :class="{ 'show': showIntroSubtext }">
          Global Top 10 AX Service Company
        </div>
      </div>

      <!-- Mute Button on Intro -->
      <button class="mute-toggle intro-mute" @click="toggleMute" :title="isMuted ? '소리 켜기' : '음소거'">
        <Volume2 v-if="!isMuted" class="mute-toggle-icon" />
        <VolumeX v-else class="mute-toggle-icon" />
      </button>
    </div>
  </Transition>

  <!-- Login Screen -->
  <Transition name="login-fade">
    <div v-show="introComplete" class="login-container">
      <!-- Mute Toggle Button -->
      <button class="mute-toggle" @click="toggleMute" :title="isMuted ? '소리 켜기' : '음소거'">
        <Volume2 v-if="!isMuted" class="mute-toggle-icon" />
        <VolumeX v-else class="mute-toggle-icon" />
      </button>

      <!-- Left Side - Visual Section -->
      <div class="login-visual">
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
          <!-- SKIP Logo -->
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

    <!-- Right Side - Login Form -->
    <div class="login-form-container">
      <div class="login-form-wrapper">
        <!-- Welcome Text -->
        <div class="welcome-section">
          <div class="welcome-title">환영합니다</div>
          <div class="welcome-subtitle">임직원 계정으로 로그인하세요</div>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin">
          <!-- Email Input -->
          <div class="input-group">
            <label class="input-label">이메일</label>
            <input
              v-model="email"
              type="email"
              placeholder="이메일을 입력하세요 (예: user@sk.com)"
              class="input-field"
              :class="{ 'input-error': email && !isValidEmail }"
              @focus="handleEmailFocus"
              @blur="handleEmailBlur"
            />
            <div v-if="email && !isValidEmail" class="error-message">
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
              :class="{ 'input-error': authStore.failedAttempts > 0 }"
              @focus="handlePasswordFocus"
              @blur="handlePasswordBlur"
            />
            <!-- Error Message with remaining attempts -->
            <div v-if="authStore.failedAttempts > 0" class="password-error-message">
              {{ authStore.remainingAttempts }}회 더 실패 시 계정이 잠금 처리됩니다
            </div>
          </div>

          <!-- Login Button -->
          <button
            type="submit"
            :disabled="!isFormValid || authStore.isLoading"
            class="login-button"
            :class="{ 'login-button-active': isFormValid }"
          >
            <template v-if="authStore.isLoading">
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
  </Transition>
</template>

<style scoped>
/* ========== Intro Screen Styles ========== */
.intro-screen {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0a0a;
  overflow: hidden;
}

.intro-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.intro-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 50% at 50% 50%, rgba(30, 30, 80, 0.4) 0%, transparent 50%),
              radial-gradient(ellipse 60% 40% at 70% 60%, rgba(60, 20, 80, 0.3) 0%, transparent 50%),
              linear-gradient(180deg, #0a0a0a 0%, #0f0f1a 50%, #0a0a0a 100%);
}

/* Abstract Wave Animation */
.intro-wave {
  position: absolute;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg,
    transparent 30%,
    rgba(100, 80, 200, 0.08) 35%,
    rgba(80, 60, 180, 0.15) 50%,
    rgba(100, 80, 200, 0.08) 65%,
    transparent 70%);
  animation: waveMove 8s ease-in-out infinite;
}

.wave-1 {
  top: -50%;
  left: -50%;
  animation-delay: 0s;
}

.wave-2 {
  top: -50%;
  left: -30%;
  background: linear-gradient(135deg,
    transparent 30%,
    rgba(60, 40, 140, 0.1) 35%,
    rgba(40, 20, 120, 0.18) 50%,
    rgba(60, 40, 140, 0.1) 65%,
    transparent 70%);
  animation-delay: -2s;
  animation-duration: 10s;
}

.wave-3 {
  top: -30%;
  left: -70%;
  background: linear-gradient(90deg,
    transparent 40%,
    rgba(80, 60, 160, 0.06) 45%,
    rgba(60, 40, 140, 0.12) 50%,
    rgba(80, 60, 160, 0.06) 55%,
    transparent 60%);
  animation-delay: -4s;
  animation-duration: 12s;
}

@keyframes waveMove {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(5%, 3%) rotate(2deg);
  }
  50% {
    transform: translate(10%, 0%) rotate(0deg);
  }
  75% {
    transform: translate(5%, -3%) rotate(-2deg);
  }
}

.intro-content {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* Intro Logo */
.intro-logo {
  opacity: 0;
  transform: translateY(-30px) scale(0.9);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1);
  margin-bottom: 60px;
}

.intro-logo.show {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.intro-logo img {
  height: 60px;
  width: auto;
  filter: drop-shadow(0 0 30px rgba(255, 100, 50, 0.3));
}

/* Main Text: Imagine, AX */
.intro-main-text {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 32px;
  opacity: 0;
  transform: translateY(40px);
  transition: all 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.intro-main-text.show {
  opacity: 1;
  transform: translateY(0);
}

.intro-main-text .imagine {
  font-size: 72px;
  font-weight: 300;
  color: #ffffff;
  letter-spacing: -2px;
  text-shadow: 0 0 60px rgba(255, 255, 255, 0.3);
}

.intro-main-text .ax {
  font-size: 72px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -2px;
  text-shadow: 0 0 60px rgba(255, 255, 255, 0.3);
}

/* Subtext */
.intro-subtext {
  font-size: 20px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 4px;
  text-transform: uppercase;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.intro-subtext.show {
  opacity: 1;
  transform: translateY(0);
}

/* Transition Animations */
.intro-fade-enter-active,
.intro-fade-leave-active {
  transition: opacity 0.8s ease;
}

.intro-fade-enter-from,
.intro-fade-leave-to {
  opacity: 0;
}

.login-fade-enter-active {
  transition: opacity 0.6s ease 0.2s;
}

.login-fade-enter-from {
  opacity: 0;
}

/* ========== Login Screen Styles ========== */
.login-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  min-width: 1440px;
  min-height: 900px;
  position: relative;
  overflow: hidden;
}

/* Visual Section */
.login-visual {
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
.login-form-container {
  width: 40%;
  height: 100%;
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-form-wrapper {
  width: 100%;
  max-width: 480px;
  padding: 60px;
}

.welcome-section {
  margin-bottom: 48px;
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
  margin-bottom: 36px;
}

.input-label {
  display: block;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 10px;
}

.input-field {
  width: 100%;
  padding: 16px 18px;
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

.error-message {
  margin-top: 8px;
  font-size: 13px;
  color: var(--color-error);
  font-weight: var(--font-weight-medium);
}

.password-error-message {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-error);
  font-weight: var(--font-weight-medium);
}

.login-error-message {
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

.remaining-attempts {
  margin-top: 8px;
  font-size: 13px;
  color: var(--color-warning);
  font-weight: var(--font-weight-medium);
}

.security-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  background: rgba(255, 193, 7, 0.1);
  border-radius: var(--radius-md);
  color: var(--color-warning);
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  margin-bottom: 20px;
}

.warning-icon {
  font-size: 14px;
}

.login-button {
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

.login-button-active {
  background: var(--gradient-primary);
  cursor: pointer;
  box-shadow: var(--shadow-primary);
}

.login-button-active:hover {
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

/* ========== Mute Controls ========== */
.mute-toggle {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.mute-toggle:hover {
  background: rgba(0, 0, 0, 0.5);
  transform: scale(1.05);
}

.mute-toggle-icon {
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.8);
}

/* Intro screen mute button */
.intro-mute {
  bottom: 40px;
  right: 40px;
}
</style>
