<template>
  <div>
    <header class="header">
      <div class="header-content">
        <NuxtLink to="/" class="logo">
          <i class="fas fa-rocket"></i>
          <span>CareerBoost AI</span>
        </NuxtLink>

        <nav class="nav">
          <a href="#" class="nav-link" @click.prevent="switchTab('home')">
            <i class="fas fa-home"></i> Home
          </a>
          <a href="#" class="nav-link" @click.prevent="switchTab('stats')">
            <i class="fas fa-chart-line"></i> Market Stats
          </a>
          <a href="#" class="nav-link" @click.prevent="switchTab('generate')">
            <i class="fas fa-file-alt"></i> CV Tailor
          </a>
        </nav>

        <div class="user-menu">
          <div v-if="authStore.user" class="user-avatar-container" @click="toggleDropdown">
            <div class="user-avatar">
              <img v-if="authStore.user.photoURL" :src="authStore.user.photoURL" :alt="authStore.user.displayName" style="width: 100%; height: 100%; border-radius: 50%;">
              <span v-else>{{ (authStore.user.displayName || 'U')[0] }}</span>
            </div>
            
            <div v-if="showDropdown" class="user-dropdown">
              <div class="user-info">
                <div class="user-photo">
                   <img v-if="authStore.user.photoURL" :src="authStore.user.photoURL" :alt="authStore.user.displayName">
                   <span v-else>{{ (authStore.user.displayName || 'U')[0] }}</span>
                </div>
                <div class="user-details">
                  <div class="user-name">{{ authStore.user.displayName || 'User' }}</div>
                  <div class="user-email">{{ authStore.user.email }}</div>
                </div>
              </div>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item" @click="logout">
                <i class="fas fa-sign-out-alt"></i> Logout
              </button>
            </div>
          </div>

          <button v-else class="btn btn-secondary" @click="openAuthModal">
            <i class="fab fa-google"></i> Login
          </button>
        </div>
      </div>
    </header>

    <main>
      <slot />
    </main>

    <AuthModal :is-open="isAuthModalOpen" @close="closeAuthModal" />
  </div>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()
const { switchTab } = useTabNavigation()
const isAuthModalOpen = ref(false)
const showDropdown = ref(false)

onMounted(() => {
  authStore.initAuth()
})

const openAuthModal = () => {
  isAuthModalOpen.value = true
}

const closeAuthModal = () => {
  isAuthModalOpen.value = false
}

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const logout = async () => {
  await authStore.logout()
  showDropdown.value = false
}

// Close dropdown when clicking outside
onMounted(() => {
  document.addEventListener('click', (e) => {
    const container = document.querySelector('.user-avatar-container')
    if (container && !container.contains(e.target)) {
      showDropdown.value = false
    }
  })
})
</script>
