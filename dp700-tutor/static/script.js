// --- THREE.JS QUANTUM FIELD ---
let scene, camera, renderer, crystal;
const canvas = document.getElementById('three-canvas');

function initThree() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    
    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Create Cosmic Crystal (Icosahedron)
    const geometry = new THREE.IcosahedronGeometry(2, 0);
    const material = new THREE.MeshPhongMaterial({
        color: 0x6366f1,
        wireframe: true,
        transparent: true,
        opacity: 0.3,
        emissive: 0x6366f1,
        emissiveIntensity: 0.5
    });
    crystal = new THREE.Mesh(geometry, material);
    scene.add(crystal);

    // Add Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0xa855f7, 2);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    camera.position.z = 10;
}

function animateThree() {
    requestAnimationFrame(animateThree);
    crystal.rotation.x += 0.005;
    crystal.rotation.y += 0.005;
    renderer.render(scene, camera);
}

// --- 3D MOUSE PARALLAX ---
const cards = document.querySelectorAll('.3d-card');
document.addEventListener('mousemove', (e) => {
    const x = (window.innerWidth / 2 - e.pageX) / 40;
    const y = (window.innerHeight / 2 - e.pageY) / 40;
    
    cards.forEach(card => {
        card.style.transform = `rotateY(${x}deg) rotateX(${-y}deg)`;
    });

    // Move camera slightly
    if(camera) {
        camera.position.x += (x/10 - camera.position.x) * 0.05;
        camera.position.y += (-y/10 - camera.position.y) * 0.05;
    }
});

// --- CORE LOGIC ---
const chatWindow = document.getElementById('chatWindow');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const langSelect = document.getElementById('langSelect');
const voiceToggle = document.getElementById('voiceToggle');
const tutorName = document.getElementById('tutorName');
const genVisualBtn = document.getElementById('genVisualBtn');

let voiceEnabled = true;

function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    voiceToggle.querySelector('.v-status').innerText = voiceEnabled ? 'Neural Voice ON' : 'Neural Voice OFF';
    gsap.fromTo(voiceToggle, {scale: 0.9}, {scale: 1, duration: 0.3, ease: "elastic.out(1, 0.3)"});
}

langSelect.addEventListener('change', () => {
    const lang = langSelect.value;
    const names = {
        'en': 'Grand Master | Fabric Guru',
        'te': 'గ్రాండ్ మాస్టర్ | ఫాబ్రిక్ గురు',
        'hi': 'ग्रैंड मास्टर | फैब्रिक गुरु',
        'ta': 'கிராண்ட் మాస్టర్ | பேப்ரிக் குரு'
    };
    tutorName.innerText = names[lang] || names['en'];
});

function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    const contentDiv = document.createElement('div');
    contentDiv.className = 'msg-content';
    contentDiv.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    msgDiv.appendChild(contentDiv);
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // GSAP Entrance
    gsap.from(msgDiv, {
        y: 30,
        opacity: 0,
        rotateX: -20,
        duration: 0.6,
        ease: "power3.out"
    });

    return msgDiv;
}

async function askQuestion() {
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    userInput.value = '';
    
    const lang = langSelect.value;
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, lang })
    });

    const reader = response.body.getReader();
    const assistantMsg = addMessage('', 'assistant');
    const contentDiv = assistantMsg.querySelector('.msg-content');
    
    let fullText = "";
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                if (data.content) {
                    fullText += data.content;
                    contentDiv.innerHTML = fullText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                }
            }
        }
    }

    if (voiceEnabled) speak(fullText, lang);
}

async function speak(text, lang) {
    const response = await fetch('/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, lang })
    });
    const data = await response.json();
    if (data.audio) {
        const audio = new Audio(`data:audio/mp3;base64,${data.audio}`);
        audio.play();
    }
}

async function generateVisual() {
    const prompt = userInput.value.trim();
    if (!prompt) return addMessage('Please provide a visual description first!', 'assistant');

    addMessage(`Generating visual for: "${prompt}"...`, 'user');
    userInput.value = '';
    
    try {
        const response = await fetch('/generate_visual', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, type: 'image' })
        });
        const data = await response.json();
        
        if (data.image) {
            const assistantMsg = addMessage('Neural Visual Generated:', 'assistant');
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${data.image}`;
            img.style.width = '100%';
            img.style.borderRadius = '15px';
            img.style.marginTop = '10px';
            img.style.cursor = 'pointer';
            img.onclick = () => showConcept(img.src, 'N^th Dimension Neural Visual');
            assistantMsg.appendChild(img);
        } else {
            addMessage(`Visual Link Failed: ${data.error}`, 'assistant');
        }
    } catch (err) {
        addMessage('Critical Error in Visual Synthesis.', 'assistant');
    }
}

// Modal
const modal = document.getElementById('imageModal');
const modalImg = document.getElementById('modalImg');
const captionText = document.getElementById('caption');

function showConcept(src, title) {
    modal.style.display = "block";
    modalImg.src = src;
    captionText.innerHTML = title;
}

function closeModal() {
    modal.style.display = "none";
}

// Listeners
sendBtn.addEventListener('click', askQuestion);
genVisualBtn.addEventListener('click', generateVisual);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') askQuestion(); });

// Initialize
window.onload = () => {
    initThree();
    animateThree();
    
    // Intro Animation
    gsap.from(".sidebar", { x: -100, opacity: 0, duration: 1.5, ease: "power4.out" });
    gsap.from(".main-content", { x: 100, opacity: 0, duration: 1.5, ease: "power4.out" });
};

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
