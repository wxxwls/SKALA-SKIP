<script setup lang="ts">
defineProps<{
  text: string;
}>();
</script>

<template>
  <div class="suggestion-card">
    <p>{{ text }}</p>
  </div>
</template>

<style scoped>
.suggestion-card {
  width: 360px;
  height: 92px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.04), 0px 8px 16px rgba(0, 0, 0, 0.03);
  padding: 18px 20px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.suggestion-card:hover {
  box-shadow: var(--shadow-lg);
}

.suggestion-card p {
  font-size: 13.5px;
  letter-spacing: -0.1px;
  color: #4a5568;
  line-height: 21px;
  word-break: keep-all;
}
</style>
