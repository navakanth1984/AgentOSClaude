/**
 * NTH Brain - 3D/4D Spatial Telemetry & Bidding Engine (MVP v0.1)
 * Integrates WebGL three.js coordinate mapping, 3D raycast drawing,
 * volumetric 3D fog lights, and animated 4D particle flow annotations.
 */

class NTHBrainEngine {
    constructor() {
        this.canvas = document.getElementById('thinking-surface');
        this.container = document.getElementById('canvas-container');
        this.fogOverlay = document.getElementById('fog-light-overlay');
        this.streamContainer = document.getElementById('stream-container');
        this.swarmFeed = document.getElementById('swarm-feed');
        this.compressionRatio = document.getElementById('compression-ratio');
        this.hudSplatCount = document.getElementById('hud-splat-count');

        // Compaction & Quantization State
        this.compactionActive = true;
        this.quantizationTolerance = 0.05; // 3D distance tolerance in units
        this.totalPointsBeforeCompaction = 0;
        this.totalPointsAfterCompaction = 0;

        // Telemetry Data Store (3D Coordinates)
        this.strokeTelemetry = [];
        this.currentStroke = null;
        this.isDrawing = false;
        this.interactionMode = 'draw'; // 'draw' or 'rotate'
        
        // 3D/4D Render State
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.drawingPlane = null;
        this.drawingLine = null;
        this.activeLinePoints = [];
        this.particleSystems = []; // Holds 4D splat particle flow networks
        this.raycaster = new THREE.Raycaster();
        this.mouseVector = new THREE.Vector2();

        // 3D Agent Mesh Reference Objects
        this.agentMeshes = {
            avatar: null,
            observer: null,
            modeler: null,
            bidder: null
        };

        // BKT (Bayesian Knowledge Tracing) & Student Mind Graph State
        this.studentMindGraph = {
            skill_source_mastery: 0.15,
            skill_intermediate_mastery: 0.10,
            path_efficiency: 0.0,
            current_anchor: null,
            target_flow_completed: false
        };

        // Safety Budget State (Audit Loop)
        this.auditBudget = {
            total_bids_triggered: 0,
            token_spent_weight: 0.0,
            max_daily_budget: 0.50, // Token budget limit in mock credits
            status: "OK"
        };

        // Governance Layer: Constitution Graph Rules
        this.constitutionRules = {
            "NO_DIRECT_ANSWERS": true,        // Action cannot spoon-feed the direct answer
            "SELF_ERASURE_MANDATE": true,      // Zero active module output during student active drawing
            "SAFETY_LIMIT_OVERRIDE": true,     // Cannot execute actions when budget is depleted
            "PEDAGOGICAL_SCAFFOLD_ONLY": true  // Hints must guide conceptually rather than solve
        };

        // Cognitive Actions Catalog (Cognitive Token Protocol - CTP definitions)
        this.cognitiveActions = {
            "direct_solution_hint": {
                name: "Direct Solution Spoon-Feeding",
                expected_info_gain: 0.01,
                compute_cost: 0.200, // Very heavy, low efficiency
                rules_violated: ["NO_DIRECT_ANSWERS", "PEDAGOGICAL_SCAFFOLD_ONLY"]
            },
            "spawn_seed": {
                name: "Spawn Spatial Seed Clue",
                expected_info_gain: 0.50,
                compute_cost: 0.005, // Ultra-light hint
                rules_violated: []
            },
            "apply_annotation": {
                name: "Apply Workspace Path Highlights",
                expected_info_gain: 0.60,
                compute_cost: 0.002, // Visual highlight
                rules_violated: []
            },
            "self_erasure_silence": {
                name: "Observe Drawing State (Silence)",
                expected_info_gain: 0.40,
                compute_cost: 0.0001, // Near-zero computational footprint
                rules_violated: []
            }
        };

        // DOM nodes for loops monitoring
        this.observeCard = document.getElementById('loop-observe');
        this.inferCard = document.getElementById('loop-infer');
        this.decideCard = document.getElementById('loop-decide');
        this.auditCard = document.getElementById('loop-audit');

        // Bidding HUD DOM nodes
        this.bidOpVal = document.getElementById('hud-bid-op');
        this.bidCostVal = document.getElementById('hud-bid-cost');
        this.bidEvcrVal = document.getElementById('hud-bid-evcr');

        this.init3DScene();
        this.initEventListeners();
        this.runLifecycleLoops();
    }

    // Initialize WebGL 3D/4D Workspace
    init3DScene() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        // 1. Scene & Render Setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x06070a);
        this.scene.fog = new THREE.FogExp2(0x06070a, 0.02);

        this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        this.camera.position.set(0, 7, 14);

        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // 2. Camera Controls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI; // Full polar range to allow rotating under the grid floor
        this.controls.enabled = false; // Disabled by default, activated in ORBIT MODE

        // 3. Grid & Drawing Plane Scaffolding
        const grid = new THREE.GridHelper(24, 24, 0x6366f1, 0x1e293b);
        grid.position.y = -1;
        this.scene.add(grid);

        // Virtual invisible plane at drawing depth (Y=0)
        const planeGeo = new THREE.PlaneGeometry(50, 50);
        planeGeo.rotateX(-Math.PI / 2);
        const planeMat = new THREE.MeshBasicMaterial({ visible: false });
        this.drawingPlane = new THREE.Mesh(planeGeo, planeMat);
        this.scene.add(this.drawingPlane);

        // 4. Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.25);
        this.scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0x818cf8, 2.0, 40);
        pointLight.position.set(0, 12, 0);
        this.scene.add(pointLight);

        // 5. Initialize 3D Spatial Anchors A, B, C, D
        this.anchors = [
            { id: 'A', name: 'Source Node A', pos: new THREE.Vector3(-6, 0, -3), color: 0x10b981 }, // Emerald Green
            { id: 'B', name: 'Intermediate B', pos: new THREE.Vector3(-1.5, 0, 3.5), color: 0xf59e0b }, // Amber
            { id: 'C', name: 'Intermediate C', pos: new THREE.Vector3(2.5, 0, -2.5), color: 0x8b5cf6 }, // Purple
            { id: 'D', name: 'Destination D', pos: new THREE.Vector3(6.5, 0, 2), color: 0x3b82f6 } // Blue
        ];

        this.anchors.forEach(anchor => {
            // Render anchor sphere
            const sphereGeo = new THREE.SphereGeometry(0.35, 32, 32);
            const sphereMat = new THREE.MeshStandardMaterial({
                color: anchor.color,
                emissive: anchor.color,
                emissiveIntensity: 0.9,
                roughness: 0.05,
                metalness: 0.9
            });
            const mesh = new THREE.Mesh(sphereGeo, sphereMat);
            mesh.position.copy(anchor.pos);
            this.scene.add(mesh);
            anchor.mesh = mesh;

            // Find corresponding HTML anchor label element
            anchor.element = document.getElementById(`anchor-${anchor.id}`);
        });

        // 6. Spawn physical 3D Agent Meshes representing Digital Mind Swarm
        this.spawn3DAgents();

        // 7. Start WebGL Frame Draw Loop
        this.animate();
        this.logTelemetry("SYSTEM", "Immersive 3D WebGL Spatial canvas initialized.", "system-msg");
    }

    // Spawn 3D agent representations inside the Three.js scene
    spawn3DAgents() {
        // A. User Nanobanana Avatar (Stylized capsule)
        const bananaGeo = new THREE.CapsuleGeometry(0.18, 0.4, 8, 16);
        const bananaMat = new THREE.MeshStandardMaterial({
            color: 0xfacc15, // banana yellow
            emissive: 0xeab308,
            emissiveIntensity: 0.5,
            roughness: 0.2,
            metalness: 0.5
        });
        this.agentMeshes.avatar = new THREE.Mesh(bananaGeo, bananaMat);
        this.agentMeshes.avatar.position.set(-6, 1.5, -3); // start at Node A
        this.scene.add(this.agentMeshes.avatar);

        // B. Observe-Agent (Cyan Dodecahedron)
        const observerGeo = new THREE.DodecahedronGeometry(0.3, 0);
        const observerMat = new THREE.MeshStandardMaterial({
            color: 0x06b6d4, // cyan
            wireframe: true,
            emissive: 0x06b6d4,
            emissiveIntensity: 0.3
        });
        this.agentMeshes.observer = new THREE.Mesh(observerGeo, observerMat);
        this.agentMeshes.observer.position.set(-3, 2, 0);
        this.scene.add(this.agentMeshes.observer);

        // C. Infer-Agent (Purple Octahedron)
        const modelerGeo = new THREE.OctahedronGeometry(0.35, 0);
        const modelerMat = new THREE.MeshStandardMaterial({
            color: 0x8b5cf6, // purple
            wireframe: true,
            emissive: 0x8b5cf6,
            emissiveIntensity: 0.3
        });
        this.agentMeshes.modeler = new THREE.Mesh(modelerGeo, modelerMat);
        this.agentMeshes.modeler.position.set(0, 2.5, 0);
        this.scene.add(this.agentMeshes.modeler);

        // D. Decide-Agent (Gold Torus)
        const bidderGeo = new THREE.TorusGeometry(0.25, 0.08, 8, 24);
        const bidderMat = new THREE.MeshStandardMaterial({
            color: 0xf59e0b, // gold
            wireframe: true,
            emissive: 0xf59e0b,
            emissiveIntensity: 0.3
        });
        this.agentMeshes.bidder = new THREE.Mesh(bidderGeo, bidderMat);
        this.agentMeshes.bidder.position.set(3, 2, 0);
        this.scene.add(this.agentMeshes.bidder);
    }

    // Capture mouse coordinate conversion for 3D Raycasting
    updateMouseVector(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.mouseVector.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouseVector.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    }

    // Bind event listeners for drawing, controls, and exporting telemetry
    initEventListeners() {
        // Mode Selector Events
        const btnDraw = document.getElementById('btn-mode-draw');
        const btnRotate = document.getElementById('btn-mode-rotate');

        btnDraw.addEventListener('click', () => {
            this.interactionMode = 'draw';
            this.controls.enabled = false;
            btnDraw.classList.add('active');
            btnRotate.classList.remove('active');
            this.logSwarmMessage("System", "Switched to DRAW MODE. Canvas orbit locked.");
        });

        btnRotate.addEventListener('click', () => {
            this.interactionMode = 'rotate';
            this.controls.enabled = true;
            btnRotate.classList.add('active');
            btnDraw.classList.remove('active');
            this.logSwarmMessage("System", "Switched to ORBIT MODE. Swipe or drag to rotate view 360°.");
        });

        // Canvas Drawing Events
        this.canvas.addEventListener('mousedown', (e) => this.startStroke(e));
        this.canvas.addEventListener('mousemove', (e) => this.drawStroke(e));
        this.canvas.addEventListener('mouseup', () => this.endStroke());
        this.canvas.addEventListener('mouseleave', () => this.endStroke());

        // Fog controls
        const fogSlider = document.getElementById('fog-slider');
        const fogVal = document.getElementById('fog-val');
        const fogActive = document.getElementById('fog-active');

        const updateFogLight = () => {
            if (fogActive.checked) {
                const intensity = fogSlider.value;
                fogVal.innerText = `${intensity}%`;
                
                // 1. Local HTML glass blur overlay
                const opacity = (intensity / 100) * 0.9;
                this.fogOverlay.style.background = `radial-gradient(circle at 50% 50%, rgba(10, 11, 16, 0) 150px, rgba(10, 11, 16, ${opacity * 0.7}) 300px, rgba(10, 11, 16, ${opacity}) 600px)`;

                // 2. WebGL 3D Volumetric Fog Density Adjustment
                const fogDensity = (intensity / 100) * 0.15;
                this.scene.fog.density = fogDensity;
            } else {
                fogVal.innerText = 'Disabled';
                this.fogOverlay.style.background = 'none';
                this.scene.fog.density = 0.001; // minimal fog
            }
        };

        fogSlider.addEventListener('input', updateFogLight);
        fogActive.addEventListener('change', updateFogLight);
        updateFogLight();

        // Compaction / Compression Controls
        const quantSlider = document.getElementById('quantization-slider');
        const quantVal = document.getElementById('quantization-val');
        const compactionActive = document.getElementById('compaction-active');

        quantSlider.addEventListener('input', () => {
            const val = quantSlider.value;
            // Map 1-10 to 0.01 - 0.10 units tolerance
            this.quantizationTolerance = val * 0.01;
            quantVal.innerText = `${this.quantizationTolerance.toFixed(2)}m tolerance`;
            this.logSwarmMessage("Observe-Agent", `Compaction tolerance adjusted to ${this.quantizationTolerance.toFixed(2)}m`);
        });

        compactionActive.addEventListener('change', () => {
            this.compactionActive = compactionActive.checked;
            this.logSwarmMessage("System", `Douglas-Peucker Compaction: ${this.compactionActive ? 'ENABLED' : 'DISABLED'}`);
            this.recalculateCompressionRatio();
        });

        // Action Buttons
        document.getElementById('btn-clear-canvas').addEventListener('click', () => this.clearCanvas());
        document.getElementById('btn-share-thinking').addEventListener('click', () => this.exportTelemetry());

        // Update canvas size responsive
        window.addEventListener('resize', () => {
            const width = this.container.clientWidth;
            const height = this.container.clientHeight;
            this.camera.aspect = width / height;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(width, height);
        });
    }

    // 3D Raycast Draw Operations
    startStroke(e) {
        if (this.interactionMode !== 'draw') return;
        this.controls.enabled = false;
        this.isDrawing = true;
        this.updateMouseVector(e);

        this.raycaster.setFromCamera(this.mouseVector, this.camera);
        const intersects = this.raycaster.intersectObject(this.drawingPlane);

        if (intersects.length > 0) {
            const point = intersects[0].point;
            this.activeLinePoints = [point];

            // Setup new THREE.Line
            const lineGeo = new THREE.BufferGeometry().setFromPoints(this.activeLinePoints);
            const lineMat = new THREE.LineBasicMaterial({
                color: 0x818cf8, // indigo
                linewidth: 3 // Note: WebGL ignore linewidth on Windows, so we render clean line
            });
            this.drawingLine = new THREE.Line(lineGeo, lineMat);
            this.scene.add(this.drawingLine);

            this.currentStroke = {
                id: `stroke_${Date.now()}`,
                points: [{ x: point.x, y: point.y, z: point.z, t: Date.now() }]
            };

            this.logTelemetry("TELEMETRY", `3D Stroke started at vector: (${point.x.toFixed(2)}, ${point.y.toFixed(2)}, ${point.z.toFixed(2)})`, 'telemetry-event');
        }
    }

    drawStroke(e) {
        if (this.interactionMode !== 'draw' || !this.isDrawing) return;
        this.updateMouseVector(e);

        this.raycaster.setFromCamera(this.mouseVector, this.camera);
        const intersects = this.raycaster.intersectObject(this.drawingPlane);

        if (intersects.length > 0) {
            const point = intersects[0].point;
            this.activeLinePoints.push(point);

            // Update line geometry
            this.drawingLine.geometry.setFromPoints(this.activeLinePoints);

            // Move Nanobanana Avatar mesh to cursor draw position
            if (this.agentMeshes.avatar) {
                this.agentMeshes.avatar.position.set(point.x, 1.2, point.z);
            }

            // Compute velocity
            const prevPoint = this.currentStroke.points[this.currentStroke.points.length - 1];
            const dt = Date.now() - prevPoint.t;
            const dist = Math.sqrt((point.x - prevPoint.x)**2 + (point.y - prevPoint.y)**2 + (point.z - prevPoint.z)**2);
            const velocity = dt > 0 ? (dist / dt) * 1000 : 0; // units/sec

            this.currentStroke.points.push({ x: point.x, y: point.y, z: point.z, t: Date.now(), v: velocity });

            // Check proximity to anchors in 3D
            this.checkAnchorProximity3D(point);
        }
    }

    endStroke() {
        if (this.interactionMode !== 'draw' || !this.isDrawing) return;
        this.isDrawing = false;
        this.controls.enabled = (this.interactionMode === 'rotate');

        if (this.currentStroke && this.currentStroke.points.length > 1) {
            const originalLength = this.currentStroke.points.length;
            this.totalPointsBeforeCompaction += originalLength;

            let finalPoints = this.currentStroke.points;

            if (this.compactionActive) {
                // Apply Douglas-Peucker compression
                finalPoints = this.compressPoints(this.currentStroke.points, this.quantizationTolerance);
                this.currentStroke.points = finalPoints;
                this.totalPointsAfterCompaction += finalPoints.length;
                this.recalculateCompressionRatio();

                this.logSwarmMessage("Observe-Agent", `Compacted coordinates load from ${originalLength} to ${finalPoints.length} points.`);
            } else {
                this.totalPointsAfterCompaction += originalLength;
                this.recalculateCompressionRatio();
            }

            this.strokeTelemetry.push({
                stroke: this.currentStroke,
                lineObj: this.drawingLine
            });
            this.logTelemetry("TELEMETRY", `3D Stroke completed. Points stored: ${finalPoints.length} (Uncompressed: ${originalLength})`, 'telemetry-event');
        }
        this.currentStroke = null;
        this.drawingLine = null;
    }

    // Douglas-Peucker coordinate compaction algorithm for 3D coordinates
    compressPoints(points, tolerance) {
        if (points.length <= 2) return points;

        let maxSqDist = 0;
        let index = 0;
        const end = points.length - 1;

        for (let i = 1; i < end; i++) {
            const sqDist = this.getSquareSegmentDistance(points[i], points[0], points[end]);
            if (sqDist > maxSqDist) {
                index = i;
                maxSqDist = sqDist;
            }
        }

        if (maxSqDist > tolerance * tolerance) {
            const results1 = this.compressPoints(points.slice(0, index + 1), tolerance);
            const results2 = this.compressPoints(points.slice(index), tolerance);
            return results1.slice(0, results1.length - 1).concat(results2);
        }

        return [points[0], points[end]];
    }

    getSquareSegmentDistance(p, p1, p2) {
        let x = p1.x;
        let y = p1.y;
        let z = p1.z;
        let dx = p2.x - x;
        let dy = p2.y - y;
        let dz = p2.z - z;

        if (dx !== 0 || dy !== 0 || dz !== 0) {
            const t = ((p.x - x) * dx + (p.y - y) * dy + (p.z - z) * dz) / (dx * dx + dy * dy + dz * dz);
            if (t > 1) {
                x = p2.x;
                y = p2.y;
                z = p2.z;
            } else if (t > 0) {
                x += dx * t;
                y += dy * t;
                z += dz * t;
            }
        }

        dx = p.x - x;
        dy = p.y - y;
        dz = p.z - z;

        return dx * dx + dy * dy + dz * dz;
    }

    recalculateCompressionRatio() {
        if (this.totalPointsAfterCompaction === 0) {
            this.compressionRatio.innerText = "1.0x";
            return;
        }
        const ratio = this.totalPointsBeforeCompaction / this.totalPointsAfterCompaction;
        this.compressionRatio.innerText = `${ratio.toFixed(1)}x`;
    }

    logSwarmMessage(sender, text) {
        if (!this.swarmFeed) return;
        const line = document.createElement('div');
        line.className = 'feed-line';
        line.innerHTML = `<strong>[${sender}]</strong> ${text}`;
        this.swarmFeed.appendChild(line);
        this.swarmFeed.scrollTop = this.swarmFeed.scrollHeight;
    }

    logTelemetry(type, msg, style) {
        if (!this.streamContainer) return;
        const row = document.createElement('div');
        row.className = `telemetry-row ${style || ''}`;
        row.innerText = `[${type}] ${msg}`;
        this.streamContainer.appendChild(row);
        this.streamContainer.scrollTop = this.streamContainer.scrollHeight;
    }

    // 3D Distance Proximity Checks for Student Mind Graph inputs
    checkAnchorProximity3D(point) {
        this.anchors.forEach(anchor => {
            const dist = point.distanceTo(anchor.pos);
            if (dist < 0.75) { // Proximity collision boundary in WebGL units
                if (this.studentMindGraph.current_anchor !== anchor.id) {
                    this.studentMindGraph.current_anchor = anchor.id;
                    anchor.mesh.material.emissiveIntensity = 2.0; // Glow bright
                    
                    // Activate active class styling on HTML tags
                    if (anchor.element) anchor.element.classList.add('active');
                    this.logTelemetry("OBSERVER", `3D Proximity Match: Node ${anchor.id}`, "telemetry-event");
                }
            } else {
                if (this.studentMindGraph.current_anchor === anchor.id && dist > 1.2) {
                    // Left anchor zone
                    anchor.mesh.material.emissiveIntensity = 0.8;
                    if (anchor.element) anchor.element.classList.remove('active');
                    this.studentMindGraph.current_anchor = null;
                }
            }
        });
    }

    clearCanvas() {
        // Remove drawn line meshes from scene
        this.strokeTelemetry.forEach(s => {
            if (s.lineObj) this.scene.remove(s.lineObj);
        });
        this.strokeTelemetry = [];

        // Remove 4D splat particle flow networks
        this.particleSystems.forEach(sys => {
            if (sys.mesh) this.scene.remove(sys.mesh);
            if (sys.points) this.scene.remove(sys.points);
        });
        this.particleSystems = [];

        // Reset anchors glow
        this.anchors.forEach(anchor => {
            anchor.mesh.material.emissiveIntensity = 0.8;
            if (anchor.element) anchor.element.classList.remove('active');
        });

        // Reset state values
        this.studentMindGraph.skill_source_mastery = 0.15;
        this.studentMindGraph.skill_intermediate_mastery = 0.10;
        this.studentMindGraph.path_efficiency = 0.0;
        this.studentMindGraph.current_anchor = null;
        this.studentMindGraph.target_flow_completed = false;

        this.logTelemetry("SYSTEM", "WebGL coordinates plane cleared. Telemetry state reset.", "system-msg");
        this.updateHUD("Idle", 0.0);
    }

    // 4-Loop Engine Lifecycle Execution
    runLifecycleLoops() {
        setInterval(() => {
            this.observeLoop();
            this.inferLoop();
            this.decideLoop();
            this.auditLoop();
        }, 1000); 
    }

    // 1. Observe Loop
    observeLoop() {
        const obsState = this.observeCard.querySelector('.loop-state');
        const obsDetails = this.observeCard.querySelector('.loop-details');

        if (this.isDrawing) {
            obsState.innerText = "CAPTURING";
            obsState.style.color = "var(--accent-emerald)";
            const latestPoint = this.currentStroke.points[this.currentStroke.points.length - 1];
            obsDetails.innerText = `XYZ: (${latestPoint.x.toFixed(1)}, ${latestPoint.y.toFixed(1)}, ${latestPoint.z.toFixed(1)})`;
        } else {
            obsState.innerText = "STREAM_WAIT";
            obsState.style.color = "var(--text-secondary)";
            obsDetails.innerText = `Total strokes: ${this.strokeTelemetry.length}`;
        }
    }

    // 2. Infer Loop
    inferLoop() {
        const infState = this.inferCard.querySelector('.loop-state');
        const infDetails = this.inferCard.querySelector('.loop-details');

        const currentAnchor = this.studentMindGraph.current_anchor;
        
        if (currentAnchor) {
            if (currentAnchor === 'A') {
                this.studentMindGraph.skill_source_mastery = Math.min(0.95, this.studentMindGraph.skill_source_mastery + 0.05);
            } else if (currentAnchor === 'B' || currentAnchor === 'C') {
                this.studentMindGraph.skill_intermediate_mastery = Math.min(0.95, this.studentMindGraph.skill_intermediate_mastery + 0.04);
            } else if (currentAnchor === 'D' && this.studentMindGraph.skill_intermediate_mastery > 0.4) {
                this.studentMindGraph.target_flow_completed = true;
            }

            const masterSum = this.studentMindGraph.skill_source_mastery + this.studentMindGraph.skill_intermediate_mastery;
            this.studentMindGraph.path_efficiency = Math.min(1.0, masterSum / 1.8);

            infState.innerText = `Zone: ${currentAnchor}`;
            infState.style.color = "#a78bfa";
            infDetails.innerText = `Src ${Math.round(this.studentMindGraph.skill_source_mastery * 100)}% | Mid ${Math.round(this.studentMindGraph.skill_intermediate_mastery * 100)}%`;
            
            if (Math.random() < 0.15) { 
                this.logTelemetry("INFERENCE", `BKT Update - Masteries: Src=${this.studentMindGraph.skill_source_mastery.toFixed(2)}, Mid=${this.studentMindGraph.skill_intermediate_mastery.toFixed(2)}`, "infer-event");
            }
        } else {
            infState.innerText = "Awaiting Anchor";
            infState.style.color = "var(--text-secondary)";
            infDetails.innerText = "Drawing coordinates plane idle.";
        }
    }

    // 3. Decide Loop (Implements Governance ➔ Economy ➔ Agency hierarchical bidding)
    decideLoop() {
        const decState = this.decideCard.querySelector('.loop-state');
        const decDetails = this.decideCard.querySelector('.loop-details');

        let candidates = [];
        
        if (this.isDrawing) {
            candidates = ["self_erasure_silence", "direct_solution_hint"];
        } else if (this.studentMindGraph.current_anchor || this.studentMindGraph.target_flow_completed) {
            if (this.studentMindGraph.target_flow_completed) {
                candidates = ["apply_annotation", "direct_solution_hint"];
            } else if (this.studentMindGraph.skill_source_mastery > 0.5 && this.studentMindGraph.skill_intermediate_mastery < 0.25) {
                candidates = ["spawn_seed", "direct_solution_hint"];
            } else {
                candidates = ["self_erasure_silence"];
            }
        } else {
            candidates = ["self_erasure_silence"];
        }

        // 1. Governance Layer: Veto candidates violating Constitutional rules
        let vettedCandidates = candidates.filter(actionKey => {
            const action = this.cognitiveActions[actionKey];
            
            if (this.constitutionRules.NO_DIRECT_ANSWERS && action.rules_violated.includes("NO_DIRECT_ANSWERS")) {
                if (Math.random() < 0.15) { 
                    this.logTelemetry("GOVERNANCE", `VETO: '${action.name}' violates NO_DIRECT_ANSWERS (spoon-feeding banned).`, "audit-event");
                }
                return false;
            }
            if (this.constitutionRules.PEDAGOGICAL_SCAFFOLD_ONLY && action.rules_violated.includes("PEDAGOGICAL_SCAFFOLD_ONLY")) {
                return false;
            }
            if (this.isDrawing && this.constitutionRules.SELF_ERASURE_MANDATE && actionKey !== "self_erasure_silence") {
                this.logTelemetry("GOVERNANCE", `VETO: Suppressing '${action.name}' - SELF_ERASURE active during drawing.`, "audit-event");
                return false;
            }
            if (this.auditBudget.status === "BUDGET_EXCEEDED" && this.constitutionRules.SAFETY_LIMIT_OVERRIDE) {
                return false;
            }
            return true;
        });

        // 2. Economy Layer: Calculate EVCR ($R_{EV/C}$) for each vetted candidate
        let marketBids = vettedCandidates.map(actionKey => {
            const action = this.cognitiveActions[actionKey];
            const evcr = action.expected_info_gain / action.compute_cost;
            return {
                key: actionKey,
                name: action.name,
                cost: action.compute_cost,
                evcr: evcr
            };
        });

        marketBids.sort((a, b) => b.evcr - a.evcr);

        // 3. Agency Layer: Select and execute the winning bid
        if (marketBids.length > 0) {
            const winningBid = marketBids[0];
            
            if (winningBid.key === "self_erasure_silence") {
                decState.innerText = "SELF_ERASURE";
                decState.style.color = "var(--text-secondary)";
                decDetails.innerText = `Silence (EVCR: ${winningBid.evcr.toFixed(0)})`;
                
                if (this.isDrawing || Math.random() < 0.05) {
                    this.updateHUD("Silence (Observe)", winningBid.cost, winningBid.evcr);
                }
            } else {
                this.triggerVisualBid(winningBid.key, winningBid.cost, winningBid.evcr, `Winning bid: ${winningBid.name}`);
                
                if (winningBid.key === "apply_annotation") {
                    decState.innerText = "BID_APPLIED";
                    decState.style.color = "var(--accent-emerald)";
                    decDetails.innerText = `Path glow (EVCR: ${winningBid.evcr.toFixed(0)})`;
                    this.studentMindGraph.current_anchor = null; 
                } else if (winningBid.key === "spawn_seed") {
                    decState.innerText = "BID_SEEDED";
                    decState.style.color = "var(--accent-amber)";
                    decDetails.innerText = `Visual hint (EVCR: ${winningBid.evcr.toFixed(0)})`;
                    this.studentMindGraph.current_anchor = null;
                }
            }
        }
    }

    // 4. Audit Loop
    auditLoop() {
        const audState = this.auditCard.querySelector('.loop-state');
        const audDetails = this.auditCard.querySelector('.loop-details');

        if (this.auditBudget.token_spent_weight >= this.auditBudget.max_daily_budget) {
            this.auditBudget.status = "BUDGET_EXCEEDED";
            audState.innerText = "HALTED";
            audState.style.color = "var(--accent-rose)";
            audDetails.innerText = `Limit hit: ${this.auditBudget.token_spent_weight.toFixed(3)} credits`;
            
            this.logTelemetry("AUDITOR", "CRITICAL - Bidding engine halted. Token weight budget exhausted.", "audit-event");
        } else {
            audState.innerText = "ACTIVE_SAFE";
            audState.style.color = "var(--accent-emerald)";
            audDetails.innerText = `Bids: ${this.auditBudget.total_bids_triggered} | Cost: ${this.auditBudget.token_spent_weight.toFixed(3)} credits`;
        }
    }

    triggerVisualBid(operation, cost, evcr, reasoning) {
        if (this.auditBudget.status === "BUDGET_EXCEEDED") return;

        this.auditBudget.total_bids_triggered++;
        this.auditBudget.token_spent_weight += cost;

        this.updateHUD(operation, cost, evcr);
        this.logTelemetry("DECIDE", `[BID] Win=${operation} (EVCR: ${evcr.toFixed(0)} | Cost: ${cost.toFixed(4)}) - Reasoning: ${reasoning}`, "decide-event");

        if (operation === 'apply_annotation') {
            this.spawn4DSplatFlowNetwork();
        } else if (operation === 'spawn_seed') {
            this.spawn3DSeedBox();
        }
    }
    updateHUD(op, cost, evcr) {
        this.bidOpVal.innerText = op;
        this.bidCostVal.innerText = cost.toFixed(4);
        this.bidEvcrVal.innerText = evcr.toFixed(0);
    }

    // Render spatial flow annotation as an animated 4D Gaussian Splat network (ellipsoidal instances)
    spawn4DSplatFlowNetwork() {
        // Clear old splat systems
        this.particleSystems.forEach(sys => {
            if (sys.mesh) this.scene.remove(sys.mesh);
            if (sys.points) this.scene.remove(sys.points);
        });
        this.particleSystems = [];

        const start = this.anchors.find(a => a.id === 'A');
        const end = this.anchors.find(a => a.id === 'D');

        if (!start || !end) return;

        // Generate bezier path points in 3D space
        const curve = new THREE.QuadraticBezierCurve3(
            start.pos,
            new THREE.Vector3((start.pos.x + end.pos.x) / 2, 3.0, (start.pos.z + end.pos.z) / 2),
            end.pos
        );

        const numSplats = 50;
        const sphereGeo = new THREE.SphereGeometry(0.2, 16, 16);
        const splatMat = new THREE.MeshStandardMaterial({
            color: 0x10b981, // green base
            transparent: true,
            opacity: 0.65,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            roughness: 0.1,
            metalness: 0.8
        });

        const instancedMesh = new THREE.InstancedMesh(sphereGeo, splatMat, numSplats);
        
        // Setup initial matrices
        const dummy = new THREE.Object3D();
        const curvePoints = curve.getPoints(numSplats);

        for (let i = 0; i < numSplats; i++) {
            dummy.position.copy(curvePoints[i]);
            // Non-uniform covariance scale for Gaussian Splats
            dummy.scale.set(
                0.7 + Math.random() * 0.4,
                0.15 + Math.random() * 0.15,
                0.15 + Math.random() * 0.15
            );
            dummy.rotation.set(
                Math.random() * Math.PI,
                Math.random() * Math.PI,
                Math.random() * Math.PI
            );
            dummy.updateMatrix();
            instancedMesh.setMatrixAt(i, dummy.matrix);
            
            // Rich multi-spectral color gradient matching Splats
            const col = new THREE.Color(i % 2 === 0 ? 0x10b981 : 0x3b82f6);
            instancedMesh.setColorAt(i, col);
        }

        instancedMesh.instanceMatrix.needsUpdate = true;
        if (instancedMesh.instanceColor) instancedMesh.instanceColor.needsUpdate = true;
        this.scene.add(instancedMesh);

        this.particleSystems.push({
            mesh: instancedMesh,
            curve: curve,
            numParticles: numSplats,
            offset: 0,
            isGaussianSplat: true
        });

        this.hudSplatCount.innerText = numSplats;
        this.logTelemetry("WORKSPACE", "WebGL 4D Gaussian Splat instanced covariance network rendered.", "system-msg");
        this.logSwarmMessage("Decide-Agent", `Spawned 4D Gaussian Splat network (${numSplats} ellipsoids) along optimized trajectory.`);
    }

    // Spawn visual helper mesh in 3D space near Node B
    spawn3DSeedBox() {
        // Clear old ones
        this.particleSystems.forEach(sys => {
            if (sys.mesh) this.scene.remove(sys.mesh);
            if (sys.points) this.scene.remove(sys.points);
        });
        this.particleSystems = [];

        const anchorB = this.anchors.find(a => a.id === 'B');
        if (!anchorB) return;

        // Render wireframe cube representing cognitive seed bounds
        const boxGeo = new THREE.BoxGeometry(0.8, 0.8, 0.8);
        const edgeGeo = new THREE.EdgesGeometry(boxGeo);
        const lineMat = new THREE.LineBasicMaterial({ color: 0xf59e0b, linewidth: 2 });
        const boxLines = new THREE.LineSegments(edgeGeo, lineMat);
        
        boxLines.position.copy(anchorB.pos);
        boxLines.position.y += 0.8; // Hover above anchor
        
        this.scene.add(boxLines);
        this.particleSystems.push({
            points: boxLines,
            isBox: true
        });

        this.hudSplatCount.innerText = "0";
        this.logTelemetry("WORKSPACE", "Created 3D cognitive seed bounding box above Node B.", "system-msg");
        this.logSwarmMessage("Infer-Agent", "Spawning spatial seed node clue at Anchor zone B.");
    }

    // 4D Temporal Animation Frame Loop (Three.js Render Cycle)
    animate() {
        requestAnimationFrame(() => this.animate());

        const time = Date.now() * 0.001;

        // 1. Update Camera Orbit Controls
        this.controls.update();

        // 2. Animate 3D Agent Meshes (bobbing, spinning, scaling)
        if (this.agentMeshes.avatar && !this.isDrawing) {
            // Hover bobbing effect for banana
            this.agentMeshes.avatar.position.y = 1.2 + Math.sin(time * 2) * 0.15;
            this.agentMeshes.avatar.rotation.y = time * 0.5;
        }

        if (this.agentMeshes.observer) {
            this.agentMeshes.observer.position.y = 2.0 + Math.sin(time * 1.5) * 0.1;
            this.agentMeshes.observer.rotation.x = time * 0.4;
            this.agentMeshes.observer.rotation.y = time * 0.3;
        }

        if (this.agentMeshes.modeler) {
            this.agentMeshes.modeler.position.y = 2.5 + Math.cos(time * 1.8) * 0.12;
            this.agentMeshes.modeler.rotation.y = time * 0.6;
            this.agentMeshes.modeler.rotation.z = time * 0.4;
        }

        if (this.agentMeshes.bidder) {
            this.agentMeshes.bidder.position.y = 2.0 + Math.sin(time * 2.2) * 0.08;
            this.agentMeshes.bidder.rotation.x = time * 0.5;
            this.agentMeshes.bidder.rotation.y = time * 0.7;
        }

        // 3. Animate 4D Splat Flow Particle Systems
        this.particleSystems.forEach(sys => {
            if (sys.isGaussianSplat && sys.mesh) {
                const dummy = new THREE.Object3D();
                sys.offset += 0.005; // speed multiplier
                if (sys.offset > 1.0) sys.offset = 0.0;

                for (let i = 0; i < sys.numParticles; i++) {
                    let t = (i / sys.numParticles + sys.offset) % 1.0;
                    const point = sys.curve.getPointAt(t);

                    // Harmonic waving along the curve (4D splat modulation)
                    const wave = Math.sin(t * Math.PI * 6 + time * 3) * 0.2;
                    dummy.position.set(point.x, point.y + wave, point.z);

                    // Dynamic scaling over time (inhale/exhale breathing splat effect)
                    const scaleFactor = 0.8 + Math.sin(time * 2 + i) * 0.25;
                    dummy.scale.set(
                        (0.7 + Math.sin(t * Math.PI) * 0.5) * scaleFactor,
                        (0.15 + Math.cos(t * Math.PI * 2) * 0.05) * scaleFactor,
                        (0.15 + Math.sin(t * Math.PI * 2) * 0.05) * scaleFactor
                    );

                    dummy.rotation.set(
                        t * Math.PI + time * 0.2,
                        t * Math.PI * 2 + time * 0.1,
                        time * 0.15
                    );

                    dummy.updateMatrix();
                    sys.mesh.setMatrixAt(i, dummy.matrix);
                }
                sys.mesh.instanceMatrix.needsUpdate = true;
            } else if (sys.isBox && sys.points) {
                // Rotate floating 3D seed box
                sys.points.rotation.x += 0.01;
                sys.points.rotation.y += 0.015;
            }
        });

        // 4. Project 3D Anchor positions to HTML DOM Labels dynamically
        this.anchors.forEach(anchor => {
            if (anchor.element) {
                const tempV = anchor.pos.clone();
                tempV.project(this.camera);

                const x = (tempV.x *  .5 + .5) * this.container.clientWidth;
                const y = (tempV.y * -.5 + .5) * this.container.clientHeight;

                anchor.element.style.transform = `translate(-50%, -50%)`;
                anchor.element.style.left = `${x}px`;
                anchor.element.style.top = `${y}px`;
            }
        });

        // 5. Project 3D Agents positions to HTML DOM tags dynamically
        const projectAgentTag = (mesh, tagId) => {
            const el = document.getElementById(tagId);
            if (mesh && el) {
                const tempV = mesh.position.clone();
                // Offset tag label slightly above the 3D mesh
                tempV.y += 0.65;
                tempV.project(this.camera);

                // Clip if behind camera
                if (tempV.z > 1) {
                    el.style.opacity = '0';
                    return;
                }

                const x = (tempV.x *  .5 + .5) * this.container.clientWidth;
                const y = (tempV.y * -.5 + .5) * this.container.clientHeight;

                el.style.opacity = '1';
                el.style.left = `${x}px`;
                el.style.top = `${y}px`;
            }
        };

        projectAgentTag(this.agentMeshes.avatar, 'tag-avatar');
        projectAgentTag(this.agentMeshes.observer, 'tag-observer');
        projectAgentTag(this.agentMeshes.modeler, 'tag-modeler');
        projectAgentTag(this.agentMeshes.bidder, 'tag-bidder');

        // 6. Render WebGL context
        this.renderer.render(this.scene, this.camera);
    }

    // Export captured 3D telemetry dataset
    exportTelemetry() {
        if (this.strokeTelemetry.length === 0) {
            alert('No 3D spatial drawing telemetry exists to export. Please sketch on the surface.');
            return;
        }

        const dataPackage = {
            metadata: {
                project: "NTH Brain 3D Spatial Canvas",
                version: "MVP v0.2 (Antigravity SDK Sync)",
                timestamp: new Date().toISOString(),
                telemetry_mode: "3D_Raycast",
                format: "XYZTV",
                compression: {
                    douglas_peucker_active: this.compactionActive,
                    quantization_tolerance_units: this.quantizationTolerance,
                    points_before_compaction: this.totalPointsBeforeCompaction,
                    points_after_compaction: this.totalPointsAfterCompaction,
                    savings_ratio: (this.totalPointsBeforeCompaction / this.totalPointsAfterCompaction).toFixed(2)
                }
            },
            student_mind_graph: this.studentMindGraph,
            strokes: this.strokeTelemetry.map(s => {
                return {
                    id: s.stroke.id,
                    points: s.stroke.points
                };
            })
        };

        const jsonStr = JSON.stringify(dataPackage, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `nth_brain_3d_telemetry_compressed_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.logTelemetry("SYSTEM", "3D coordinate telemetry dataset successfully exported.", "system-msg");
        this.logSwarmMessage("System", `Exported telemetry payload. Saved ${((1 - this.totalPointsAfterCompaction/this.totalPointsBeforeCompaction)*100).toFixed(0)}% token load size.`);
    }
}

// Initialise the WebGL workspace engine on page load
window.addEventListener('DOMContentLoaded', () => {
    window.NTHBrain = new NTHBrainEngine();
});
