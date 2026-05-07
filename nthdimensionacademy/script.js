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
    }
});
