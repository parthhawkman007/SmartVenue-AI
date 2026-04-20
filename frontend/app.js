const firebaseConfig = {
    apiKey: "AIzaSyC9_utODz62Pd68K6UjvNQLHaTVT3APPFY",
    authDomain: "smart-experience-ai.firebaseapp.com",
    projectId: "smart-experience-ai",
    storageBucket: "smart-experience-ai.firebasestorage.app",
    messagingSenderId: "1077180830187",
    appId: "1:1077180830187:web:9a24b02141d4c5f5c289ae",
    measurementId: "G-NZ2H2MNZC3"
};

if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const auth = firebase.auth();

let currentToken = null;
let currentRole = "user";

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // Structural Bindings
    const API_BASE = 'https://smartvenue-api-1077180830187.asia-south1.run.app';

    const DOM = {
        loginContainer: document.getElementById('login-container'),
        appContainer: document.getElementById('app-container'),
        authForm: document.getElementById('auth-form'),
        authEmail: document.getElementById('auth-email'),
        authPassword: document.getElementById('auth-password'),
        googleBtn: document.getElementById('google-login-btn'),
        authToggle: document.getElementById('auth-toggle-mode'),
        authTitle: document.getElementById('auth-title'),
        authSubmitBtn: document.getElementById('auth-submit-btn'),
        logoutBtn: document.getElementById('logoutBtn'),
        userDisplayEmail: document.getElementById('user-display-email'),
        userDisplayRole: document.getElementById('user-display-role'),
        adminOnlyBtns: document.querySelectorAll('.admin-only'),
        zones: document.getElementById('zonesGrid'),
        analytics: document.getElementById('analyticsList'),
        alerts: document.getElementById('alertsContainerFull'),
        insights: document.getElementById('insightsContainerFull'),
        envGrid: document.getElementById('envGrid'),
        simulateBtn: document.getElementById('simulateBtn'),
        autoToggle: document.getElementById('autoRefreshToggle'),
        eventTypeToggle: document.getElementById('eventTypeToggle'),
        loader: document.getElementById('global-loader'),
        viewTitle: document.getElementById('viewTitle'),
        adminStartSystemBtn: document.getElementById('adminStartSystemBtn'),
        adminStopSystemBtn: document.getElementById('adminStopSystemBtn'),
        systemStatusIndicator: document.getElementById('systemStatusIndicator'),
        systemStatusText: document.getElementById('systemStatusText'),
        lastSyncTime: document.getElementById('last-sync-time'),
        statusDot: document.getElementById('status-dot'),
        statusText: document.getElementById('status-text'),
        emergencyToast: document.getElementById('emergency-toast')
    };

    let syncInterval = null;
    let activeView = "dashboard";

    // SPA Routing Logic
    const views = document.querySelectorAll('.view-section');
    const navBtns = document.querySelectorAll('.nav-btn');

    const navigateTo = (target) => {
        // Update UI Title
        const titleMap = {
            'dashboard': 'Live Dashboard',
            'analytics': 'Topology Analytics',
            'alerts': 'Serious Alerts',
            'insights': 'Intelligence Panel',
            'environment': 'Cloud Environment',
            'controls': 'System Controls'
        };
        DOM.viewTitle.innerText = titleMap[target] || 'Dashboard';
        
        // Hide inactive views
        views.forEach(v => v.classList.remove('active'));
        document.getElementById(`view-${target}`).classList.add('active');

        // Toggle active button states
        navBtns.forEach(btn => {
            btn.classList.remove('active');
            btn.removeAttribute('aria-current');
        });
        const activeButton = document.querySelector(`.nav-btn[data-target="${target}"]`);
        activeButton.classList.add('active');
        activeButton.setAttribute('aria-current', 'page');
        
        activeView = target;
        // Fetch data dynamically
        fetchViewData(target);
    };

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tgt = btn.getAttribute('data-target');
            navigateTo(tgt);
        });
    });

    // UX System Parameters
    const COLORS = {
        empty: 'var(--empty)',
        low: 'var(--safe)',
        moderate: 'var(--caution)',
        crowded: 'var(--warning)',
        very_crowded: 'var(--danger)'
    };

    const getStateColor = (density) => {
        if (density <= 20) return COLORS.empty;
        if (density <= 40) return COLORS.low;
        if (density <= 70) return COLORS.moderate;
        if (density <= 90) return COLORS.crowded;
        return COLORS.very_crowded;
    };

    const getTrendIcon = (trend) => {
        if (trend === 'increasing') return '<span class="trend-icon trend-increasing" title="Increasing Trend">↑</span>';
        if (trend === 'decreasing') return '<span class="trend-icon trend-decreasing" title="Decreasing Trend">↓</span>';
        return '<span class="trend-icon trend-stable" title="Stable Bounds">→</span>';
    };

    const formatTime = (iso) => {
        const d = new Date(iso);
        return d.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + d.getMilliseconds().toString().padStart(3,'0');
    };

    const sanitizeHTML = (str) => {
        return String(str).replace(/[&<>'"]/g, match => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[match]);
    };

    const renderInlineMessage = (target, message, color = 'var(--text-muted)') => {
        target.innerHTML = `<div style="color: ${color}; font-size: 1.1rem; text-align: center; padding: 40px;">${sanitizeHTML(message)}</div>`;
    };

    const clearViewData = () => {
        DOM.analytics.innerHTML = '';
        DOM.insights.innerHTML = '';
        DOM.alerts.innerHTML = '';
        DOM.envGrid.innerHTML = '';
    };

    // View Renderers Matrix
    const renderDashboard = (zones) => {
        if (!zones || zones.length === 0) {
            renderInlineMessage(DOM.zones, 'No active crowd monitoring streams detected currently.');
            return;
        }
        DOM.zones.innerHTML = zones.map(z => {
            const colorParam = getStateColor(z.density);
            return `
                <div class="zone-card" style="--state-color: ${colorParam};">
                    <div class="zone-header">
                        <div class="zone-name">${sanitizeHTML(z.zone)}</div>
                        ${getTrendIcon(z.trend)}
                    </div>
                    <div class="zone-metrics">
                        <div class="density-ring" style="--density: ${z.density}">
                            <div class="density-value">${z.density}%</div>
                        </div>
                        <div class="zone-details">
                            <div class="status-badge" style="box-shadow: 0 0 10px ${colorParam}40">${sanitizeHTML(z.status)}</div>
                            <div class="timestamp">SYNC: ${sanitizeHTML(formatTime(z.timestamp))}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    };

    const renderAnalytics = (zones) => {
        if (!zones || zones.length === 0) {
            renderInlineMessage(DOM.analytics, 'No analytical data available for processing.');
            return;
        }
        // Sort by density descending
        const sorted = [...zones].sort((a,b) => b.density - a.density);
        DOM.analytics.innerHTML = sorted.map(z => `
            <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 15px 20px; display: flex; align-items:center; justify-content:space-between;">
                <div style="font-size: 1.1rem; font-weight: 600;">${sanitizeHTML(z.zone)}</div>
                <div style="display:flex; align-items:center; gap: 20px;">
                    <div style="width: 250px; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow:hidden;">
                        <div style="height: 100%; width: ${z.density}%; background: ${getStateColor(z.density)};"></div>
                    </div>
                    <div style="font-weight: 700; width: 45px; text-align:right;">${z.density}%</div>
                </div>
            </div>
        `).join('');
    };

    const renderAlerts = (alerts) => {
        let displayAlerts = alerts;
        if (state.userRole === "user") {
            displayAlerts = displayAlerts.filter(a => a.level !== "critical");
        }
        
        if (!displayAlerts.length) {
            DOM.alerts.innerHTML = '<div style="color: var(--safe); font-size: 1.1rem; font-weight:600;">✓ System Nominal. Zero threshold breaches dynamically logging.</div>';
            return;
        }
        DOM.alerts.innerHTML = displayAlerts.map(a => `
            <div class="alert-item alert-${sanitizeHTML(a.level)}">
                <div style="font-weight: 700; margin-bottom: 5px; color: white;">⚠️ ${sanitizeHTML(a.zone)} [${sanitizeHTML(a.level).toUpperCase()}]</div>
                <div style="color: rgba(255,255,255,0.8);">${sanitizeHTML(a.message)}</div>
            </div>
        `).join('');
    };

    const renderInsights = (recommendations) => {
        let displayRecs = recommendations;
        if (state.userRole === "user") {
            displayRecs = displayRecs.map(r => {
                if (r.action.toLowerCase().includes("deploy") || r.action.toLowerCase().includes("dispatch") || r.action.toLowerCase().includes("immediate")) {
                    return { ...r, action: "Standby for Command Instructions", reason: "Tactical structural shifts are actively being managed by Administrative leads securely." };
                }
                return r;
            });
        }
        
        if (!displayRecs.length) {
            DOM.insights.innerHTML = '<div style="color: var(--text-muted); font-size: 0.95rem;">Standby for structural tactical shifts gracefully.</div>';
            return;
        }
        DOM.insights.innerHTML = displayRecs.map(r => `
            <div class="insight-item">
                <div style="font-weight: 700; font-size: 1.1rem; color: white; margin-bottom: 6px;">🎯 ${sanitizeHTML(r.action)}</div>
                <div style="color: rgba(255,255,255,0.7); font-size: 0.95rem;">REASON INTEGRITY: ${sanitizeHTML(r.reason)}</div>
            </div>
        `).join('');
    };

    // Global State Management
    const state = {
        crowd: [],
        insights: {},
        alerts: [],
        environment: {},
        userRole: null
    };

    /**
     * Display non-blocking global error toast UI
     */
    const showGlobalError = (message) => {
        const toast = document.getElementById('global-error-toast');
        const text = document.getElementById('global-error-text');
        if (!toast || !text) return;
        
        text.innerText = message;
        toast.style.display = 'flex';
        
        setTimeout(() => {
            toast.style.display = 'none';
        }, 4000);
    };

    /**
     * Singleton API Client enforcing consistent wrappers, headers, and request debouncing.
     */
    const apiClient = {
        cache: {},
        
        async fetch(endpoint, options = {}, force = false) {
            if (!currentToken) return null;
            
            const evt = DOM.eventTypeToggle.value;
            const url = `${API_BASE}${endpoint}?event=${evt}`;
            
            // Prevent duplicate fetches on rapid tab switching
            if (!force && this.cache[url] && (Date.now() - this.cache[url].time < 2000)) {
                return this.cache[url].data;
            }
            
            const headers = { 
                "Authorization": `Bearer ${currentToken}`,
                "Content-Type": "application/json",
                ...(options.headers || {})
            };
            
            try {
                const res = await fetch(url, { ...options, headers });
                
                if (res.status === 401 || res.status === 403) {
                    console.error("Auth session expired or insufficient privileges.");
                    await auth.signOut();
                    return null;
                }
                
                const responsePayload = await res.json().catch(() => ({ status: "error", message: "Invalid JSON response" }));
                
                if (!res.ok || responsePayload.status === "error") {
                    throw new Error(responsePayload.message || responsePayload.detail || `HTTP Error ${res.status}`);
                }
                
                if (responsePayload.status === 'idle') {
                    return { idle: true, message: responsePayload.message };
                }
                
                // Cache successful structural queries safely
                if (options.method === 'GET' || !options.method) {
                    this.cache[url] = { time: Date.now(), data: responsePayload.data };
                }
                
                return responsePayload.data;
                
            } catch (err) {
                console.error(`[API ERROR] ${endpoint}:`, err.message);
                throw err;
            }
        }
    };

    const fetchViewData = async (target, forceSync = false) => {
        /**
         * Fetches situational data for the active dashboard view.
         * Implements structural try-catch with global loading state management.
         */
        if (!currentToken) return;
        if (target === 'controls') return;
        
        DOM.loader.classList.add('active');
        try {
            let domain = target;
            if (target === 'dashboard' || target === 'analytics') domain = 'crowd';
            
            const data = await apiClient.fetch(`/${domain}`, {}, forceSync);
            
            if (!data) return; // Unauthenticated drop
            
            if (data.idle) {
                renderInlineMessage(DOM.zones, data.message || 'System Idle. Waiting for Admin activation.', 'var(--safe)');
                clearViewData();
                return;
            }
            
            // Map data to local state slices and trigger renderers
            if (domain === 'crowd') {
                state.crowd = data;
                if (target === 'dashboard') renderDashboard(state.crowd);
                if (target === 'analytics') renderAnalytics(state.crowd);
            } else if (domain === 'insights') {
                state.insights = data;
                renderInsights(state.insights.recommendations || []);
            } else if (domain === 'alerts') {
                state.alerts = data;
                renderAlerts(state.alerts || []);
            } else if (domain === 'environment') {
                state.environment = data;
                renderEnvironment(state.environment);
            }
        } catch (err) {
            const msg = `Unable to load ${target}. ${err.message || 'Check system connectivity.'}`;
            if (target === 'dashboard') {
                renderInlineMessage(DOM.zones, msg, 'var(--danger)');
            } else {
                showGlobalError(msg);
            }
        } finally {
            DOM.loader.classList.remove('active');
            // Update Sync Status Panel
            if (DOM.lastSyncTime) DOM.lastSyncTime.innerText = new Date().toLocaleTimeString();
            
            const hasCriticalAlerts = state.alerts && state.alerts.some(a => a.level === 'critical');
            if (hasCriticalAlerts) {
                DOM.statusDot.className = 'status-dot dot-critical';
                DOM.statusText.innerText = 'Critical Thresholds Detected';
                DOM.statusText.style.color = 'var(--danger)';
            } else {
                DOM.statusDot.className = 'status-dot dot-stable';
                DOM.statusText.innerText = 'Stable Operations';
                DOM.statusText.style.color = 'var(--safe)';
            }
        }
    };

    const renderEnvironment = (envData) => {
        if (envData && envData.event_phase) {
            DOM.envGrid.innerHTML = `
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 5px;">Active Event Phase</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: white;">${sanitizeHTML(envData.event_phase)}</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 5px;">Meteorological Conditions</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: white;">${sanitizeHTML(envData.weather_condition)}</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 5px;">Thermal Sensors</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: var(--warning);">${sanitizeHTML(envData.temperature_celsius)}°C</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 5px;">Humidity Integrity</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: var(--empty);">${sanitizeHTML(envData.humidity_percent)}%</div>
                </div>
            `;
        } else {
            DOM.envGrid.innerHTML = '';
        }
    };

    const triggerFullSyncCycle = async (shouldSimulate = false) => {
        if (!currentToken) return; // Prevent idle executions natively
        
        if (shouldSimulate) {
            try {
                await apiClient.fetch('/simulate', { method: 'GET' }, true).catch(e => console.warn("API Simulate Hook Error.", e));
            } catch (error) {}
        }

        await fetchViewData(activeView);
    };

    // Attach Interactivity
    DOM.simulateBtn.addEventListener('click', () => {
        // UI Feedback: Emergency Scenario
        DOM.emergencyToast.style.display = 'flex';
        document.body.classList.add('emergency-active');
        
        setTimeout(() => {
            DOM.emergencyToast.style.display = 'none';
            document.body.classList.remove('emergency-active');
        }, 3000);

        triggerFullSyncCycle(true);
    });
    DOM.eventTypeToggle.addEventListener('change', () => triggerFullSyncCycle(false));

    DOM.autoToggle.addEventListener('change', (e) => {
        if (e.target.checked) {
            if (syncInterval) clearInterval(syncInterval);
            triggerFullSyncCycle(true);
            syncInterval = setInterval(() => triggerFullSyncCycle(true), 5000);
        } else {
            if (syncInterval) {
                clearInterval(syncInterval);
                syncInterval = null;
            }
        }
    });

    const toggleSystemActiveState = (isActive) => {
        DOM.systemStatusIndicator.style.background = isActive ? 'var(--safe)' : '#666';
        DOM.systemStatusText.innerText = isActive ? 'ACTIVE' : 'IDLE';
        DOM.systemStatusText.style.color = isActive ? 'var(--safe)' : 'var(--text-muted)';
        
        DOM.autoToggle.checked = isActive;
        DOM.autoToggle.dispatchEvent(new Event('change'));
    };

    if (DOM.adminStartSystemBtn) {
        DOM.adminStartSystemBtn.addEventListener('click', async () => {
            if (!currentToken) return;
            DOM.loader.classList.add('active');
            try {
                const data = await apiClient.fetch("/admin/system/start", { method: "POST" }, true);
                if (data || data === null) {
                    toggleSystemActiveState(true);
                }
            } catch (e) {
                console.error("[ADMIN START ERROR]", e);
                showGlobalError(`Activation Failed: ${e.message || 'Critical failure during system engagement.'}`);
            } finally {
                DOM.loader.classList.remove('active');
            }
        });
    }

    if (DOM.adminStopSystemBtn) {
        DOM.adminStopSystemBtn.addEventListener('click', async () => {
            if (!currentToken) return;
            DOM.loader.classList.add('active');
            try {
                const data = await apiClient.fetch("/admin/system/stop", { method: "POST" }, true);
                if (data || data === null) {
                    toggleSystemActiveState(false);
                }
            } catch (e) {
                console.error("[ADMIN STOP ERROR]", e);
                showGlobalError(`Deactivation Failed: ${e.message}`);
            } finally {
                DOM.loader.classList.remove('active');
            }
        });
    }

    // Authentication & Role Logic
    let isSignup = false;
    DOM.authToggle.addEventListener('click', () => {
        isSignup = !isSignup;
        DOM.authTitle.innerText = isSignup ? 'Create Account' : 'Welcome Back';
        DOM.authSubmitBtn.innerText = isSignup ? 'Sign Up' : 'Sign In';
        DOM.authToggle.innerText = isSignup ? 'Already have an account? Sign in' : 'Need an account? Sign up';
    });

    DOM.authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = DOM.authEmail.value.trim();
        const password = DOM.authPassword.value;

        // --- Production Validation Bounds ---
        if (!email || !password) {
            alert("Please fill in both email and password fields.");
            return;
        }

        if (password.length < 6) {
            alert("Security requirement: Password must be at least 6 characters.");
            return;
        }

        DOM.loader.classList.add('active');
        try {
            if (isSignup) {
                await auth.createUserWithEmailAndPassword(email, password);
            } else {
                await auth.signInWithEmailAndPassword(email, password);
            }
        } catch (err) {
            console.error("[AUTH ERROR]", err.code, err.message);
            alert(`Authentication Failed: ${err.message}`);
        } finally {
            DOM.loader.classList.remove('active');
        }
    });

    DOM.googleBtn.addEventListener('click', async () => {
        try {
            const provider = new firebase.auth.GoogleAuthProvider();
            await auth.signInWithPopup(provider);
        } catch (err) {
            console.error("Google Login Error:", err);
            alert(err.message);
        }
    });

    DOM.logoutBtn.addEventListener('click', async () => {
        await auth.signOut();
    });

    auth.onAuthStateChanged(async (user) => {
        if (user) {
            currentToken = await user.getIdToken();
            const tokenResult = await user.getIdTokenResult();
            currentRole = tokenResult.claims.role || 'user';
            state.userRole = currentRole;
            
            DOM.loginContainer.style.display = 'none';
            DOM.appContainer.style.display = 'block';
            DOM.userDisplayEmail.innerText = user.email;
            DOM.userDisplayRole.innerText = currentRole;
            
            if (currentRole === 'admin') {
                DOM.userDisplayRole.style.color = 'var(--primary)';
                DOM.adminOnlyBtns.forEach(el => el.style.display = 'flex');
                DOM.simulateBtn.style.display = 'block';
            } else {
                DOM.userDisplayRole.style.color = '#9ca3af';
                DOM.adminOnlyBtns.forEach(el => el.style.display = 'none');
                DOM.simulateBtn.style.display = 'none';
            }

            triggerFullSyncCycle(false);
            
        } else {
            if (syncInterval) clearInterval(syncInterval);
            currentToken = null;
            currentRole = "user";
            DOM.loginContainer.style.display = 'flex';
            DOM.appContainer.style.display = 'none';
        }
    });

});
