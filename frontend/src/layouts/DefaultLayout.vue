<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import SidebarNav from '@/components/SidebarNav.vue';
import ChatHistorySidebar from '@/components/ChatHistorySidebar.vue';

// Route
const route = useRoute();

// Computed
const showChatHistory = computed(() => route.name === 'Chat');
</script>

<template>
  <div class="layout-container">
    <SidebarNav />
    <div class="layout-main">
      <slot />
    </div>
    <ChatHistorySidebar v-if="showChatHistory" />
  </div>
</template>

<style scoped>
.layout-container {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.layout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 0;
  transition: margin-left var(--transition-slow);
}

@media (min-width: 1280px) {
  .layout-main {
    margin-left: 54px;
  }
}
</style>
