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
    const loginBtn = document.querySelector('.user-menu .btn-secondary');
    const userAvatar = document.getElementById('user-avatar');

    if (loginBtn) loginBtn.classList.add('hidden');
    if (userAvatar) {
        userAvatar.classList.remove('hidden');

        if (user.photoURL) {
            userAvatar.innerHTML = `<img src="${user.photoURL}" alt="${user.displayName || user.email}" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
        } else {
            const initial = (user.displayName || user.email || 'U')[0].toUpperCase();
            userAvatar.innerHTML = `<span>${initial}</span>`;
        }

        userAvatar.title = user.displayName || user.email;
    }
}

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

    let html = `
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
                <div class="stat-number">${stats.soft_skills.length}</div>
                <div class="stat-label">Soft Skills</div>
            </div>
        </div>
    `;

    if (stats.market_summary) {
        html += `
            <div class="chart-container" style="background: linear-gradient(to right, #f8f9fa, #e9ecef); border-left: 5px solid var(--primary);">
                <h3><i class="fas fa-robot"></i> AI Market Analysis</h3>
                <div style="white-space: pre-wrap; line-height: 1.6; color: var(--dark);">
                    ${stats.market_summary}
                </div>
            </div>
        `;
    }

    if (stats.technologies.length > 0) {
        html += `
            <div class="chart-container">
                <h3><i class="fas fa-laptop-code"></i> Top Technologies</h3>
                <img src="${API_URL}/data/chart_technologies.png?ts=${Date.now()}" alt="Technologies Chart">
                <ul style="margin-top: 1rem; list-style: none; padding: 0;">
                    ${stats.technologies.map(t => `
                        <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-check-circle" style="color: var(--success);"></i>
                            <strong>${t.name}</strong>: ${t.percentage}% of jobs
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    if (stats.languages.length > 0) {
        html += `
            <div class="chart-container">
                <h3><i class="fas fa-code"></i> Programming Languages</h3>
                <img src="${API_URL}/data/chart_languages.png?ts=${Date.now()}" alt="Languages Chart">
                <ul style="margin-top: 1rem; list-style: none; padding: 0;">
                    ${stats.languages.map(l => `
                        <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-check-circle" style="color: var(--success);"></i>
                            <strong>${l.name}</strong>: ${l.percentage}% of jobs
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    if (stats.recommendations && stats.recommendations.length > 0) {
        html += `
            <div class="chart-container">
                <h3><i class="fas fa-lightbulb"></i> Recommendations</h3>
                <ul style="list-style: none; padding: 0;">
                    ${stats.recommendations.map(r => `
                        <li style="padding: 0.75rem 0; display: flex; align-items: start; gap: 0.75rem;">
                            <i class="fas fa-star" style="color: var(--warning); margin-top: 0.25rem;"></i>
                            <span>${r}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    contentDiv.innerHTML = html;
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
