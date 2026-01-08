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

// Canvas Map
const canvas = document.getElementById('world-map');
const ctx = canvas.getContext('2d');
let worldState = null;

// Chat
const input = document.getElementById('cmd-input');
const history = document.getElementById('chat-history');

// --- 1. Interaction ---

function sendCommand() {
    const text = input.value.trim();
    if (!text) return;

    addMessage('user', text);
    input.value = '';

    fetch('/api/interact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: text })
    })
    .then(res => res.json())
    .then(data => {
        addMessage('daemon', data.response);
    })
    .catch(err => {
        addMessage('daemon', 'Error: ' + err);
    });
}

function addMessage(role, text) {
    const div = document.createElement('div');
    div.className = `msg ${role}`;
    const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
    div.innerHTML = `<span class="timestamp">${time}</span> ${text}`;
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;
}

input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendCommand();
});
document.getElementById('send-btn').addEventListener('click', sendCommand);

// --- 2. Map Rendering ---

function resizeCanvas() {
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth;
    canvas.height = parent.clientHeight;
}
window.addEventListener('resize', resizeCanvas);

function drawMap() {
    if (!worldState || !worldState.locations) return;
    
    // Clear
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Simple layout algorithm: distribute locations in a circle for visual clarity
    // In a real game, they'd have X/Y coordinates in properties
    
    const locIds = Object.keys(worldState.locations);
    const count = locIds.length;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const radius = Math.min(cx, cy) * 0.7;
    
    const positions = {};
    
    // Draw Locations
    locIds.forEach((id, i) => {
        const angle = (i / count) * Math.PI * 2;
        const x = cx + Math.cos(angle) * radius;
        const y = cy + Math.sin(angle) * radius;
        positions[id] = {x, y};
        
        ctx.fillStyle = '#0a0';
        ctx.beginPath();
        ctx.arc(x, y, 20, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#0f0';
        ctx.stroke();
        
        // Label
        ctx.fillStyle = '#fff';
        ctx.font = '10px monospace';
        ctx.textAlign = 'center';
        const name = worldState.locations[id].name;
        ctx.fillText(name.substring(0, 15), x, y + 35);
    });
    
    // Draw Connections (Linearly linked in our generator)
    ctx.strokeStyle = '#050';
    ctx.lineWidth = 2;
    Object.values(worldState.locations).forEach(loc => {
        const p1 = positions[loc.id];
        loc.connected_location_ids.forEach(targetId => {
             const p2 = positions[targetId];
             if (p1 && p2) {
                 ctx.beginPath();
                 ctx.moveTo(p1.x, p1.y);
                 ctx.lineTo(p2.x, p2.y);
                 ctx.stroke();
             }
        });
    });

    // Draw Entities
    Object.values(worldState.entities).forEach(ent => {
        if (ent.location_id && positions[ent.location_id]) {
            const loc = positions[ent.location_id];
            // Jitter position slightly so they don't stack perfectly
            // Use ID hash for deterministic jitter
            const jitterX = (ent.id.charCodeAt(0) % 20) - 10;
            const jitterY = (ent.id.charCodeAt(1) % 20) - 10;
            
            ctx.fillStyle = '#f0f';
            ctx.beginPath();
            ctx.arc(loc.x + jitterX, loc.y + jitterY, 5, 0, Math.PI * 2);
            ctx.fill();
        }
    });
}

// --- 3. Core Loop & Polling ---

function pollStatus() {
    fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            renderAvatar(data.avatar);
            renderDrives(data.drives);
            worldState = data.world;
            drawMap();
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
    if (visual.sub_state === "blink") faceArt = "( - - )";
    
    faceEl.innerText = faceArt;
    document.getElementById('mood').innerText = visual.expression.toUpperCase();
}

function renderDrives(drives) {
    const container = document.getElementById('drives-list');
    container.innerHTML = '';
    
    for (const [name, value] of Object.entries(drives)) {
        // Determine color based on urgency
        let color = '#0f0';
        if (value < 0.3) color = '#f00'; // Critical
        else if (value < 0.6) color = '#ff0'; // Warning
        
        const div = document.createElement('div');
        div.className = 'bar-container';
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between;">
                <span>${name}</span>
                <span>${(value * 100).toFixed(0)}%</span>
            </div>
            <div class="bar">
                <div class="fill" style="width: ${value * 100}%; background-color: ${color};"></div>
            </div>
        `;
        container.appendChild(div);
    }
}

// Hardware Adaptation Logic (from previous step)
function runBenchmark() {
    const start = performance.now();
    let count = 0;
    while (performance.now() - start < 100) { Math.sqrt(Math.random()); count++; }
    if (count > 500000) state.hardwareTier = "high";
    else if (count > 100000) state.hardwareTier = "medium";
    else state.hardwareTier = "low";
    updateUIAdaptation();
}

function updateUIAdaptation() {
    const root = document.documentElement;
    if (state.screen.ratio > 2.0) root.style.setProperty('--scale-ratio', '1.05');
    else if (state.screen.ratio < 1.0) root.style.setProperty('--scale-ratio', '0.8');
    
    if (state.hardwareTier === "high") root.style.setProperty('--contrast', '110%');
    
    document.getElementById('perf-stats').innerText = 
        `HW: ${state.hardwareTier.toUpperCase()} | Res: ${state.screen.width}x${state.screen.height}`;
}

// Init
resizeCanvas();
runBenchmark();
setInterval(pollStatus, 1000);
