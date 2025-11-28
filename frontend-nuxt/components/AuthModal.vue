<template>
  <div class="modal" :class="{ active: isOpen }">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Welcome Back</h2>
        <button class="modal-close" @click="close">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="oauth-buttons">
        <button class="btn btn-google btn-block" @click="handleGoogleLogin">
          <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" style="width: 24px; height: 24px; margin-right: 1rem;">
          Sign in with Google
        </button>
      </div>

      <div v-if="error" class="alert alert-error" style="margin-top: 1rem;">
        <i class="fas fa-exclamation-circle"></i>
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])
const authStore = useAuthStore()
const error = ref(null)

const close = () => {
  emit('close')
  error.value = null
}

const handleGoogleLogin = async () => {
  try {
    error.value = null
    await authStore.loginWithGoogle()
    close()
  } catch (e) {
    error.value = e.message
  }
}
</script>
