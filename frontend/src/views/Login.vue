<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NInput, NButton, NForm, NFormItem, useMessage } from 'naive-ui'
import { setApiKey } from '../api/auth'

const router = useRouter()
const msg = useMessage()

const apiKey = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!apiKey.value.trim()) {
    msg.warning('请输入 API Key')
    return
  }
  loading.value = true
  try {
    await setApiKey(apiKey.value.trim())
    router.push('/workbench')
  } catch (e: unknown) {
    msg.error('认证失败，请检查 API Key')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <!-- V8 对公经营书桌登录页 -->
    <div class="login-content">
      <div class="login-card">
        <!-- 品牌区：矿物深蓝底 -->
        <div class="login-brand-bar">
          <span class="login-brand-mark" aria-hidden="true">
            <svg width="26" height="26" viewBox="0 0 28 28" fill="none">
              <rect x="2" y="2" width="24" height="24" rx="6" fill="rgba(255,255,255,0.10)" />
              <path d="M8 18L14 9L20 18" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
              <line x1="10" y1="15.5" x2="18" y2="15.5" stroke="white" stroke-width="1.5" stroke-linecap="round" />
            </svg>
          </span>
          <div class="login-brand-text">
            <h1 class="login-brand-name">GITS Bank</h1>
            <p class="login-brand-sub">对公经营书桌</p>
          </div>
        </div>

        <div class="login-form-area">
          <p class="login-welcome">登录到您的账户</p>
          <NForm @submit.prevent="handleLogin">
            <NFormItem label="API Key">
              <NInput
                v-model:value="apiKey"
                type="password"
                show-password-on="click"
                placeholder="输入 X-API-KEY"
                :disabled="loading"
                @keyup.enter="handleLogin"
              />
            </NFormItem>
            <NButton
              type="primary"
              block
              :loading="loading"
              attr-type="submit"
            >
              登录
            </NButton>
          </NForm>

          <p class="login-hint">内网开发环境 · API Key 认证</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* V8 对公经营书桌登录页 */
.login-page {
  min-height: 100vh;
  display: flex;
  background: var(--v8-canvas);
  position: relative;
}

/* V8 装饰性背景纹理 — 极淡的对角线 */
.login-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(135deg, var(--v8-cream) 25%, transparent 25%),
    linear-gradient(225deg, var(--v8-cream) 25%, transparent 25%);
  background-size: 60px 60px;
  background-position: 0 0, 30px 0;
  opacity: 0.3;
  pointer-events: none;
}

.login-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  position: relative;
  z-index: 1;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: var(--v8-paper);
  border: 1px solid var(--v8-line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.login-brand-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 24px 32px;
  background: var(--v8-dark);
}

.login-brand-mark {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.10);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.login-brand-text {
  display: flex;
  flex-direction: column;
}

.login-brand-name {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  line-height: 1.1;
  margin: 0;
  letter-spacing: 0.04em;
}

.login-brand-sub {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 3px 0 0;
  letter-spacing: 0.06em;
}

.login-form-area {
  padding: 28px 32px 24px;
}

.login-welcome {
  font-size: 16px;
  font-weight: 600;
  color: var(--v8-ink);
  margin-bottom: 20px;
}

.login-hint {
  margin-top: 20px;
  font-size: 11px;
  color: var(--v8-faint);
  text-align: center;
  letter-spacing: 0.02em;
}

@media (max-width: 480px) {
  .login-content {
    padding: var(--space-4);
  }

  .login-card {
    max-width: 100%;
  }

  .login-brand-bar {
    padding: 20px 24px;
  }

  .login-form-area {
    padding: 24px 24px 20px;
  }
}
</style>
