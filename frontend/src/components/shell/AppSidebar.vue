<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchCustomers, fetchOperatingView } from '../../api/engagement'
import { fetchCommitments } from '../../api/v11'
import { SHELL_NAV_GROUPS, navDomainForPath, type ShellNavItem } from '../../layouts/navConfig'
import { useWorkspaceTabsStore } from '../../stores/workspaceTabs'

const router = useRouter()
const route = useRoute()
const tabs = useWorkspaceTabsStore()

const commitmentCount = ref(0)

const activeDomain = computed(() => navDomainForPath(route.path))

onMounted(async () => {
  try {
    const list = await fetchCommitments({})
    commitmentCount.value = Array.isArray(list) ? list.length : 0
  } catch {
    commitmentCount.value = 0
  }
})

function badgeFor(item: ShellNavItem): number | null {
  if (item.domain === 'commitments' && commitmentCount.value > 0) {
    return commitmentCount.value
  }
  return null
}

function panoramaTarget(): string {
  const fromTab = [...tabs.tabs].reverse().find(tab => tab.path.startsWith('/customers/'))
  if (fromTab) {
    const match = fromTab.path.match(/^\/customers\/([^/]+)/)
    if (match?.[1]) {
      return `/customers/${match[1]}/group`
    }
  }
  return '/accounts'
}

async function firstPanoramaCustomerId(): Promise<string | null> {
  const customers = await fetchCustomers()
  if (!customers.length) {
    return null
  }
  const inspected = await Promise.all(
    customers.slice(0, 12).map(async customer => {
      try {
        const view = await fetchOperatingView(customer.customerId)
        return { id: customer.customerId, members: view.entities.length }
      } catch {
        return { id: customer.customerId, members: 0 }
      }
    }),
  )
  return inspected.find(row => row.members > 0)?.id ?? customers[0].customerId
}

async function openItem(item: ShellNavItem) {
  if (item.domain === 'panorama') {
    const fromTab = panoramaTarget()
    if (fromTab.startsWith('/customers/')) {
      await router.push(fromTab)
      return
    }
    try {
      const id = await firstPanoramaCustomerId()
      if (id) {
        await router.push({ name: 'CustomerGroupView', params: { id } })
        return
      }
    } catch {
      /* fall through to 客户组合 */
    }
  }
  await router.push(item.to)
}

function goHome() {
  router.push('/workbench')
}
</script>

<template>
  <nav class="shell-sidebar" data-testid="shell-sidebar" aria-label="GITS Bank 主导航">
    <button type="button" class="brand" data-testid="shell-brand" @click="goHome">
      <span class="brand-mark">G</span>
      <span class="brand-copy">
        <span class="brand-name">GITS Bank</span>
        <span class="brand-sub">对公客户经营工作台</span>
      </span>
    </button>

    <div
      v-for="group in SHELL_NAV_GROUPS"
      :key="group.key"
      class="nav-group"
      :data-testid="`nav-group-${group.key}`"
    >
      <p class="nav-group-label">{{ group.label }}</p>
      <button
        v-for="item in group.children"
        :key="item.key"
        type="button"
        class="nav-item"
        :class="{ active: activeDomain === item.domain }"
        :data-testid="`nav-item-${item.key}`"
        :aria-label="item.label"
        :aria-current="activeDomain === item.domain ? 'page' : undefined"
        @click="openItem(item)"
      >
        <span class="nav-icon" aria-hidden="true">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
        <span v-if="badgeFor(item) != null" class="nav-badge" data-testid="nav-badge">{{ badgeFor(item) }}</span>
      </button>
    </div>

    <div class="nav-user" data-testid="shell-nav-user">
      <span class="nav-avatar" aria-hidden="true">开</span>
      <span class="nav-user-copy">
        <span class="nav-user-name">开发会话</span>
        <span class="nav-user-role">对公客户经理 · 在线</span>
      </span>
    </div>
  </nav>
</template>

<style scoped>
.shell-sidebar {
  height: 100%;
  min-height: 100vh;
  background: var(--gits-navy-900);
  color: #d8e3f0;
  display: flex;
  flex-direction: column;
  padding: 0 0 16px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  height: 62px;
  padding: 0 16px;
  border: 0;
  background: var(--gits-navy-800);
  cursor: pointer;
  text-align: left;
}
.brand-mark {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: var(--gits-blue-600);
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.brand-copy {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}
.brand-name {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}
.brand-sub {
  font-size: 9px;
  color: #b8cbe0;
}
.nav-group {
  padding: 10px 8px 4px;
}
.nav-group-label {
  margin: 0 10px 8px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #8299b7;
}
.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  height: 36px;
  margin-bottom: 4px;
  padding: 0 12px 0 16px;
  border: 0;
  border-radius: 5px;
  background: transparent;
  color: #d8e3f0;
  cursor: pointer;
  text-align: left;
  font-size: 11px;
  overflow: hidden;
}
.nav-item:hover {
  background: rgba(18, 62, 114, 0.55);
  color: #fff;
}
.nav-item.active {
  background: #123e72;
  color: #fff;
  font-weight: 600;
}
.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: 2px 0 0 2px;
  background: #48a7e8;
}
.nav-icon {
  width: 16px;
  text-align: center;
  color: #9fb2c9;
}
.nav-item.active .nav-icon {
  color: #fff;
}
.nav-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.nav-badge {
  min-width: 20px;
  height: 18px;
  padding: 0 6px;
  border-radius: 9px;
  background: var(--gits-amber-400);
  color: var(--gits-amber-800);
  font-size: 10px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.nav-user {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px 4px;
  border-top: 1px solid #284767;
}
.nav-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 2px solid var(--gits-teal-500);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #fff;
}
.nav-user-copy {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.nav-user-name {
  font-size: 10px;
  color: #fff;
  font-weight: 600;
}
.nav-user-role {
  font-size: 8px;
  color: #9fb2c9;
}
</style>
