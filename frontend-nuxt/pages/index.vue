<template>
  <div>
    <section class="hero">
      <h1>Master the Job Market</h1>
      <p>
        AI-powered insights and CV tailoring to help you land your dream job.
        Analyze trends, optimize your resume, and stand out.
      </p>
    </section>

    <div class="container">
      <!-- Tabs -->
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab', { active: activeTab === tab.id }]"
          @click="switchTab(tab.id)"
        >
          <i :class="tab.icon"></i> {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div v-show="activeTab === 'home'" class="tab-content active">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">150+</div>
            <div class="stat-label">Jobs Analyzed</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">85%</div>
            <div class="stat-label">Success Rate</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Real-time Updates</div>
          </div>
        </div>
      </div>

      <div v-show="activeTab === 'scrape'" class="tab-content">
        <JobScraper />
      </div>

      <div v-show="activeTab === 'generate'" class="tab-content">
        <CvGenerator />
      </div>

      <div v-show="activeTab === 'stats'" class="tab-content">
        <StatsDashboard />
      </div>

      <div v-show="activeTab === 'jobs'" class="tab-content">
        <div class="card">
          <div class="card-icon">
            <i class="fas fa-briefcase"></i>
          </div>
          <h2>Scraped Jobs</h2>
          <p>View all your scraped LinkedIn job postings.</p>
          <p style="text-align: center; color: var(--gray); padding: 2rem;">
            <i class="fas fa-info-circle"></i> Jobs list coming soon...
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  layout: 'default'
})

const { activeTab, switchTab } = useTabNavigation()

const tabs = [
  { id: 'home', label: 'Home', icon: 'fas fa-home' },
  { id: 'scrape', label: 'Scrape', icon: 'fas fa-search' },
  { id: 'generate', label: 'Generate CV', icon: 'fas fa-magic' },
  { id: 'stats', label: 'Stats', icon: 'fas fa-chart-line' },
  { id: 'jobs', label: 'Jobs', icon: 'fas fa-briefcase' }
]
</script>
