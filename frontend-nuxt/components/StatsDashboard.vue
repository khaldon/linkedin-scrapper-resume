<template>
  <div class="card">
    <div class="card-icon">
      <i class="fas fa-chart-line"></i>
    </div>
    <h2>Job Market Statistics</h2>
    <p>Analyze job market trends, top technologies, and in-demand skills from your scraped jobs.</p>

    <button @click="generateStats" class="btn btn-primary btn-block" :disabled="loading">
      <i class="fas fa-sync-alt"></i>
      {{ loading ? 'Generating...' : 'Generate Fresh Stats' }}
    </button>

    <!-- Alert -->
    <div v-if="alert.message" :class="`alert alert-${alert.type}`" style="margin-top: 1.5rem;">
      <i :class="`fas fa-${alert.type === 'success' ? 'check-circle' : 'exclamation-circle'}`"></i>
      {{ alert.message }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="spinner"></div>

    <!-- Stats Content -->
    <div v-if="stats" style="margin-top: 2rem;">
      <!-- Summary Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ stats.total_jobs }}</div>
          <div class="stat-label">Total Jobs Analyzed</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.technologies?.length || 0 }}</div>
          <div class="stat-label">Top Technologies</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.languages?.length || 0 }}</div>
          <div class="stat-label">Languages Found</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ (stats.soft_skills?.length || 0) + (stats.hard_skills?.length || 0) }}</div>
          <div class="stat-label">Skills Identified</div>
        </div>
      </div>

      <!-- AI Market Analysis -->
      <div v-if="stats.market_summary && stats.market_summary !== 'Market insights currently unavailable.'" 
           class="chart-container" 
           style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
        <h3 style="color: white; display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
          <i class="fas fa-robot" style="font-size: 1.5rem;"></i>
          <span>AI Market Analysis</span>
        </h3>
        <div style="display: grid; gap: 1rem;">
          <div v-for="(paragraph, i) in formatMarketSummary(stats.market_summary)" :key="i"
               style="background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(10px); padding: 1.25rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.2); line-height: 1.7;">
            <div style="display: flex; align-items: start; gap: 0.75rem;">
              <i class="fas fa-lightbulb" style="color: #ffd700; margin-top: 0.25rem; font-size: 1.1rem;"></i>
              <p style="margin: 0; color: rgba(255, 255, 255, 0.95);" v-html="formatMarkdown(paragraph)"></p>
            </div>
          </div>
        </div>
      </div>

      <!-- Technologies Chart -->
      <div v-if="stats.technologies?.length" class="chart-container">
        <h3><i class="fas fa-laptop-code"></i> Top Technologies</h3>
        <div v-for="(item, index) in stats.technologies.slice(0, 10)" :key="index" style="margin-bottom: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; color: var(--dark);">{{ item.name }}</span>
            <span style="font-weight: 700; color: #6366f1;">{{ item.count }} job{{ item.count !== 1 ? 's' : '' }}</span>
          </div>
          <div style="background: #e2e8f0; border-radius: 8px; height: 32px; overflow: hidden;">
            <div :style="`width: ${item.percentage}%; background: linear-gradient(90deg, #6366f1, #8b5cf6); height: 100%; display: flex; align-items: center; padding: 0 1rem; color: white; font-weight: 600; font-size: 0.9rem; transition: width 1s ease-out;`">
              {{ item.percentage }}%
            </div>
          </div>
        </div>
      </div>

      <!-- Languages Chart -->
      <div v-if="stats.languages?.length" class="chart-container">
        <h3><i class="fas fa-code"></i> Programming Languages</h3>
        <div v-for="(item, index) in stats.languages.slice(0, 10)" :key="index" style="margin-bottom: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; color: var(--dark);">{{ item.name }}</span>
            <span style="font-weight: 700; color: #10b981;">{{ item.count }} job{{ item.count !== 1 ? 's' : '' }}</span>
          </div>
          <div style="background: #e2e8f0; border-radius: 8px; height: 32px; overflow: hidden;">
            <div :style="`width: ${item.percentage}%; background: linear-gradient(90deg, #10b981, #34d399); height: 100%; display: flex; align-items: center; padding: 0 1rem; color: white; font-weight: 600; font-size: 0.9rem; transition: width 1s ease-out;`">
              {{ item.percentage }}%
            </div>
          </div>
        </div>
      </div>

      <!-- Soft Skills Chart -->
      <div v-if="stats.soft_skills?.length" class="chart-container">
        <h3><i class="fas fa-users"></i> Top Soft Skills</h3>
        <div v-for="(item, index) in stats.soft_skills.slice(0, 10)" :key="index" style="margin-bottom: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; color: var(--dark);">{{ item.name }}</span>
            <span style="font-weight: 700; color: #f59e0b;">{{ item.count }} job{{ item.count !== 1 ? 's' : '' }}</span>
          </div>
          <div style="background: #e2e8f0; border-radius: 8px; height: 32px; overflow: hidden;">
            <div :style="`width: ${item.percentage}%; background: linear-gradient(90deg, #f59e0b, #fbbf24); height: 100%; display: flex; align-items: center; padding: 0 1rem; color: white; font-weight: 600; font-size: 0.9rem; transition: width 1s ease-out;`">
              {{ item.percentage }}%
            </div>
          </div>
        </div>
      </div>

      <!-- Hard Skills Chart -->
      <div v-if="stats.hard_skills?.length" class="chart-container">
        <h3><i class="fas fa-tools"></i> Top Hard Skills</h3>
        <div v-for="(item, index) in stats.hard_skills.slice(0, 10)" :key="index" style="margin-bottom: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; color: var(--dark);">{{ item.name }}</span>
            <span style="font-weight: 700; color: #ec4899;">{{ item.count }} job{{ item.count !== 1 ? 's' : '' }}</span>
          </div>
          <div style="background: #e2e8f0; border-radius: 8px; height: 32px; overflow: hidden;">
            <div :style="`width: ${item.percentage}%; background: linear-gradient(90deg, #ec4899, #f472b6); height: 100%; display: flex; align-items: center; padding: 0 1rem; color: white; font-weight: 600; font-size: 0.9rem; transition: width 1s ease-out;`">
              {{ item.percentage }}%
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { apiCall } = useApi()

const loading = ref(false)
const alert = ref({ type: '', message: '' })
const stats = ref(null)

// Load stats on mount
onMounted(async () => {
  try {
    stats.value = await apiCall('/api/stats')
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
})

const generateStats = async () => {
  loading.value = true
  alert.value = { type: '', message: '' }

  try {
    const data = await apiCall('/api/stats/generate', { method: 'POST' })
    stats.value = data.stats
    alert.value = { type: 'success', message: 'Statistics generated successfully!' }
  } catch (error) {
    alert.value = { type: 'error', message: error.message || 'Failed to generate stats' }
  } finally {
    loading.value = false
  }
}

const formatMarketSummary = (summary) => {
  return summary.split('\n\n').filter(p => p.trim())
}

const formatMarkdown = (text) => {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong style="color: #ffd700; background: rgba(255, 215, 0, 0.15); padding: 2px 6px; border-radius: 4px;">$1</strong>')
    .replace(/__(.+?)__/g, '<strong style="color: #ffd700; background: rgba(255, 215, 0, 0.15); padding: 2px 6px; border-radius: 4px;">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code style="background: rgba(0,0,0,0.1); padding: 2px 6px; border-radius: 4px; font-family: monospace;">$1</code>')
    .replace(/\n/g, '<br>')
}
</script>
