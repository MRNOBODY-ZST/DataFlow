<template>
  <AppLayout :title="t('settings.title')">
    <div class="py-6 px-4 sm:px-6">
      <div class="mx-auto">
        <div class="space-y-10">
          <!-- Profile Section -->
          <div class="border-b border-gray-200 pb-10 dark:border-white/10">
            <h2 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('settings.profile') }}</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('settings.accountInfo') }}</p>

            <div class="mt-6 space-y-4">
              <div class="sm:grid sm:grid-cols-3 sm:items-center sm:gap-4">
                <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('settings.username') }}</label>
                <div class="mt-1 sm:col-span-2 sm:mt-0">
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ auth.username || '—' }}</span>
                </div>
              </div>

              <div class="sm:grid sm:grid-cols-3 sm:items-center sm:gap-4">
                <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('settings.userId') }}</label>
                <div class="mt-1 sm:col-span-2 sm:mt-0">
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ auth.userId || '—' }}</span>
                </div>
              </div>

              <div class="sm:grid sm:grid-cols-3 sm:items-center sm:gap-4">
                <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('settings.createdAt') }}</label>
                <div class="mt-1 sm:col-span-2 sm:mt-0">
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ profileCreatedAt }}</span>
                </div>
              </div>

              <div class="sm:grid sm:grid-cols-3 sm:items-center sm:gap-4">
                <label for="email" class="block text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('settings.email') }}</label>
                <div class="mt-1 flex gap-3 sm:col-span-2 sm:mt-0">
                  <input
                    id="email"
                    v-model="profileEmail"
                    type="email"
                    class="block w-full rounded-md bg-white px-3 py-1.5 text-sm text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-sky-500"
                    :placeholder="t('settings.emailPlaceholder')"
                  />
                  <button
                    type="button"
                    class="shrink-0 rounded-md bg-sky-600 px-3 py-1.5 text-sm font-semibold text-white shadow-xs hover:bg-sky-500 disabled:opacity-60 dark:bg-sky-500 dark:hover:bg-sky-400"
                    :disabled="savingProfile"
                    @click="saveProfile"
                  >
                    {{ savingProfile ? t('common.saving') : t('common.save') }}
                  </button>
                </div>
              </div>
              <p v-if="profileMsg" class="text-sm" :class="profileError ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'">{{ profileMsg }}</p>
            </div>
          </div>

          <!-- Password Section -->
          <div class="border-b border-gray-200 pb-10 dark:border-white/10">
            <h2 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('settings.changePassword') }}</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('settings.passwordDesc') }}</p>

            <div class="mt-6 space-y-4">
              <div class="sm:grid sm:grid-cols-3 sm:items-center sm:gap-4">
                <label for="currentPassword" class="block text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('settings.currentPassword') }}</label>
                <div class="mt-1 sm:col-span-2 sm:mt-0">
                  <input
                    id="currentPassword"
                    v-model="passwordForm.current"
                    type="password"
                    autocomplete="current-password"
                    class="block w-full rounded-md bg-white px-3 py-1.5 text-sm text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-sky-500"
                  />
                </div>
              </div>

              <div class="sm:grid sm:grid-cols-3 sm:items-center sm:gap-4">
                <label for="newPassword" class="block text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('settings.newPassword') }}</label>
                <div class="mt-1 sm:col-span-2 sm:mt-0">
                  <input
                    id="newPassword"
                    v-model="passwordForm.newPwd"
                    type="password"
                    autocomplete="new-password"
                    class="block w-full rounded-md bg-white px-3 py-1.5 text-sm text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-sky-500"
                  />
                </div>
              </div>

              <div class="sm:grid sm:grid-cols-3 sm:items-center sm:gap-4">
                <label for="confirmPassword" class="block text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('settings.confirmPassword') }}</label>
                <div class="mt-1 sm:col-span-2 sm:mt-0">
                  <input
                    id="confirmPassword"
                    v-model="passwordForm.confirm"
                    type="password"
                    autocomplete="new-password"
                    class="block w-full rounded-md bg-white px-3 py-1.5 text-sm text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-sky-500"
                  />
                </div>
              </div>

              <div class="flex items-center gap-3">
                <button
                  type="button"
                  class="rounded-md bg-sky-600 px-3 py-1.5 text-sm font-semibold text-white shadow-xs hover:bg-sky-500 disabled:opacity-60 dark:bg-sky-500 dark:hover:bg-sky-400"
                  :disabled="changingPassword || !passwordForm.current || !passwordForm.newPwd || !passwordForm.confirm"
                  @click="changePassword"
                >
                  {{ changingPassword ? t('settings.updating') : t('settings.updatePassword') }}
                </button>
                <p v-if="passwordMsg" class="text-sm" :class="passwordError ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'">{{ passwordMsg }}</p>
              </div>
            </div>
          </div>

          <!-- Appearance Section -->
          <div class="border-b border-gray-200 pb-10 dark:border-white/10">
            <h2 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('settings.appearance') }}</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('settings.customizeApp') }}</p>

            <div class="mt-6">
              <fieldset>
                <legend class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('settings.theme') }}</legend>
                <div class="mt-4 space-y-3">
                  <div v-for="option in themeOptions" :key="option.value" class="flex items-center gap-3">
                    <div class="group grid size-4 grid-cols-1">
                      <input
                        :id="`theme-${option.value}`"
                        v-model="theme"
                        type="radio"
                        :value="option.value"
                        class="col-start-1 row-start-1 appearance-none rounded-full border border-gray-300 bg-white checked:border-sky-600 checked:bg-sky-600 dark:border-white/10 dark:bg-white/5 dark:checked:border-sky-500 dark:checked:bg-sky-500"
                        @change="applyTheme"
                      />
                    </div>
                    <label :for="`theme-${option.value}`" class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ option.label }}</label>
                  </div>
                </div>
              </fieldset>
            </div>

            <div class="mt-6">
              <fieldset>
                <legend class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('settings.language') }}</legend>
                <div class="mt-4 space-y-3">
                  <div v-for="option in languageOptions" :key="option.value" class="flex items-center gap-3">
                    <div class="group grid size-4 grid-cols-1">
                      <input
                        :id="`lang-${option.value}`"
                        v-model="currentLocale"
                        type="radio"
                        :value="option.value"
                        class="col-start-1 row-start-1 appearance-none rounded-full border border-gray-300 bg-white checked:border-sky-600 checked:bg-sky-600 dark:border-white/10 dark:bg-white/5 dark:checked:border-sky-500 dark:checked:bg-sky-500"
                        @change="applyLocale"
                      />
                    </div>
                    <label :for="`lang-${option.value}`" class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ option.label }}</label>
                  </div>
                </div>
              </fieldset>
            </div>
          </div>

          <!-- Danger Zone -->
          <div class="rounded-lg border border-red-200 p-6 dark:border-red-500/20">
            <h2 class="text-base font-semibold text-red-600 dark:text-red-400">{{ t('settings.dangerZone') }}</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('settings.irreversible') }}</p>
            <div class="mt-4">
              <button type="button" class="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-red-500 dark:bg-red-500 dark:hover:bg-red-400" @click="logout">{{ t('common.signOut') }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const { t, locale } = useI18n()
const router = useRouter()
const auth = useAuthStore()

const themeOptions = computed(() => [
  { label: t('settings.system'), value: 'system' },
  { label: t('settings.light'), value: 'light' },
  { label: t('settings.dark'), value: 'dark' },
])

const languageOptions = [
  { label: '中文', value: 'zh-CN' },
  { label: 'English', value: 'en' },
]

const theme = ref(localStorage.getItem('df_theme') || 'system')
const currentLocale = ref(locale.value)

// Profile
const profileEmail = ref('')
const profileCreatedAt = ref('—')
const savingProfile = ref(false)
const profileMsg = ref('')
const profileError = ref(false)

// Password
const passwordForm = reactive({ current: '', newPwd: '', confirm: '' })
const changingPassword = ref(false)
const passwordMsg = ref('')
const passwordError = ref(false)

onMounted(async () => {
  try {
    const { data } = await authApi.getProfile()
    profileEmail.value = data.email || ''
    profileCreatedAt.value = data.createdAt ? new Date(data.createdAt).toLocaleString() : '—'
  } catch {}
})

async function saveProfile() {
  savingProfile.value = true
  profileMsg.value = ''
  try {
    await authApi.updateProfile({ email: profileEmail.value })
    profileError.value = false
    profileMsg.value = t('settings.profileSaved')
  } catch (e: any) {
    profileError.value = true
    profileMsg.value = e.response?.data?.message || e.message || t('common.error')
  } finally {
    savingProfile.value = false
  }
}

async function changePassword() {
  passwordMsg.value = ''
  if (passwordForm.newPwd !== passwordForm.confirm) {
    passwordError.value = true
    passwordMsg.value = t('settings.passwordMismatch')
    return
  }
  if (passwordForm.newPwd.length < 6) {
    passwordError.value = true
    passwordMsg.value = t('settings.passwordTooShort')
    return
  }
  changingPassword.value = true
  try {
    await authApi.changePassword(passwordForm.current, passwordForm.newPwd)
    passwordError.value = false
    passwordMsg.value = t('settings.passwordChanged')
    passwordForm.current = ''
    passwordForm.newPwd = ''
    passwordForm.confirm = ''
  } catch (e: any) {
    passwordError.value = true
    passwordMsg.value = e.response?.data?.message || e.message || t('common.error')
  } finally {
    changingPassword.value = false
  }
}

function applyTheme() {
  localStorage.setItem('df_theme', theme.value)
  const html = document.documentElement
  if (theme.value === 'dark') {
    html.classList.add('dark')
  } else if (theme.value === 'light') {
    html.classList.remove('dark')
  } else {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }
}

function applyLocale() {
  locale.value = currentLocale.value
  localStorage.setItem('df_locale', currentLocale.value)
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
