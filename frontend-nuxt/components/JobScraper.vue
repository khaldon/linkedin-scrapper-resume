<template>
  <div class="card">
    <div class="card-icon">
      <i class="fas fa-search"></i>
    </div>
    <h2>Scrape LinkedIn Job</h2>
    <p>Enter a LinkedIn job posting URL to extract job details and save them to your database.</p>

    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label class="form-label" for="job-url">
          <i class="fas fa-link"></i> LinkedIn Job URL
        </label>
        <input
          id="job-url"
          v-model="jobUrl"
          type="url"
          class="form-input"
          placeholder="https://www.linkedin.com/jobs/view/..."
          required
        />
        <div v-if="urlError" class="alert alert-error" style="margin-top: 0.5rem;">
          <i class="fas fa-exclamation-circle"></i>
          {{ urlError }}
        </div>
      </div>

      <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
        <i class="fas fa-search"></i>
        {{ loading ? 'Scraping...' : 'Scrape Job' }}
      </button>
    </form>

    <!-- Alert -->
    <div v-if="alert.message" :class="`alert alert-${alert.type}`" style="margin-top: 1.5rem;">
      <i :class="`fas fa-${alert.type === 'success' ? 'check-circle' : 'exclamation-circle'}`"></i>
      {{ alert.message }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="spinner"></div>

    <!-- Result -->
    <div v-if="result" style="margin-top: 2rem; padding: 1.5rem; background: var(--light); border-radius: var(--radius);">
      <h3 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
        <i class="fas fa-briefcase"></i> {{ result.title }}
      </h3>
      <p><strong><i class="fas fa-building"></i> Company:</strong> {{ result.company }}</p>
      <p><strong><i class="fas fa-user"></i> Posted by:</strong> {{ result.poster }}</p>
      
      <div style="margin-top: 1.5rem;">
        <h4 style="margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
          <i class="fas fa-file-alt"></i> Job Description
        </h4>
        <div style="
          background: white; 
          padding: 1.25rem; 
          border-radius: var(--radius); 
          border-left: 4px solid var(--primary);
          max-height: 400px;
          overflow-y: auto;
          white-space: pre-wrap;
          word-wrap: break-word;
          line-height: 1.6;
          color: var(--dark);
        ">
          {{ result.full_description || result.description }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { apiCall } = useApi()
const { validateUrl, validateRequired } = useValidation()

const jobUrl = ref('')
const urlError = ref('')
const loading = ref(false)
const alert = ref({ type: '', message: '' })
const result = ref(null)

const handleSubmit = async () => {
  // Reset states
  urlError.value = ''
  alert.value = { type: '', message: '' }
  result.value = null

  // Validate URL
  const urlValidation = validateRequired(jobUrl.value) || validateUrl(jobUrl.value)
  if (urlValidation) {
    urlError.value = urlValidation
    return
  }

  loading.value = true

  try {
    const data = await apiCall('/api/scrape', {
      method: 'POST',
      body: JSON.stringify({ url: jobUrl.value })
    })

    alert.value = { type: 'success', message: 'Job scraped successfully!' }
    result.value = data
    jobUrl.value = ''
  } catch (error) {
    alert.value = { type: 'error', message: error.message || 'Failed to scrape job' }
  } finally {
    loading.value = false
  }
}
</script>
