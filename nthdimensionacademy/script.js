document.addEventListener('DOMContentLoaded', () => {
    // Custom Cursor Glow Effect
    const cursorGlow = document.querySelector('.cursor-glow');
    
    document.addEventListener('mousemove', (e) => {
        requestAnimationFrame(() => {
            cursorGlow.style.left = `${e.clientX}px`;
            cursorGlow.style.top = `${e.clientY}px`;
        });
    });

    // Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Reveal Animations on Scroll
    const revealElements = document.querySelectorAll('.reveal');

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        const elementVisible = 100;

        revealElements.forEach((element) => {
            const elementTop = element.getBoundingClientRect().top;
            if (elementTop < windowHeight - elementVisible) {
                element.classList.add('active');
            }
        });
    };

    // Initial check
    revealOnScroll();
    
    // Check on scroll
    window.addEventListener('scroll', revealOnScroll);

    // Holographic Tilt Effect for Cards
    const tiltCards = document.querySelectorAll('.stat-card, .glass-card');
    tiltCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px) scale(1.02)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0) scale(1)';
        });
    });

    // Smooth Scrolling for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if(targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // 3D Knowledge Graph Initialization
    const graphContainer = document.getElementById('3d-graph-container');
    if (graphContainer && typeof ForceGraph3D !== 'undefined') {
        const graphData = {
            nodes: [
                // Core
                { id: 'MCT', group: 1, val: 25, name: 'Microsoft Certified Trainer (MCT)' },
                
                // Ecosystems & Platforms
                { id: 'Azure Data Ecosystem', group: 2, val: 18, name: 'Azure Data Ecosystem' },
                { id: 'Microsoft Fabric', group: 3, val: 20, name: 'Microsoft Fabric' },
                { id: 'Azure Databricks', group: 3, val: 18, name: 'Azure Databricks' },
                { id: 'Power BI', group: 6, val: 18, name: 'Power BI Ecosystem' },
                
                // Architecture & Concepts
                { id: 'Medallion Architecture', group: 4, val: 15, name: 'Medallion Architecture' },
                { id: 'Lakehouse', group: 4, val: 12, name: 'Lakehouse Pattern' },
                { id: 'Data Mesh', group: 4, val: 12, name: 'Data Mesh Strategy' },
                
                // Certifications
                { id: 'DP-600', group: 5, val: 15, name: 'DP-600: Fabric Analytics' },
                { id: 'DP-203', group: 5, val: 15, name: 'DP-203: Azure Data Engineer' },
                { id: 'DP-900', group: 5, val: 10, name: 'DP-900: Data Fundamentals' },
                
                // Specific Technologies & Modules
                { id: 'ADLS Gen2', group: 2, val: 10, name: 'ADLS Gen2 Storage' },
                { id: 'Event Hub', group: 2, val: 10, name: 'Azure Event Hubs' },
                { id: 'Key Vault', group: 2, val: 8, name: 'Azure Key Vault' },
                { id: 'PySpark', group: 3, val: 12, name: 'PySpark / Spark SQL' },
                { id: 'Delta Lake', group: 4, val: 12, name: 'Delta Lake Tables' },
                { id: 'DAX', group: 6, val: 10, name: 'DAX Optimization' },
                { id: 'Alteryx', group: 7, val: 12, name: 'Alteryx Workflows' },
                { id: 'Python Automation', group: 7, val: 14, name: 'Python Automation' },
                { id: 'Global Enterprise Cohorts', group: 8, val: 16, name: 'Global Enterprise Upskilling' }
            ],
            links: [
                { source: 'MCT', target: 'Azure Data Ecosystem' },
                { source: 'MCT', target: 'Microsoft Fabric' },
                { source: 'MCT', target: 'DP-600' },
                { source: 'MCT', target: 'DP-203' },
                { source: 'MCT', target: 'DP-900' },
                { source: 'MCT', target: 'Global Enterprise Cohorts' },
                
                { source: 'Azure Data Ecosystem', target: 'Azure Databricks' },
                { source: 'Azure Data Ecosystem', target: 'ADLS Gen2' },
                { source: 'Azure Data Ecosystem', target: 'Event Hub' },
                { source: 'Azure Data Ecosystem', target: 'Key Vault' },
                
                { source: 'Microsoft Fabric', target: 'Medallion Architecture' },
                { source: 'Microsoft Fabric', target: 'Lakehouse' },
                { source: 'Microsoft Fabric', target: 'Power BI' },
                { source: 'Microsoft Fabric', target: 'DP-600' },
                
                { source: 'Azure Databricks', target: 'Medallion Architecture' },
                { source: 'Azure Databricks', target: 'PySpark' },
                { source: 'Azure Databricks', target: 'Delta Lake' },
                
                { source: 'Lakehouse', target: 'Delta Lake' },
                { source: 'Medallion Architecture', target: 'Data Mesh' },
                
                { source: 'Power BI', target: 'DAX' },
                { source: 'Power BI', target: 'Alteryx' }, // Showing data prep connection
                
                { source: 'Python Automation', target: 'Alteryx' },
                { source: 'Python Automation', target: 'Azure Databricks' },
                
                { source: 'DP-203', target: 'Azure Data Ecosystem' },
                { source: 'DP-900', target: 'Global Enterprise Cohorts' },
                { source: 'DP-600', target: 'Global Enterprise Cohorts' },
                { source: 'DP-203', target: 'Global Enterprise Cohorts' }
            ]
        };

        // Color palette matching the Cosmic Gold / Neon Blue theme
        const groupColors = {
            1: '#FFD700', // Cosmic Gold (MCT)
            2: '#00F3FF', // Neon Blue (Azure)
            3: '#8A2BE2', // Deep Purple (Fabric/Databricks)
            4: '#00FA9A', // Spring Green (Architecture)
            5: '#FF8C00', // Dark Orange (Certifications)
            6: '#F0E68C', // Khaki (Power BI)
            7: '#FF1493', // Deep Pink (Automation)
            8: '#FFF8DC'  // Cornsilk (Global Cohorts)
        };

        const Graph = ForceGraph3D()(graphContainer)
            .graphData(graphData)
            .nodeLabel('name')
            .nodeColor(node => groupColors[node.group] || '#ffffff')
            .nodeRelSize(6)
            .linkColor(link => {
                const sourceGroup = typeof link.source === 'object' ? link.source.group : graphData.nodes.find(n => n.id === link.source).group;
                return groupColors[sourceGroup] + '80'; // Add 50% opacity (80 in hex)
            })
            .linkWidth(1.5)
            .linkDirectionalParticles(2)
            .linkDirectionalParticleSpeed(0.005)
            .linkDirectionalParticleWidth(2.5)
            .linkOpacity(0.4)
            .backgroundColor('rgba(0,0,0,0)') // Transparent background
            .onNodeHover(node => graphContainer.style.cursor = node ? 'pointer' : null);

        // Auto-rotate
        let angle = 0;
        setInterval(() => {
            Graph.cameraPosition({
                x: 200 * Math.sin(angle),
                z: 200 * Math.cos(angle)
            });
            angle += Math.PI / 400; // slightly slower rotation for complex graph
        }, 30);

        // Resize handler
        window.addEventListener('resize', () => {
            Graph.width(graphContainer.clientWidth);
            Graph.height(graphContainer.clientHeight);
        });

        // Link Graph Node Clicks to AI Assistant
        Graph.onNodeClick(node => {
            openAssistant();
            const prompt = `Tell me more about ${node.name}. What is its role in Microsoft Fabric and the Nth Dimension?`;
            addMessage('user', prompt);
            callNIM(prompt);
        });
    }

    // AI Assistant Logic
    const aiAssistant = document.getElementById('ai-assistant');
    const openBtn = document.getElementById('open-assistant');
    const closeBtn = document.getElementById('close-assistant');
    const sendBtn = document.getElementById('send-msg');
    const voiceBtn = document.getElementById('voice-msg');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    let chatHistory = [];

    const openAssistant = () => {
        aiAssistant.classList.remove('hidden');
        openBtn.style.display = 'none';
    };

    const closeAssistant = () => {
        aiAssistant.classList.add('hidden');
        openBtn.style.display = 'flex';
    };

    const addMessage = (role, text) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.innerHTML = `<p>${text}</p>`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const callNIM = async (text) => {
        try {
            // Show Thinking state
            const thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'message system thinking';
            thinkingDiv.innerHTML = '<p><i class="ph ph-sparkle"></i> The Guide is consulting the Nth Dimension...</p>';
            chatMessages.appendChild(thinkingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, history: chatHistory })
            });
            
            // Remove Thinking state
            thinkingDiv.remove();

            const data = await response.json();
            
            // Parse for Actions
            const actionMatch = data.response.match(/\[ACTION:(.*?)\]/);
            if (actionMatch) {
                const action = actionMatch[1];
                handleUIAction(action);
                const cleanResponse = data.response.replace(/\[ACTION:.*?\]/g, '').trim();
                addMessage('system', cleanResponse);
            } else {
                addMessage('system', data.response);
            }

            chatHistory.push({ role: 'user', content: text });
            chatHistory.push({ role: 'assistant', content: data.response });
        } catch (error) {
            console.error('NIM Error:', error);
            const thinking = chatMessages.querySelector('.thinking');
            if(thinking) thinking.remove();
            addMessage('system', "Apologies, Voyager. The dimensional link is unstable. Please ensure the backend is running.");
        }
    };

    const handleUIAction = (action) => {
        console.log("Triggering Action:", action);
        switch(action) {
            case 'SCROLL_TO_EXPERTISE':
                document.getElementById('expertise').scrollIntoView({ behavior: 'smooth' });
                break;
            case 'SCROLL_TO_FABRIC':
            case 'PLAY_VIDEO_FABRIC':
                document.getElementById('fabric-demo').scrollIntoView({ behavior: 'smooth' });
                // Add highlight effect
                document.querySelector('.demo-container').classList.add('neon-pulse');
                setTimeout(() => document.querySelector('.demo-container').classList.remove('neon-pulse'), 3000);
                break;
            case 'BOOK_MEETING':
                window.open('mailto:navkanthr@gmail.com?subject=Inquiry from Nth Dimension Academy', '_blank');
                break;
            default:
                console.warn("Unknown action:", action);
        }
    };

    window.triggerFabricDemo = () => {
        const video = document.getElementById('fabric-video-player');
        const overlay = document.getElementById('demo-overlay');
        
        if (video) {
            overlay.style.display = 'none';
            video.play();
            video.controls = true;
        }

        openAssistant();
        addMessage('system', "Initiating N<span class='nth-style'>TH</span> Dimension Fabric Demo Masterclass... Observe the convergence of data streams.");
        const demoPrompt = "I am watching the Microsoft Fabric Demo. Explain the key architectural components being shown and how they align with the NTH Dimension.";
        addMessage('user', "Launch the Fabric Demo.");
        callNIM(demoPrompt);
        
        const demoContainer = document.querySelector('.demo-container');
        demoContainer.classList.add('neon-pulse');
        setTimeout(() => demoContainer.classList.remove('neon-pulse'), 5000);
    };

    const synthesizeVoice = async (text) => {
        try {
            addMessage('system', "Synthesizing voice in the Nth Dimension...");
            const response = await fetch('http://localhost:8000/api/voice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, target_language: "te-IN" }) // Default to Telugu as per Multilingual Tutor goal
            });
            const data = await response.json();
            if (data.audio_urls) {
                const audio = new Audio(data.audio_urls[0]);
                audio.play();
            }
        } catch (error) {
            console.error('Voice Error:', error);
        }
    };

    openBtn.addEventListener('click', openAssistant);
    closeBtn.addEventListener('click', closeAssistant);

    sendBtn.addEventListener('click', () => {
        const text = userInput.value.trim();
        if (text) {
            addMessage('user', text);
            userInput.value = '';
            callNIM(text);
        }
    });

    voiceBtn.addEventListener('click', () => {
        const lastMessage = Array.from(chatMessages.querySelectorAll('.message.system p')).pop();
        if (lastMessage) {
            synthesizeVoice(lastMessage.innerText);
        }
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendBtn.click();
    });

    // Video Carousel Swiping & Clickable Dots Interaction
    const carousel = document.querySelector('.video-carousel');
    const dots = document.querySelectorAll('.carousel-dot');

    if (carousel && dots.length > 0) {
        carousel.addEventListener('scroll', () => {
            const index = Math.round(carousel.scrollLeft / carousel.clientWidth);
            dots.forEach((dot, idx) => {
                if (idx === index) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });
        });

        dots.forEach(dot => {
            dot.addEventListener('click', function() {
                const targetIndex = parseInt(this.getAttribute('data-index'));
                carousel.scrollTo({
                    left: targetIndex * carousel.clientWidth,
                    behavior: 'smooth'
                });
            });
        });
    }
});
