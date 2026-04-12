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
const db = firebase.firestore();

let currentToken = null;
let currentRole = "user";

document.addEventListener('DOMContentLoaded', () => {
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
        systemStatusText: document.getElementById('systemStatusText')
    };

    let syncInterval = null;
    let activeView = "dashboard";

    // SPA Routing Logic
    const views = document.querySelectorAll('.view-section');
    const navBtns = document.querySelectorAll('.nav-btn');

    const navigateTo = (target) => {
        // Change UI Title dynamically mapped securely without library overhead
        const titleMap = {
            'dashboard': 'Live Dashboard',
            'analytics': 'Topology Analytics',
            'alerts': 'Serious Alerts',
            'insights': 'Intelligence Panel',
            'environment': 'Cloud Environment',
            'controls': 'System Controls'
        };
        DOM.viewTitle.innerText = titleMap[target] || 'Dashboard';
        
        // Hide all views cleanly, toggle structural classes native DOM arrays
        views.forEach(v => v.classList.remove('active'));
        document.getElementById(`view-${target}`).classList.add('active');

        // Toggle strict UI navigation buttons cleanly bounding UX parameters
        navBtns.forEach(btn => btn.classList.remove('active'));
        document.querySelector(`.nav-btn[data-target="${target}"]`).classList.add('active');
        
        activeView = target;
        // Dynamic Route handling gracefully enforcing isolated API renders
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

    // View Renderers Matrix
    const renderDashboard = (zones) => {
        DOM.zones.innerHTML = zones.map(z => {
            const colorParam = getStateColor(z.density);
            return `
                <div class="zone-card" style="--state-color: ${colorParam};">
                    <div class="zone-header">
                        <div class="zone-name">${z.zone}</div>
                        ${getTrendIcon(z.trend)}
                    </div>
                    <div class="zone-metrics">
                        <div class="density-ring" style="--density: ${z.density}">
                            <div class="density-value">${z.density}%</div>
                        </div>
                        <div class="zone-details">
                            <div class="status-badge" style="box-shadow: 0 0 10px ${colorParam}40">${z.status}</div>
                            <div class="timestamp">SYNC: ${formatTime(z.timestamp)}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    };

    const renderAnalytics = (zones) => {
        // Native sort algorithms natively extracting highest density threat mappings down cleanly
        const sorted = [...zones].sort((a,b) => b.density - a.density);
        DOM.analytics.innerHTML = sorted.map(z => `
            <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 15px 20px; display: flex; align-items:center; justify-content:space-between;">
                <div style="font-size: 1.1rem; font-weight: 600;">${z.zone}</div>
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
            <div class="alert-item alert-${a.level}">
                <div style="font-weight: 700; margin-bottom: 5px; color: white;">⚠️ ${a.zone} [${a.level.toUpperCase()}]</div>
                <div style="color: rgba(255,255,255,0.8);">${a.message}</div>
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
                <div style="font-weight: 700; font-size: 1.1rem; color: white; margin-bottom: 6px;">🎯 ${r.action}</div>
                <div style="color: rgba(255,255,255,0.7); font-size: 0.95rem;">REASON INTEGRITY: ${r.reason}</div>
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

    const fetchViewData = async (target) => {
        if (!currentToken) return;
        DOM.loader.classList.add('active');
        try {
            const evt = DOM.eventTypeToggle.value;
            const params = `?event=${evt}`;
            const headers = { "Authorization": `Bearer ${currentToken}` };
            
            // Map target to API domain logically mapped
            let domain = target;
            if (target === 'dashboard' || target === 'analytics') domain = 'crowd';
            if (target === 'controls') return; // Native controls, no dynamic fetch required
            
            const res = await fetch(`${API_BASE}/${domain}${params}`, { headers });
            if (res.status === 401 || res.status === 403) throw new Error("Unauthorized");
            const data = await res.json();
            
            if (data.status === 'idle') {
                DOM.zones.innerHTML = '<div style="color:var(--safe)">System Idle. Waiting for Admin activation.</div>';
                DOM.analytics.innerHTML = '';
                DOM.insights.innerHTML = '';
                DOM.alerts.innerHTML = '';
                DOM.envGrid.innerHTML = '';
                return;
            }
            
            // Strictly enforce isolated state slices
            if (domain === 'crowd') {
                state.crowd = data;
                if (target === 'dashboard') renderDashboard(state.crowd);
                if (target === 'analytics') renderAnalytics(state.crowd);
            } else if (domain === 'insights') {
                state.insights = data;
                renderInsights(state.insights.recommendations || []);
            } else if (domain === 'alerts') {
                state.alerts = data;
                renderAlerts(state.alerts);
            } else if (domain === 'environment') {
                state.environment = data;
                renderEnvironment(state.environment);
            }
        } catch (err) {
            console.error(`Isolated tab fetch error for ${target}:`, err);
        } finally {
            DOM.loader.classList.remove('active');
        }
    };

    const renderEnvironment = (envData) => {
        if (envData && envData.event_phase) {
            DOM.envGrid.innerHTML = `
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 5px;">Active Event Phase Boundary</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: white;">${envData.event_phase}</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 5px;">Meteorological Structural Conditions</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: white;">${envData.weather_condition}</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 5px;">Thermal Sensors</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: var(--warning);">${envData.temperature_celsius}°C</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 5px;">Moisture / Air Integrity</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: var(--empty);">${envData.humidity_percent}%</div>
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
                const evt = DOM.eventTypeToggle.value;
                const params = `?event=${evt}`;
                const headers = { "Authorization": `Bearer ${currentToken}` };
                await fetch(`${API_BASE}/simulate${params}`, { headers }).catch(e => console.warn("API Simulate Hook Error.", e));
            } catch (error) {}
        }

        // Delegate exclusively to Active View to permanently prevent cross-tab state overwrites and flickering
        await fetchViewData(activeView);
    };

    // Attach Interactivity
    DOM.simulateBtn.addEventListener('click', () => triggerFullSyncCycle(true));
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

    if (DOM.adminStartSystemBtn) {
        DOM.adminStartSystemBtn.addEventListener('click', async () => {
            if (!currentToken) return;
            DOM.loader.classList.add('active');
            try {
                const evt = DOM.eventTypeToggle.value;
                const res = await fetch(`${API_BASE}/admin/system/start?event_type=${evt}`, {
                    method: "POST",
                    headers: { "Authorization": `Bearer ${currentToken}` }
                });
                if (res.ok) {
                    DOM.systemStatusIndicator.style.background = 'var(--safe)';
                    DOM.systemStatusText.innerText = 'ACTIVE';
                    DOM.systemStatusText.style.color = 'var(--safe)';
                    
                    // Enable Live Sync functionality seamlessly
                    DOM.autoToggle.checked = true;
                    DOM.autoToggle.dispatchEvent(new Event('change'));
                } else {
                    alert("Failed to start system. Token validation rejected.");
                }
            } catch (e) {
                console.error(e);
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
                const res = await fetch(`${API_BASE}/admin/system/stop`, {
                    method: "POST",
                    headers: { "Authorization": `Bearer ${currentToken}` }
                });
                if (res.ok) {
                    DOM.systemStatusIndicator.style.background = '#666';
                    DOM.systemStatusText.innerText = 'IDLE';
                    DOM.systemStatusText.style.color = 'var(--text-muted)';
                    
                    // Disable Live Sync gracefully
                    DOM.autoToggle.checked = false;
                    DOM.autoToggle.dispatchEvent(new Event('change'));
                } else {
                    alert("Failed to stop system cleanly.");
                }
            } catch (e) {
                console.error(e);
            } finally {
                DOM.loader.classList.remove('active');
            }
        });
    }

    // ----------------------------------------------------
    // Authentication & Role Logic Systematically Intercepted
    // ----------------------------------------------------
    let isSignup = false;
    DOM.authToggle.addEventListener('click', () => {
        isSignup = !isSignup;
        DOM.authTitle.innerText = isSignup ? 'Create Account' : 'Welcome Back';
        DOM.authSubmitBtn.innerText = isSignup ? 'Sign Up' : 'Sign In';
        DOM.authToggle.innerText = isSignup ? 'Already have an account? Sign in' : 'Need an account? Sign up';
    });

    DOM.authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = DOM.authEmail.value;
        const password = DOM.authPassword.value;
        try {
            if (isSignup) {
                await auth.createUserWithEmailAndPassword(email, password);
            } else {
                await auth.signInWithEmailAndPassword(email, password);
            }
        } catch (err) {
            console.error("Auth Error:", err);
            alert(err.message);
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

    // Handle Auth States natively blocking arrays securely
    auth.onAuthStateChanged(async (user) => {
        if (user) {
            // Retrieve JWT for Backend Execution
            currentToken = await user.getIdToken();
            DOM.loginContainer.style.display = 'none';
            DOM.appContainer.style.display = 'block';
            
            // Map UI dynamically
            DOM.userDisplayEmail.innerText = user.email;
            
            // Manage Structural Roles
            const userDocRef = db.collection('users').doc(user.uid);
            let userDoc = await userDocRef.get();
            
            if (!userDoc.exists) {
                const ADMIN_EMAIL = "bhardwajparth185@gmail.com";
                const assignedRole = (user.email === ADMIN_EMAIL) ? 'admin' : 'user';
                
                await userDocRef.set({
                    uid: user.uid,
                    email: user.email,
                    role: assignedRole,
                    created_at: firebase.firestore.FieldValue.serverTimestamp()
                });
                
                currentRole = assignedRole;
            } else {
                currentRole = userDoc.data().role || 'user';
            }
            
            DOM.userDisplayRole.innerText = currentRole;
            if (currentRole === 'admin') {
                DOM.userDisplayRole.style.background = 'rgba(234, 179, 8, 0.2)';
                DOM.userDisplayRole.style.color = 'var(--caution)';
                DOM.adminOnlyBtns.forEach(el => el.style.display = 'flex');
                DOM.simulateBtn.style.display = 'block';
            } else {
                DOM.userDisplayRole.style.background = 'rgba(255,255,255,0.1)';
                DOM.userDisplayRole.style.color = 'white';
                DOM.adminOnlyBtns.forEach(el => el.style.display = 'none');
                DOM.simulateBtn.style.display = 'none';
            }

            // Immediately Trigger execution bounds cleanly now authorized!
            triggerFullSyncCycle(false);
        } else {
            // Reset to Login State seamlessly dropping arrays avoiding stale ghosts
            if (syncInterval) clearInterval(syncInterval);
            currentToken = null;
            currentRole = "user";
            DOM.loginContainer.style.display = 'flex';
            DOM.appContainer.style.display = 'none';
        }
    });

});
