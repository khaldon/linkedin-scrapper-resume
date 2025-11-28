<template>
  <div class="card">
    <div class="card-icon">
      <i class="fas fa-file-alt"></i>
    </div>
    <h2>Generate Tailored CV</h2>
    <p>Upload your CV and select a job to generate an ATS-optimized, tailored resume.</p>

    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label class="form-label" for="job-select">
          <i class="fas fa-briefcase"></i> Select Job
        </label>
        <select id="job-select" v-model="selectedJobId" class="form-select" required>
          <option value="">Select a job...</option>
          <option v-for="job in jobs" :key="job.id" :value="job.id">
            {{ job.title }} - {{ job.company }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label" for="cv-file">
          <i class="fas fa-upload"></i> Upload Your CV (PDF or Markdown)
        </label>
        <div class="file-input-wrapper">
          <input
            id="cv-file"
            ref="fileInput"
            type="file"
            accept=".pdf,.md,.txt"
            @change="handleFileChange"
            required
          />
          <label for="cv-file" class="file-input-label">
            <i class="fas fa-cloud-upload-alt"></i>
            <span>{{ fileName || 'Click to upload or drag and drop' }}</span>
          </label>
        </div>
        <div v-if="fileError" class="alert alert-error" style="margin-top: 0.5rem;">
          <i class="fas fa-exclamation-circle"></i>
          {{ fileError }}
        </div>
      </div>

      <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
        <i class="fas fa-magic"></i>
        {{ loading ? 'Generating...' : 'Generate Tailored CV' }}
      </button>
    </form>

    <!-- Alert -->
    <div v-if="alert.message" :class="`alert alert-${alert.type}`" style="margin-top: 1.5rem;">
      <i :class="`fas fa-${alert.type === 'success' ? 'check-circle' : 'exclamation-circle'}`"></i>
      {{ alert.message }}
    </div>

    <!-- Progress Bar -->
    <div v-if="uploadProgress > 0" style="margin-top: 1.5rem;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">{{ uploadProgress === 100 ? 'Processing...' : 'Uploading...' }}</span>
        <span style="font-weight: 700; color: var(--primary);">{{ uploadProgress }}%</span>
      </div>
      <div style="background: #e2e8f0; border-radius: 8px; height: 32px; overflow: hidden;">
        <div
          :style="`width: ${uploadProgress}%; background: linear-gradient(90deg, var(--primary), var(--secondary)); height: 100%; transition: width 0.3s;`"
        ></div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading && uploadProgress === 0" class="spinner"></div>

    <!-- Result -->
    <div v-if="result" style="margin-top: 2rem; padding: 1.5rem; background: var(--light); border-radius: var(--radius);">
      <h3 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
        <i class="fas fa-file-alt"></i> Your Tailored CV is Ready!
      </h3>
      <div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
        <a :href="`${apiBase}${result.cv_markdown}`" class="btn btn-secondary" download>
          <i class="fas fa-file-code"></i> Download Markdown
        </a>
        <a :href="`${apiBase}${result.cv_pdf}`" class="btn btn-primary" download>
          <i class="fas fa-file-pdf"></i> Download PDF
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
const { apiCall, apiBase, getAuthHeaders } = useApi()
const { validateFile } = useValidation()
const authStore = useAuthStore()

const selectedJobId = ref('')
const fileName = ref('')
const fileInput = ref(null)
const fileError = ref('')
const loading = ref(false)
const uploadProgress = ref(0)
const alert = ref({ type: '', message: '' })
const result = ref(null)
const jobs = ref([])

// Load jobs on mount
onMounted(async () => {
  try {
    const data = await apiCall('/api/jobs?limit=50')
    jobs.value = data.jobs
  } catch (error) {
    console.error('Failed to load jobs:', error)
  }
})

const handleFileChange = (event) => {
  const target = event.target
  const file = target.files?.[0]
  
  if (file) {
    fileName.value = file.name
    fileError.value = ''
    
    // Validate file
    const validation = validateFile(file, 5, ['application/pdf', 'text/markdown', 'text/plain'])
    if (validation) {
      fileError.value = validation
    }
  }
}

const handleSubmit = async () => {
  // Reset states
  fileError.value = ''
  alert.value = { type: '', message: '' }
  result.value = null
  uploadProgress.value = 0

  // Check auth
  if (!authStore.user) {
    alert.value = { type: 'error', message: 'Please login to generate a CV' }
    return
  }

  // Validate
  if (!selectedJobId.value) {
    alert.value = { type: 'error', message: 'Please select a job from the list' }
    return
  }

  const file = fileInput.value?.files?.[0]
  if (!file) {
    alert.value = { type: 'error', message: 'Please upload a CV file' }
    return
  }

  const validation = validateFile(file, 5, ['application/pdf', 'text/markdown', 'text/plain'])
  if (validation) {
    fileError.value = validation
    return
  }

  loading.value = true

  try {
    const formData = new FormData()
    formData.append('job_id', selectedJobId.value)
    formData.append('cv_file', file)

    const headers = await getAuthHeaders()
    delete headers['Content-Type'] // Let browser set it for FormData

    // Use XMLHttpRequest for progress tracking
    const data = await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          uploadProgress.value = Math.round((e.loaded / e.total) * 100)
        }
      })

      xhr.open('POST', `${apiBase}/api/generate-cv`)
      
      // Set auth header
      if (headers['Authorization']) {
        xhr.setRequestHeader('Authorization', headers['Authorization'])
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            resolve(JSON.parse(xhr.responseText))
          } catch (e) {
            reject(new Error('Invalid JSON response'))
          }
        } else {
          try {
            const errorData = JSON.parse(xhr.responseText)
            reject(new Error(errorData.detail || xhr.statusText))
          } catch (e) {
            reject(new Error(xhr.statusText))
          }
        }
      }

      xhr.onerror = () => reject(new Error('Network request failed'))
      xhr.send(formData)
    })

    alert.value = { type: 'success', message: 'CV generated successfully!' }
    result.value = data
    
    // Reset form
    selectedJobId.value = ''
    fileName.value = ''
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } catch (error) {
    alert.value = { type: 'error', message: error.message || 'Failed to generate CV' }
  } finally {
    loading.value = false
    uploadProgress.value = 0
  }
}
</script>
