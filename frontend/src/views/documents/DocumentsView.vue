<template>
  <div
    class="w-full h-full flex flex-col"
    :style="{
      background: '#F7F8FA'
    }"
  >
    <!-- Main Content -->
    <div class="flex-1 overflow-hidden">
      <DocumentList />
    </div>
  </div>
</template>

<script setup lang="ts">
import DocumentList from '@/components/issuepool/DocumentList.vue'
</script>
