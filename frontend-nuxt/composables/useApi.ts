export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const getAuthHeaders = async () => {
    const authStore = useAuthStore()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }

    if (authStore.user) {
      try {
        const { $auth } = useNuxtApp()
        const token = await $auth.currentUser?.getIdToken()
        if (token) {
          headers['Authorization'] = `Bearer ${token}`
        }
      } catch (error) {
        console.error('Failed to get auth token:', error)
      }
    }

    return headers
  }

  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    const headers = await getAuthHeaders()
    
    const response = await fetch(`${apiBase}${endpoint}`, {
      ...options,
      headers: {
        ...headers,
        ...options.headers
      }
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(error.detail || `API Error: ${response.status}`)
    }

    return response.json()
  }

  return {
    apiBase,
    apiCall,
    getAuthHeaders
  }
}
