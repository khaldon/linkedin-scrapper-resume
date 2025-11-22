const CONFIG = {
    // Backend API URL (Hugging Face Spaces)
    API_URL: "https://MKhaldon-linkedin-scraper-resume.hf.space",
    
    // Set to true ONLY for local development
    USE_LOCAL_API: false
};

// Helper to get the active URL
function getApiUrl() {
    if (CONFIG.USE_LOCAL_API && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
        return 'http://localhost:8080';
    }
    return CONFIG.API_URL;
}
