// Global variables
let visitData = {};
let visitTracked = false;
const API_BASE = 'http://localhost:3000/api';

// Function to detect detailed browser information
function getBrowserInfo() {
    const userAgent = navigator.userAgent;
    let browserName = 'Unknown Browser';
    
    if (userAgent.indexOf('Edg') !== -1) {
        browserName = 'Microsoft Edge';
    } else if (userAgent.indexOf('OPR') !== -1 || userAgent.indexOf('Opera') !== -1) {
        browserName = 'Opera';
    } else if (userAgent.indexOf('Chrome') !== -1 && userAgent.indexOf('Edg') === -1) {
        browserName = 'Google Chrome';
    } else if (userAgent.indexOf('Firefox') !== -1) {
        browserName = 'Mozilla Firefox';
    } else if (userAgent.indexOf('Safari') !== -1 && userAgent.indexOf('Chrome') === -1) {
        browserName = 'Safari';
    }
    
    return browserName;
}

// Function to detect detailed OS information
function getOSInfo() {
    const userAgent = navigator.userAgent;
    let osName = 'Unknown OS';
    
    if (userAgent.indexOf('Android') !== -1) {
        osName = 'Android';
    } else if (userAgent.indexOf('iPhone') !== -1 || userAgent.indexOf('iPad') !== -1) {
        osName = 'iOS';
    } else if (userAgent.indexOf('Windows NT') !== -1) {
        osName = 'Windows';
    } else if (userAgent.indexOf('Mac OS X') !== -1) {
        osName = 'macOS';
    } else if (userAgent.indexOf('Linux') !== -1) {
        osName = 'Linux';
    }
    
    return osName;
}

// Function to get timezone information
function getTimezoneInfo() {
    try {
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const offset = new Date().getTimezoneOffset();
        const offsetHours = Math.floor(Math.abs(offset) / 60);
        const offsetMinutes = Math.abs(offset) % 60;
        const offsetSign = offset <= 0 ? '+' : '-';
        const offsetString = `UTC${offsetSign}${offsetHours.toString().padStart(2, '0')}:${offsetMinutes.toString().padStart(2, '0')}`;
        
        return `${timezone} (${offsetString})`;
    } catch (error) {
        return 'Unknown Timezone';
    }
}

// Function to capture all visit data
function captureVisitData() {
    const now = new Date();
    
    visitData = {
        datetime: now.toISOString(),
        os: getOSInfo(),
        browser: getBrowserInfo(),
        screen_resolution: `${screen.width}x${screen.height}`,
        user_agent: navigator.userAgent,
        url: window.location.href,
        timezone: getTimezoneInfo(),
        timestamp_local: now.toLocaleString(),
        language: navigator.language || navigator.userLanguage,
        platform: navigator.platform
    };
    
    return visitData;
}

// Function to update the UI with captured data
function updateUI(data) {
    document.getElementById('datetime').textContent = data.timestamp_local;
    document.getElementById('timezone').textContent = data.timezone;
    document.getElementById('page-url').textContent = data.url;
    document.getElementById('os-info').textContent = data.os;
    document.getElementById('browser-info').textContent = data.browser;
    document.getElementById('screen-info').textContent = data.screen_resolution;
}

// Function to send data to backend
async function sendToBackend(data) {
    try {
        const response = await fetch(`${API_BASE}/track`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Update status to success
        const statusElement = document.getElementById('status');
        statusElement.innerHTML = `
            <span>✅</span>
            <span>Visit tracked successfully! (Visit ID: ${result.visit_id})</span>
        `;
        statusElement.className = 'status success';
        
        console.log('Visit tracked successfully:', result);
        
        // Load recent visits after tracking
        await loadRecentVisits();
        
        return result;
        
    } catch (error) {
        console.error('Error sending data to backend:', error);
        
        // Update status to error
        const statusElement = document.getElementById('status');
        statusElement.innerHTML = `
            <span>❌</span>
            <span>Error tracking visit: ${error.message}</span>
        `;
        statusElement.className = 'status error';
        
        throw error;
    }
}

// Function to load recent visits
async function loadRecentVisits() {
    const container = document.getElementById('visits-container');
    try {
        const response = await fetch(`${API_BASE}/visits`);
        if (!response.ok) throw new Error("API request failed");
        const data = await response.json();
        if (data.visits && data.visits.length > 0) {
            container.innerHTML =
              `<table>
                <thead>
                  <tr>
                    <th>ID</th><th>Timestamp</th><th>Browser</th>
                    <th>OS</th><th>Screen</th><th>IP</th>
                  </tr>
                </thead>
                <tbody>
                  ${data.visits.map(v => `<tr>
                    <td>${v.id}</td>
                    <td>${new Date(v.timestamp).toLocaleString()}</td>
                    <td>${v.browser}</td>
                    <td>${v.os}</td>
                    <td>${v.screen_resolution || "N/A"}</td>
                    <td>${v.ip_address}</td>
                  </tr>`).join("")}
                </tbody>
              </table>`;
        } else {
            container.textContent = "No visits found.";
        }
    } catch (error) {
        container.textContent = "❌ Failed to fetch recent visits: " + error.message;
    }
}
// Main function to execute when page loads
async function initializeTracking() {
    try {
        // Capture visit data
        const data = captureVisitData();
        
        // Update UI immediately
        updateUI(data);
        
        // Send to backend
        await sendToBackend(data);
        
    } catch (error) {
        console.error('Error during initialization:', error);
        
        const statusElement = document.getElementById('status');
        statusElement.innerHTML = `
            <span>❌</span>
            <span>Initialization error: ${error.message}</span>
        `;
        statusElement.className = 'status error';
    }
}

// Execute when page loads
window.addEventListener('load', initializeTracking);

// Also execute when DOM is ready (fallback)
// Modify the main initialization
document.addEventListener('DOMContentLoaded', async function() {
    if (visitTracked) return; // Prevent duplicate tracking
    
    try {
        console.log('🔍 Starting visit tracking...');
        
        // Capture visit data
        const data = captureVisitData();
        
        // Update UI first
        updateUI(data);
        
        // Send to backend only once
        await sendToBackend(data);
        visitTracked = true; // Set flag after successful tracking
        
    } catch (error) {
        console.error('❌ Error during initialization:', error);
        const statusElement = document.getElementById('status');
        if (statusElement) {
            statusElement.textContent = `❌ Initialization error: ${error.message}`;
            statusElement.className = 'status error';
        }
    }
});
