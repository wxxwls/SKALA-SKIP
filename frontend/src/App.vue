<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores';
import DefaultLayout from '@/layouts/DefaultLayout.vue';

// Store & Route
const authStore = useAuthStore();
const route = useRoute();

// Computed
const hideLayout = computed(() =>
  route.name === 'Login' || route.name === 'ChangePassword'
);

// Lifecycle
onMounted(() => {
  authStore.checkAuth();
});
</script>

<template>
  <RouterView v-if="hideLayout" />
  <DefaultLayout v-else>
    <RouterView />
  </DefaultLayout>
</template>

<style>
/* Global styles are imported in main.ts */
</style>
