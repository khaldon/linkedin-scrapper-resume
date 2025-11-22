const CONFIG = {
    // Replace this with your Hugging Face Space URL
    // Format: https://YOUR_USERNAME-SPACE_NAME.hf.space
    API_URL: "https://MKhaldon-linkedin-scraper-resume.hf.space",
    
    // Set to true to use local API (http://localhost:8080)
    // Set to false for production (Hugging Face)
    USE_LOCAL_API: false
};

// Helper to get the active URL
function getApiUrl() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return CONFIG.USE_LOCAL_API ? 'http://localhost:8080' : CONFIG.API_URL;
    }
    return CONFIG.API_URL;
}
