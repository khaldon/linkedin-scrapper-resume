// Firebase Configuration
// Replace these with your Firebase project credentials
const firebaseConfig = {
    apiKey: "AIzaSyANDCAB8VI00JIVoRKLyXtc2FateShvn_c",
    authDomain: "linkedscrapper.firebaseapp.com",
    projectId: "linkedscrapper",
    storageBucket: "linkedscrapper.firebasestorage.app",
    messagingSenderId: "537959019488",
    appId: "1:537959019488:web:945b43c36a4bb6c198f185",
    measurementId: "G-HFP9095PCP"
};

// Initialize Firebase (will be loaded from CDN)
let auth = null;
let currentUser = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    // Wait for Firebase to load
    if (typeof firebase !== 'undefined') {
        firebase.initializeApp(firebaseConfig);
        auth = firebase.auth();

        // Handle redirect result (in case popup was blocked)
        try {
            const result = await auth.getRedirectResult();
            if (result.user) {
                console.log('Sign-in via redirect successful!');
                showAlert('auth-alert', 'success', 'Successfully signed in!');
                closeAuthModal();
            }
        } catch (error) {
            if (error.code === 'auth/unauthorized-domain') {
                console.error('DOMAIN ERROR:', error);
                console.log('Current URL:', window.location.href);
                console.log('Expected domain: localhost');
                alert('⚠️ IMPORTANT: You must access this site via http://localhost:8080 (not 127.0.0.1)');
            }
        }

        // Set up auth state listener
        auth.onAuthStateChanged(handleAuthStateChanged);
    } else {
        console.warn('Firebase not loaded. OAuth2 features will not work.');
        // Fall back to checking localStorage
        checkLocalAuth();
    }

    loadJobs();
});

// Handle authentication state changes
async function handleAuthStateChanged(user) {
    if (user) {
        // User is signed in
        currentUser = user;

        // Get ID token
        const idToken = await user.getIdToken();
        localStorage.setItem('firebaseToken', idToken);
        localStorage.setItem('currentUser', JSON.stringify({
            uid: user.uid,
            email: user.email,
            displayName: user.displayName,
            photoURL: user.photoURL
        }));

        updateUIForLoggedInUser(user);

        // Sync with backend
        await syncUserWithBackend(idToken);
    } else {
        // User is signed out
        currentUser = null;
        localStorage.removeItem('firebaseToken');
        localStorage.removeItem('currentUser');
        updateUIForLoggedOutUser();
    }
}

// Check local auth (fallback)
function checkLocalAuth() {
    const token = localStorage.getItem('firebaseToken');
    const user = localStorage.getItem('currentUser');

    if (token && user) {
        currentUser = JSON.parse(user);
        updateUIForLoggedInUser(currentUser);
    }
}

// Sync user with backend
async function syncUserWithBackend(idToken) {
    try {
        const response = await fetch(`${API_URL}/api/auth/sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${idToken}`
            }
        });

        if (!response.ok) {
            console.error('Failed to sync user with backend');
        }
    } catch (error) {
        console.error('Error syncing user:', error);
    }
}

// Update UI for logged in user
function updateUIForLoggedInUser(user) {
    // Show avatar container and hide login button
    const loginBtn = document.querySelector('.user-menu .btn-secondary');
    const avatarContainer = document.getElementById('user-avatar-container');
    const userAvatar = document.getElementById('user-avatar');
    const userPhoto = document.getElementById('user-photo');
    const userName = document.getElementById('user-name');
    const userEmail = document.getElementById('user-email');
    const userDropdown = document.getElementById('user-dropdown');

    if (loginBtn) loginBtn.classList.add('hidden');
    if (avatarContainer) avatarContainer.classList.remove('hidden');

    // Populate photo or initials
    if (user.photoURL) {
        userPhoto.innerHTML = `<img src="${user.photoURL}" alt="${user.displayName || user.email}" />`;
    } else {
        const initial = (user.displayName || user.email || 'U')[0].toUpperCase();
        userPhoto.innerHTML = `<span>${initial}</span>`;
    }

    // Set name and email
    userName.textContent = user.displayName || user.email || 'User';
    userEmail.textContent = user.email || '';

    // Ensure dropdown is hidden initially
    if (userDropdown) userDropdown.classList.add('hidden');
}

// Toggle user dropdown visibility
function toggleUserMenu(event) {
    event.stopPropagation(); // Prevent click from bubbling to document
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

// Hide dropdown when clicking outside
document.addEventListener('click', function (e) {
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown && !dropdown.contains(e.target) && e.target.id !== 'user-avatar') {
        dropdown.classList.add('hidden');
    }
});

// Update UI for logged out user
function updateUIForLoggedOutUser() {
    const loginBtn = document.querySelector('.user-menu .btn-secondary');
    const userAvatar = document.getElementById('user-avatar');

    if (loginBtn) loginBtn.classList.remove('hidden');
    if (userAvatar) userAvatar.classList.add('hidden');
}

// Google Sign In
async function signInWithGoogle() {
    if (!auth) {
        showAlert('auth-alert', 'error', 'Firebase not initialized. Please refresh the page.');
        return;
    }

    try {
        const provider = new firebase.auth.GoogleAuthProvider();
        provider.addScope('profile');
        provider.addScope('email');

        // Set custom parameters
        provider.setCustomParameters({
            prompt: 'select_account'
        });

        // Try popup first
        try {
            const result = await auth.signInWithPopup(provider);
            showAlert('auth-alert', 'success', 'Successfully signed in with Google!');
            setTimeout(() => closeAuthModal(), 1000);
        } catch (popupError) {
            // If popup fails, try redirect
            if (popupError.code === 'auth/popup-blocked' ||
                popupError.code === 'auth/popup-closed-by-user' ||
                popupError.code === 'auth/cancelled-popup-request') {
                console.log('Popup failed, trying redirect...');
                await auth.signInWithRedirect(provider);
            } else {
                throw popupError;
            }
        }

    } catch (error) {
        console.error('Google sign in error:', error);
        let errorMessage = `Sign in failed: ${error.message}`;

        // Provide helpful error messages
        if (error.code === 'auth/unauthorized-domain') {
            errorMessage = `Domain "${window.location.hostname}" is not authorized. Please add it to Firebase Console → Authentication → Settings → Authorized domains`;
        } else if (error.code === 'auth/operation-not-allowed') {
            errorMessage = 'Google sign-in is not enabled. Please enable it in Firebase Console → Authentication → Sign-in method';
        }

        showAlert('auth-alert', 'error', errorMessage);
    }
}



// Logout
async function logout() {
    try {
        if (auth) {
            await auth.signOut();
        }
        localStorage.removeItem('firebaseToken');
        localStorage.removeItem('currentUser');
        currentUser = null;
        location.reload();
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Show alert helper
function showAlert(elementId, type, message) {
    const alertDiv = document.getElementById(elementId);
    if (!alertDiv) return;

    const iconMap = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };

    alertDiv.innerHTML = `
        <div class="alert alert-${type}">
            <i class="fas ${iconMap[type]}"></i>
            ${message}
        </div>
    `;
}

// Get auth token for API calls
async function getAuthToken() {
    if (currentUser && auth) {
        try {
            return await auth.currentUser.getIdToken();
        } catch (error) {
            console.error('Failed to get token:', error);
        }
    }
    return localStorage.getItem('firebaseToken');
}

// Modal functions
function openAuthModal() {
    document.getElementById('auth-modal').classList.add('active');
}

function closeAuthModal() {
    document.getElementById('auth-modal').classList.remove('active');
}

// API base URL
const API_URL = getApiUrl();

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    const tabContent = document.getElementById(`tab-${tabName}`);
    if (tabContent) {
        tabContent.classList.add('active');
    }

    const tabButtons = document.querySelectorAll('.tab');
    tabButtons.forEach(button => {
        if (button.textContent.toLowerCase().includes(tabName.toLowerCase()) ||
            button.onclick?.toString().includes(tabName)) {
            button.classList.add('active');
        }
    });

    if (tabName === 'jobs') {
        loadJobs();
    } else if (tabName === 'stats') {
        loadStats();
    } else if (tabName === 'generate') {
        loadJobsForSelect();
    }
}

// Scrape Job Form
document.getElementById('scrape-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const url = document.getElementById('job-url').value;
    const alertDiv = document.getElementById('scrape-alert');
    const loadingDiv = document.getElementById('scrape-loading');
    const resultDiv = document.getElementById('scrape-result');

    alertDiv.innerHTML = '';
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');

    try {
        const token = await getAuthToken();
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch(`${API_URL}/api/scrape`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        loadingDiv.classList.add('hidden');

        if (response.ok) {
            showAlert('scrape-alert', 'success', `Job scraped successfully!`);
            await loadJobs();

            resultDiv.innerHTML = `
                <div style="margin-top: 2rem; padding: 1.5rem; background: var(--light); border-radius: var(--radius);">
                    <h3 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-briefcase"></i> ${data.title}
                    </h3>
                    <p><strong><i class="fas fa-building"></i> Company:</strong> ${data.company}</p>
                    <p><strong><i class="fas fa-user"></i> Posted by:</strong> ${data.poster}</p>
                    
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
                            ${data.full_description || data.description}
                        </div>
                    </div>
                </div>
            `;
            resultDiv.classList.remove('hidden');

            document.getElementById('scrape-form').reset();
        } else {
            showAlert('scrape-alert', 'error', data.detail || 'Failed to scrape job');
        }
    } catch (error) {
        loadingDiv.classList.add('hidden');
        showAlert('scrape-alert', 'error', `Network error: ${error.message}`);
    }
});

// Load jobs for select dropdown
async function loadJobsForSelect() {
    try {
        const token = await getAuthToken();
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch(`${API_URL}/api/jobs?limit=50`, { headers });
        const data = await response.json();

        const select = document.getElementById('job-select');
        select.innerHTML = '<option value="">Select a job...</option>';

        data.jobs.forEach(job => {
            const option = document.createElement('option');
            option.value = job.id;
            option.textContent = `${job.title} - ${job.company}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

// Generate CV Form
document.getElementById('generate-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Check auth first
    const token = await getAuthToken();
    if (!token) {
        showAlert('generate-alert', 'info', 'Please login to generate a CV');
        openAuthModal();
        return;
    }

    const jobId = document.getElementById('job-select').value;
    const cvFile = document.getElementById('cv-file').files[0];
    const alertDiv = document.getElementById('generate-alert');
    const loadingDiv = document.getElementById('generate-loading');
    const resultDiv = document.getElementById('generate-result');

    if (!cvFile) {
        showAlert('generate-alert', 'error', 'Please upload a CV file');
        return;
    }

    alertDiv.innerHTML = '';
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');

    const formData = new FormData();
    formData.append('job_id', jobId);
    formData.append('cv_file', cvFile);

    try {
        const token = await getAuthToken();
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch(`${API_URL}/api/generate-cv`, {
            method: 'POST',
            headers,
            body: formData
        });

        const data = await response.json();

        loadingDiv.classList.add('hidden');

        if (response.ok) {
            showAlert('generate-alert', 'success', 'CV generated successfully!');

            resultDiv.innerHTML = `
                <div style="margin-top: 2rem; padding: 1.5rem; background: var(--light); border-radius: var(--radius);">
                    <h3 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-file-alt"></i> Your Tailored CV is Ready!
                    </h3>
                    <div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
                        <a href="${data.cv_markdown}" class="btn btn-secondary" download>
                            <i class="fas fa-file-code"></i> Download Markdown
                        </a>
                        <a href="${data.cv_pdf}" class="btn btn-primary" download>
                            <i class="fas fa-file-pdf"></i> Download PDF
                        </a>
                    </div>
                </div>
            `;
            resultDiv.classList.remove('hidden');
        } else {
            showAlert('generate-alert', 'error', data.detail || 'Failed to generate CV');
        }
    } catch (error) {
        loadingDiv.classList.add('hidden');
        showAlert('generate-alert', 'error', `Network error: ${error.message}`);
    }
});

// Load and display stats
async function loadStats() {
    try {
        const token = await getAuthToken();
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch(`${API_URL}/api/stats`, { headers });
        const data = await response.json();

        displayStats(data);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Generate fresh stats
async function generateStats() {
    const loadingDiv = document.getElementById('stats-loading');
    const contentDiv = document.getElementById('stats-content');

    loadingDiv.classList.remove('hidden');

    try {
        const token = await getAuthToken();
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch(`${API_URL}/api/stats/generate`, {
            method: 'POST',
            headers
        });
        const data = await response.json();

        loadingDiv.classList.add('hidden');

        if (response.ok) {
            displayStats(data.stats, data.charts);
        } else {
            console.error('Stats generation failed:', data);
            contentDiv.innerHTML = `
                <div class="alert alert-error">
                    <i class="fas fa-exclamation-circle"></i>
                    Failed to generate stats: ${data.detail || 'Unknown error'}
                </div>
            `;
        }
    } catch (error) {
        loadingDiv.classList.add('hidden');
        console.error('Error generating stats:', error);
        contentDiv.innerHTML = `
            <div class="alert alert-error">
                <i class="fas fa-exclamation-circle"></i>
                Network error: ${error.message}. Check console for details.
            </div>
        `;
    }
}

// Display stats
function displayStats(stats, charts) {
    const contentDiv = document.getElementById('stats-content');

    console.log('Stats data received:', stats);

    // Check if Plotly is available
    const usePlotly = typeof Plotly !== 'undefined';
    if (!usePlotly) {
        console.warn('Plotly not loaded, using CSS charts as fallback');
    }

    // Simple markdown to HTML converter for AI insights
    function formatMarkdown(text) {
        return text
            // Bold: **text** or __text__ - with highlighting
            .replace(/\*\*(.+?)\*\*/g, '<strong style="color: #ffd700; background: rgba(255, 215, 0, 0.15); padding: 2px 6px; border-radius: 4px;">$1</strong>')
            .replace(/__(.+?)__/g, '<strong style="color: #ffd700; background: rgba(255, 215, 0, 0.15); padding: 2px 6px; border-radius: 4px;">$1</strong>')
            // Italic: *text* or _text_
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/_(.+?)_/g, '<em>$1</em>')
            // Code: `code`
            .replace(/`(.+?)`/g, '<code style="background: rgba(0,0,0,0.1); padding: 2px 6px; border-radius: 4px; font-family: monospace;">$1</code>')
            // Line breaks
            .replace(/\n/g, '<br>');
    }

    // Helper to create Plotly chart
    function createPlotlyChart(elementId, data, title, color) {
        if (!usePlotly) return false;

        const element = document.getElementById(elementId);
        if (!element) {
            console.error(`Element ${elementId} not found`);
            return false;
        }

        if (!data || !data.labels || data.labels.length === 0) {
            console.log(`No data for ${elementId}`);
            return false;
        }

        try {
            const trace = {
                type: 'bar',
                x: data.values,
                y: data.labels,
                orientation: 'h',
                marker: {
                    color: color,
                    line: {
                        color: color.replace('0.8', '1'),
                        width: 2
                    }
                },
                text: data.values.map(v => v.toFixed(2)),
                textposition: 'outside',
                hovertemplate: '<b>%{y}</b><br>Score: %{x:.2f}<extra></extra>'
            };

            const layout = {
                title: {
                    text: title,
                    font: { size: 18, weight: 700, color: '#2d3436' }
                },
                xaxis: {
                    title: 'Relevance Score',
                    showgrid: true,
                    gridcolor: '#e2e8f0'
                },
                yaxis: {
                    autorange: 'reversed',
                    showgrid: false
                },
                margin: { l: 150, r: 50, t: title ? 60 : 20, b: 60 },
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: 'white',
                height: Math.max(300, data.labels.length * 40)
            };

            const config = {
                responsive: true,
                displayModeBar: false
            };

            Plotly.newPlot(elementId, [trace], layout, config);
            console.log(`Plotly chart created for ${elementId}`);
            return true;
        } catch (error) {
            console.error(`Error creating Plotly chart for ${elementId}:`, error);
            return false;
        }
    }

    // Helper to create CSS bar chart (fallback)
    function createBarChart(items, color, maxItems = 10) {
        if (!items || items.length === 0) {
            return '<p style="text-align: center; color: var(--gray); padding: 2rem;">No data available</p>';
        }

        const displayItems = items.slice(0, maxItems);
        const maxValue = Math.max(...displayItems.map(item => item.count || 0));

        return displayItems.map((item, index) => {
            const percentage = maxValue > 0 ? (item.count / maxValue) * 100 : 0;
            const delay = index * 0.1;

            return `
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600; color: var(--dark);">${item.name}</span>
                        <span style="font-weight: 700; color: ${color};">${item.count} job${item.count !== 1 ? 's' : ''}</span>
                    </div>
                    <div style="
                        background: #e2e8f0;
                        border-radius: 8px;
                        height: 32px;
                        position: relative;
                        overflow: hidden;
                    ">
                        <div style="
                            background: linear-gradient(90deg, ${color}, ${color}dd);
                            height: 100%;
                            width: ${percentage}%;
                            border-radius: 8px;
                            display: flex;
                            align-items: center;
                            padding: 0 1rem;
                            color: white;
                            font-weight: 600;
                            font-size: 0.9rem;
                            transition: width 1s ease-out ${delay}s;
                            animation: slideIn 1s ease-out ${delay}s both;
                        ">
                            ${item.percentage}%
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    let html = `
        <style>
            @keyframes slideIn {
                from {
                    width: 0%;
                    opacity: 0;
                }
                to {
                    opacity: 1;
                }
            }
        </style>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">${stats.total_jobs}</div>
                <div class="stat-label">Total Jobs Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.technologies.length}</div>
                <div class="stat-label">Top Technologies</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.languages.length}</div>
                <div class="stat-label">Languages Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.soft_skills.length + stats.hard_skills.length}</div>
                <div class="stat-label">Skills Identified</div>
            </div>
        </div>
    `;

    // AI Market Analysis - formatted as cards with highlighted keywords
    if (stats.market_summary && stats.market_summary !== "Market insights currently unavailable.") {
        // Split into paragraphs and format nicely
        const paragraphs = stats.market_summary.split('\n\n').filter(p => p.trim());
        
        html += `
            <div class="chart-container" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
                <h3 style="color: white; display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                    <i class="fas fa-robot" style="font-size: 1.5rem;"></i>
                    <span>AI Market Analysis</span>
                </h3>
                <div style="display: grid; gap: 1rem;">
                    ${paragraphs.map((p, i) => `
                        <div style="
                            background: rgba(255, 255, 255, 0.15); 
                            backdrop-filter: blur(10px);
                            padding: 1.25rem; 
                            border-radius: 12px;
                            border: 1px solid rgba(255, 255, 255, 0.2);
                            line-height: 1.7;
                        ">
                            <div style="display: flex; align-items: start; gap: 0.75rem;">
                                <i class="fas fa-lightbulb" style="color: #ffd700; margin-top: 0.25rem; font-size: 1.1rem;"></i>
                                <p style="margin: 0; color: rgba(255, 255, 255, 0.95);">${formatMarkdown(p.trim())}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Technologies Chart
    if (stats.technologies.length > 0) {
        html += `
            <div class="chart-container">
                <h3><i class="fas fa-laptop-code"></i> Top Technologies</h3>
                <p style="color: var(--gray); margin-bottom: 1.5rem;">Technologies found across all job descriptions</p>
                ${usePlotly ? '<div id="chart-technologies" style="width: 100%; min-height: 400px;"></div>' : createBarChart(stats.technologies, '#667eea', 10)}
            </div>
        `;
    }

    // Languages Chart
    if (stats.languages.length > 0) {
        html += `
            <div class="chart-container">
                <h3><i class="fas fa-code"></i> Programming Languages</h3>
                <p style="color: var(--gray); margin-bottom: 1.5rem;">Most requested programming languages</p>
                ${usePlotly ? '<div id="chart-languages" style="width: 100%; min-height: 400px;"></div>' : createBarChart(stats.languages, '#4ecdc4', 10)}
            </div>
        `;
    }

    // Skills Section - Split into Soft and Hard Skills
    if (stats.soft_skills.length > 0 || stats.hard_skills.length > 0) {
        html += `
            <div class="chart-container">
                <h3><i class="fas fa-brain"></i> Skills Analysis</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 1.5rem;">
        `;

        // Soft Skills
        if (stats.soft_skills.length > 0) {
            html += `
                <div>
                    <h4 style="color: #e17055; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-users"></i> Soft Skills
                    </h4>
                    <div id="chart-soft-skills" style="width: 100%; min-height: 300px;"></div>
                    <div style="margin-top: 1rem; display: grid; gap: 0.5rem;">
                        ${stats.soft_skills.slice(0, 3).map((s, i) => `
                            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: #fff5f5; border-radius: 6px;">
                                <span style="font-weight: 500;">${s.name}</span>
                                <span style="color: #e17055; font-weight: 600;">${s.count} job${s.count !== 1 ? 's' : ''}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Hard Skills
        if (stats.hard_skills.length > 0) {
            html += `
                <div>
                    <h4 style="color: #00b894; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-cogs"></i> Hard Skills
                    </h4>
                    <div id="chart-hard-skills" style="width: 100%; min-height: 300px;"></div>
                    <div style="margin-top: 1rem; display: grid; gap: 0.5rem;">
                        ${stats.hard_skills.slice(0, 3).map((h, i) => `
                            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: #f0fff4; border-radius: 6px;">
                                <span style="font-weight: 500;">${h.name}</span>
                                <span style="color: #00b894; font-weight: 600;">${h.count} job${h.count !== 1 ? 's' : ''}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        html += `
                </div>
            </div>
        `;
    }

    // Recommendations
    if (stats.recommendations && stats.recommendations.length > 0) {
        html += `
            <div class="chart-container" style="background: linear-gradient(to right, #ffeaa7, #fdcb6e); border: none;">
                <h3 style="color: #2d3436;"><i class="fas fa-lightbulb"></i> Recommendations</h3>
                <div style="display: grid; gap: 1rem;">
                    ${stats.recommendations.map((r, i) => `
                        <div style="
                            background: white;
                            padding: 1.25rem;
                            border-radius: 12px;
                            display: flex;
                            align-items: start;
                            gap: 1rem;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        ">
                            <div style="
                                background: linear-gradient(135deg, #ffd700, #ffed4e);
                                width: 32px;
                                height: 32px;
                                border-radius: 50%;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                flex-shrink: 0;
                                box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
                            ">
                                <i class="fas fa-star" style="color: white; font-size: 0.9rem;"></i>
                            </div>
                            <span style="color: #2d3436; line-height: 1.6; font-size: 1.05rem;">${r}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    contentDiv.innerHTML = html;

    // Create Plotly charts after DOM is updated
    setTimeout(() => {
        console.log('Creating Plotly charts...');
        if (stats.chart_data) {
            console.log('Chart data exists:', stats.chart_data);
            
            if (stats.chart_data.technologies && stats.chart_data.technologies.labels.length > 0) {
                createPlotlyChart('chart-technologies', stats.chart_data.technologies, 'Top Technologies', 'rgba(102, 126, 234, 0.8)');
            }
            if (stats.chart_data.languages && stats.chart_data.languages.labels.length > 0) {
                createPlotlyChart('chart-languages', stats.chart_data.languages, 'Programming Languages', 'rgba(78, 205, 196, 0.8)');
            }
            if (stats.chart_data.soft_skills && stats.chart_data.soft_skills.labels.length > 0) {
                createPlotlyChart('chart-soft-skills', stats.chart_data.soft_skills, '', 'rgba(225, 112, 85, 0.8)');
            }
            if (stats.chart_data.hard_skills && stats.chart_data.hard_skills.labels.length > 0) {
                createPlotlyChart('chart-hard-skills', stats.chart_data.hard_skills, '', 'rgba(0, 184, 148, 0.8)');
            }
        } else {
            console.error('No chart_data in stats!');
        }
    }, 200);
}

// Load jobs list
async function loadJobs() {
    try {
        const token = await getAuthToken();
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch(`${API_URL}/api/jobs?limit=1000`, { headers });
        const data = await response.json();
        // Refresh stats after fetching jobs to keep UI in sync
        await loadStats();

        const listDiv = document.getElementById('jobs-list');
        // Clear any previous entries to avoid duplicates
        listDiv.innerHTML = '';

        if (data.jobs.length === 0) {
            listDiv.innerHTML = `
                <p style="text-align: center; color: var(--gray); padding: 3rem;">
                    <i class="fas fa-inbox" style="font-size: 3rem; display: block; margin-bottom: 1rem; opacity: 0.5;"></i>
                    No jobs scraped yet. Start by scraping a job!
                </p>
            `;
            return;
        }

        listDiv.innerHTML = data.jobs.map(job => `
            <div class="job-item">
                <div class="job-title">${job.title}</div>
                <div class="job-company">
                    <i class="fas fa-building"></i> ${job.company}
                </div>
                <div class="job-meta">
                    <span><i class="fas fa-user"></i> ${job.poster}</span>
                    <span><i class="fas fa-calendar"></i> ${new Date(job.scraped_at).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

// LinkedIn Auth removed - anonymous scraping now!
