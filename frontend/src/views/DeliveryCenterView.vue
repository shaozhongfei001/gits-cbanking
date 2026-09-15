<script setup lang="ts">
import GovDegradeShell from '../components/shell/GovDegradeShell.vue'
import { GOV_DEGRADE_PAGES } from '../composables/govDegrade'

const page = GOV_DEGRADE_PAGES.P33
</script>

<template>
  <GovDegradeShell v-bind="page" />
</template>
