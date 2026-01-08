// app.js

const state = {
    fps: 60,
    screen: {
        width: window.innerWidth,
        height: window.innerHeight,
        ratio: window.innerWidth / window.innerHeight
    },
    hardwareTier: "unknown"
};

// 1. Hardware Detection & Benchmark
function runBenchmark() {
    const start = performance.now();
    let count = 0;
    while (performance.now() - start < 100) { // Run for 100ms
        Math.sqrt(Math.random() * 10000);
        count++;
    }
    // Simple heuristic
    if (count > 500000) state.hardwareTier = "high";
    else if (count > 100000) state.hardwareTier = "medium";
    else state.hardwareTier = "low";
    
    updateUIAdaptation();
    sendTelemetry();
}

// 2. Adaptive UI Logic (The "Core Feature")
function updateUIAdaptation() {
    const root = document.documentElement;
    
    // Adjust layout based on screen ratio
    if (state.screen.ratio > 2.0) {
        // Ultra-wide: Scale up text
        root.style.setProperty('--scale-ratio', '1.1');
    } else if (state.screen.ratio < 1.0) {
        // Portrait/Mobile: Compact scale
        root.style.setProperty('--scale-ratio', '0.8');
    }
    
    // Adjust visual fidelity based on hardware tier
    if (state.hardwareTier === "high") {
        root.style.setProperty('--contrast', '110%'); // Pop the colors
        // Enable animations (CSS class toggle could happen here)
    } else {
        root.style.setProperty('--contrast', '100%');
        // Disable heavy effects
    }
    
    document.getElementById('perf-stats').innerText = 
        `HW: ${state.hardwareTier} | Res: ${state.screen.width}x${state.screen.height}`;
}

function sendTelemetry() {
    fetch('/api/client_telemetry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            screen: state.screen,
            fps: state.fps,
            tier: state.hardwareTier
        })
    });
}

// 3. Status Polling
function pollStatus() {
    fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            renderAvatar(data.avatar);
            renderDrives(data.drives);
        });
}

function renderAvatar(visual) {
    if (!visual) return;
    const faceEl = document.getElementById('face');
    // Simple mapping for the web UI (could use SVG later)
    let faceArt = "( - - )";
    if (visual.expression === "happy") faceArt = "( ^ ^ )";
    if (visual.expression === "surprised") faceArt = "( O O )";
    if (visual.expression === "angry") faceArt = "( > < )";
    
    faceEl.innerText = faceArt;
    document.getElementById('mood').innerText = visual.expression.toUpperCase();
}

function renderDrives(drives) {
    const container = document.getElementById('drives-list');
    container.innerHTML = '';
    
    for (const [name, value] of Object.entries(drives)) {
        const div = document.createElement('div');
        div.className = 'bar-container';
        div.innerHTML = `
            <div>${name}: ${(value * 100).toFixed(0)}%</div>
            <div class="bar">
                <div class="fill" style="width: ${value * 100}%"></div>
            </div>
        `;
        container.appendChild(div);
    }
}

// Init
window.addEventListener('resize', () => {
    state.screen.width = window.innerWidth;
    state.screen.height = window.innerHeight;
    state.screen.ratio = window.innerWidth / window.innerHeight;
    updateUIAdaptation();
});

runBenchmark();
setInterval(pollStatus, 1000);
