<script setup lang="ts">
import { computed } from 'vue';
import { Plus, MessageSquare, Trash2 } from 'lucide-vue-next';
import { useChatStore } from '@/stores';

// Store
const chatStore = useChatStore();

// Computed
const sortedSessions = computed(() =>
  [...chatStore.sessions].sort((a, b) => b.lastUpdated - a.lastUpdated)
);

// Methods
function formatDate(timestamp: number) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return '오늘';
  } else if (diffDays === 1) {
    return '어제';
  } else if (diffDays < 7) {
    return `${diffDays}일 전`;
  } else {
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  }
}

function isActiveSession(sessionId: string) {
  return chatStore.currentSessionId === sessionId;
}
</script>

<template>
  <div class="chat-history-sidebar">
    <!-- Header -->
    <div class="sidebar-header">
      <div class="header-title">
        <MessageSquare class="w-5 h-5" />
        <span>채팅 기록</span>
      </div>
      <button class="new-chat-button" @click="chatStore.createNewSession">
        <Plus :size="18" :stroke-width="2.5" />
      </button>
    </div>

    <!-- Session List -->
    <div class="session-list">
      <div
        v-for="session in sortedSessions"
        :key="session.id"
        class="session-item"
        :class="{ 'session-item-active': isActiveSession(session.id) }"
        @click="chatStore.loadSession(session.id)"
      >
        <div class="session-content">
          <div class="session-title">{{ session.title }}</div>
          <div class="session-date">{{ formatDate(session.lastUpdated) }}</div>
        </div>
        <button
          class="delete-button"
          @click.stop="chatStore.deleteSession(session.id)"
        >
          <Trash2 :size="14" />
        </button>
      </div>

      <div v-if="sortedSessions.length === 0" class="empty-state">
        <MessageSquare class="w-8 h-8 text-muted" />
        <p>채팅 기록이 없습니다</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-history-sidebar {
  position: fixed;
  right: 0;
  top: 0;
  width: 320px;
  height: 100%;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  z-index: var(--z-fixed);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.header-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.new-chat-button {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: var(--color-background);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  transition: all var(--transition-normal);
}

.new-chat-button:hover {
  background: var(--color-border);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  margin-bottom: var(--spacing-sm);
}

.session-item:hover {
  background: var(--color-background);
}

.session-item-active {
  background: var(--color-background);
  border: 1px solid var(--color-primary-light);
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.session-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.delete-button {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  opacity: 0;
  transition: all var(--transition-normal);
}

.session-item:hover .delete-button {
  opacity: 1;
}

.delete-button:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  padding: var(--spacing-2xl);
  color: var(--color-text-muted);
  text-align: center;
}

.text-muted {
  color: var(--color-text-muted);
}
</style>
