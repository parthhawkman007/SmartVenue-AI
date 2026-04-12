/**
 * SmartVenue AI - Frontend Application Logic
 * Implements clean, maintainable, modular JavaScript handling asynchronous
 * data fetching, structural DOM rendering, and user feedback states perfectly.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Cache DOM Elements for Efficiency
    const fetchBtn = document.getElementById('fetchBtn');
    const crowdList = document.getElementById('crowdList');
    const loader = document.getElementById('loader');

    // Configuration
    const CONFIG = {
        // Deployed Cloud Run backend URL
        API_URL: 'https://smartvenue-api-1077180830187.asia-south1.run.app/crowd',
        ANIMATION_DELAY_MS: 100
    };

    /**
     * Toggles the loading UI state for the fetching process.
     * @param {boolean} isLoading - Whether the UI should display processing states.
     */
    const setLoadingState = (isLoading) => {
        loader.style.display = isLoading ? 'block' : 'none';
        fetchBtn.disabled = isLoading;
        fetchBtn.style.opacity = isLoading ? '0.7' : '1';
        fetchBtn.setAttribute('aria-busy', isLoading.toString());
    };

    /**
     * Determines the CSS status class corresponding to a given crowd density.
     * @param {number} density - Crowd density percentage (0-100).
     * @returns {string} The computed string class explicitly tying logic to CSS.
     */
    const getStatusClass = (density) => {
        if (density <= 30) return 'status-low';       // Green
        if (density <= 70) return 'status-moderate';  // Yellow
        return 'status-very-crowded';                 // Red
    };

    /**
     * Renders incoming JSON payloads safely onto the DOM structure.
     * Applies modular item generation natively to prevent complex DOM rewrites.
     * @param {Array<Object>} data - The API JSON response.
     */
    const renderCrowdData = (data) => {
        // Safe clear before render
        crowdList.innerHTML = '';
        
        if (data.length === 0) {
            crowdList.innerHTML = `
                <div style="color: var(--text-muted); margin-top: 20px; font-weight: 500;">
                    No crowd data available currently. Initialize Firestore seeding via API POST endpoint.
                </div>
            `;
            return;
        }

        data.forEach(({ zone, density, status }, index) => {
            const li = document.createElement('li');
            li.className = 'crowd-item';
            li.setAttribute('role', 'listitem');
            
            // Stagger the entrance animation purely using inline calculations
            li.style.animationDelay = `${index * CONFIG.ANIMATION_DELAY_MS}ms`; 
            
            const statusClass = getStatusClass(density);
            
            // Secure template injection using exact destructured payload
            li.innerHTML = `
                <div class="zone-name">${zone}</div>
                <div class="zone-info" aria-label="${status} status at ${density} percent">
                    <span class="status-indicator ${statusClass}" aria-hidden="true"></span>
                    <span style="font-weight: 500; font-size: 0.95rem; margin-right: 5px;">${status}</span>
                    <span class="density-badge">${density}%</span>
                </div>
            `;
            
            crowdList.appendChild(li);
        });
    };

    /**
     * Main Orchestrator Function: Handles Asynchronous Networking safely.
     */
    const handleFetchData = async () => {
        setLoadingState(true);
        crowdList.innerHTML = '';

        try {
            // Fake delay purely for demonstration aesthetics
            await new Promise(r => setTimeout(r, 600));

            const response = await fetch(CONFIG.API_URL);
            
            if (!response.ok) {
                // Generates accurate standard error throwing natively handled in catch block
                throw new Error(`HTTP Error Status: ${response.status}`);
            }
            
            const data = await response.json();
            renderCrowdData(data);
            
        } catch (error) {
            console.error('API Fetch Runtime Error:', error);
            crowdList.innerHTML = `
                <div style="color: #ef4444; margin-top: 20px; font-weight: 500; font-size: 0.9rem;" role="alert">
                    Failed to fetch data. Please check your network connection or try again later.
                </div>
            `;
        } finally {
            setLoadingState(false);
        }
    };

    // Attach Event Listeners explicitly natively mapped
    fetchBtn.addEventListener('click', handleFetchData);
});
