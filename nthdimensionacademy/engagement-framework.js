/**
 * Nth Dimension Academy - Engagement & UX Telemetry Framework (Vanilla version)
 * Tracks user experience signals (Time, Scroll, Clicks, Sections) and converts
 * them into an in-universe gamified learning companion HUD.
 */

(function () {
    // --- EVENT REGISTRY ---
    const EVENTS = {
        SECTION_VISITED: 'academy:sectionVisited',
        MILESTONE_UNLOCKED: 'academy:milestoneUnlocked',
        CURIOSITY_CHANGED: 'academy:curiosityChanged'
    };

    // --- CONFIGURATION CONSTANTS ---
    const CONFIG = {
        VERSION: 1,
        SESSION_STORAGE_KEY: 'nth_learning_hud_v1',
        
        // Score Weightings (Total = 100%)
        WEIGHTS: {
            TIME: 35,
            SCROLL: 30,
            CLICKS: 20,
            SECTIONS: 15
        },
        
        // Thresholds & Cap Limits
        CAPS: {
            MAX_TIME_SEC: 180,    // 3 minutes caps time score
            MAX_CLICKS: 5,        // 5 clicks caps interaction score
            TOTAL_SECTIONS: 8     // Total sections mapping in DOM
        },

        // Learning Momentum Time Thresholds (in seconds)
        MOMENTUM_THRESHOLDS: {
            IMMERSION: 90,
            DEEP_DIVE: 45,
            EXPLORING: 15
        },

        // Explorer Ranks (Minimum Curiosity Index required)
        RANKS: [
            { min: 90, title: 'Cosmic Architect' },
            { min: 60, title: 'Dimension Weaver' },
            { min: 30, title: 'Knowledge Seeker' },
            { min: 0,  title: 'Apprentice Explorer' }
        ],

        // Toast Duration in milliseconds
        TOAST_DURATION_MS: 2400,

        // Curiosity Score Milestones to unlock
        MILESTONES: [
            { threshold: 25, label: 'Timeline unlocked', desc: 'Discovered the ancient history tracks.' },
            { threshold: 50, label: 'Hidden quote discovered', desc: 'Resonated with the architectural tenets.' },
            { threshold: 75, label: 'Interactive visualization unlocked', desc: 'Neural fabric data matrix ready.' },
            { threshold: 90, label: 'Cosmic Architect', desc: 'Achieved maximum comprehension of the Academy.' }
        ]
    };

    // --- STATE MACHINE ---
    const state = {
        isOpen: false,
        timeOnPage: 0,
        maxScrollDepth: 0,
        clickCount: 0,
        visitedSections: [],
        unlockedMilestones: [],
        isTabActive: true,
        lastEmittedScore: -1,
        prefersReducedMotion: false
    };

    // DOM References
    let elements = {
        progressBar: null,
        sectionNameEl: null,
        scrollPercentEl: null,
        hudWrapper: null,
        toastContainer: null
    };

    // --- LIFE CYCLE INITIALIZATION ---
    document.addEventListener('DOMContentLoaded', () => {
        // Accessibility Check
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        state.prefersReducedMotion = mediaQuery.matches;
        mediaQuery.addEventListener('change', (e) => {
            state.prefersReducedMotion = e.matches;
            renderHUD();
        });

        // Initialize state from Storage
        loadStateFromStorage();

        // Build DOM Nodes
        buildProgressAndHUDElements();

        // Bind Events
        bindEventListeners();

        // Initial Calculations
        recalculateAndRender();
        
        // Default to expanded HUD on Desktop viewports
        if (window.innerWidth >= 768) {
            state.isOpen = true;
            renderHUD();
        }
    });

    // --- LOAD & SAVE SESSION STORAGE ---
    function loadStateFromStorage() {
        const rawData = sessionStorage.getItem(CONFIG.SESSION_STORAGE_KEY);
        if (rawData) {
            try {
                const parsed = JSON.parse(rawData);
                if (parsed.version === CONFIG.VERSION) {
                    if (parsed.timeOnPage) state.timeOnPage = parsed.timeOnPage;
                    if (parsed.maxScrollDepth) state.maxScrollDepth = parsed.maxScrollDepth;
                    if (parsed.clickCount) state.clickCount = parsed.clickCount;
                    if (parsed.visitedSections) state.visitedSections = parsed.visitedSections;
                    if (parsed.unlockedMilestones) state.unlockedMilestones = parsed.unlockedMilestones;
                }
            } catch (e) {
                console.warn('Failed to parse sessionStorage UX state:', e);
            }
        }
    }

    function saveStateToStorage() {
        const payload = {
            version: CONFIG.VERSION,
            timeOnPage: state.timeOnPage,
            maxScrollDepth: state.maxScrollDepth,
            clickCount: state.clickCount,
            visitedSections: state.visitedSections,
            unlockedMilestones: state.unlockedMilestones
        };
        sessionStorage.setItem(CONFIG.SESSION_STORAGE_KEY, JSON.stringify(payload));
    }

    // --- DOM BUILDER ---
    function buildProgressAndHUDElements() {
        // 1. Scroll Progress Bar & Pill Overlay
        const progressContainer = document.createElement('div');
        progressContainer.className = 'scroll-progress-container';
        progressContainer.innerHTML = `
            <div class="scroll-progress-bar"></div>
            <div class="active-section-pill">
                <div class="section-pill-content">
                    <span class="section-pill-dot"></span>
                    <span class="section-pill-name">Welcome</span>
                    <span class="section-pill-divider">|</span>
                    <span class="section-pill-progress">0%</span>
                </div>
            </div>
        `;
        document.body.appendChild(progressContainer);

        elements.progressBar = progressContainer.querySelector('.scroll-progress-bar');
        elements.sectionNameEl = progressContainer.querySelector('.section-pill-name');
        elements.scrollPercentEl = progressContainer.querySelector('.section-pill-progress');

        // 2. Toast Alert Container
        elements.toastContainer = document.createElement('div');
        elements.toastContainer.className = 'hud-toast-container';
        document.body.appendChild(elements.toastContainer);

        // 3. Main HUD Wrapper
        elements.hudWrapper = document.createElement('div');
        elements.hudWrapper.className = 'engagement-hud-wrapper';
        document.body.appendChild(elements.hudWrapper);
    }

    // --- CORE LOGIC EVENT LISTENERS ---
    function bindEventListeners() {
        // A. Idle-Aware Timer
        document.addEventListener('visibilitychange', () => {
            state.isTabActive = !document.hidden;
        });

        setInterval(() => {
            if (state.isTabActive) {
                state.timeOnPage++;
                saveStateToStorage();
                recalculateAndRender();
            }
        }, 1000);

        // B. High-Performance Scroll Depth
        let scrolling = false;
        window.addEventListener('scroll', () => {
            if (!scrolling) {
                window.requestAnimationFrame(() => {
                    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
                    if (totalHeight > 0) {
                        const progressPercent = Math.min(
                            100,
                            Math.round((window.scrollY / totalHeight) * 100)
                        );
                        
                        state.maxScrollDepth = Math.max(state.maxScrollDepth, progressPercent);
                        
                        // Update Progress DOM elements
                        if (elements.progressBar) {
                            elements.progressBar.style.width = `${progressPercent}%`;
                        }
                        if (elements.scrollPercentEl) {
                            elements.scrollPercentEl.textContent = `${progressPercent}%`;
                        }
                        
                        saveStateToStorage();
                        recalculateAndRender();
                    }
                    scrolling = false;
                });
                scrolling = true;
            }
        }, { passive: true });

        // C. Intersection Observer for Sectors
        const sections = document.querySelectorAll('[data-section]');
        if (sections.length > 0) {
            const observerOptions = {
                root: null,
                rootMargin: '-20% 0px -60% 0px',
                threshold: 0
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        const sectionName = entry.target.getAttribute('data-section');
                        if (sectionName) {
                            // Update active pill indicator
                            if (elements.sectionNameEl) {
                                elements.sectionNameEl.textContent = sectionName;
                            }
                            
                            // Dispatch Custom DOM Event
                            window.dispatchEvent(
                                new CustomEvent(EVENTS.SECTION_VISITED, {
                                    detail: { section: sectionName }
                                })
                            );
                        }
                    }
                });
            }, observerOptions);

            sections.forEach((section) => observer.observe(section));
        }

        // D. Capture Section Visited Event to update HUD state
        window.addEventListener(EVENTS.SECTION_VISITED, (e) => {
            const section = e.detail?.section;
            if (section && !state.visitedSections.includes(section)) {
                state.visitedSections.push(section);
                saveStateToStorage();
                recalculateAndRender();
            }
        });

        // E. Delegated Click Monitor (ignores clicks within HUD panel itself)
        document.addEventListener('click', (e) => {
            if (elements.hudWrapper && elements.hudWrapper.contains(e.target)) return;

            let el = e.target;
            let depth = 0;
            let clickedInteractive = false;

            while (el && depth < 4) {
                const tag = el.tagName?.toLowerCase();
                const role = el.getAttribute('role');
                const tracksClick = el.hasAttribute('data-track-click') || el.classList.contains('track-click');

                if (
                    tag === 'button' ||
                    tag === 'a' ||
                    tag === 'summary' ||
                    role === 'button' ||
                    role === 'tab' ||
                    role === 'link' ||
                    tracksClick
                ) {
                    if (!el.hasAttribute('disabled')) {
                        clickedInteractive = true;
                        break;
                    }
                }
                el = el.parentElement;
                depth++;
            }

            if (clickedInteractive) {
                state.clickCount++;
                saveStateToStorage();
                recalculateAndRender();
            }
        });
    }

    // --- RECALCULATE SCORING & TOAST TRIGGERS ---
    function recalculateAndRender() {
        // Calculate Sub-scores based on Config weightings
        const timeScore = Math.min(CONFIG.WEIGHTS.TIME, (state.timeOnPage / CONFIG.CAPS.MAX_TIME_SEC) * CONFIG.WEIGHTS.TIME);
        const scrollScore = state.maxScrollDepth * (CONFIG.WEIGHTS.SCROLL / 100);
        const clickScore = Math.min(CONFIG.WEIGHTS.CLICKS, (state.clickCount / CONFIG.CAPS.MAX_CLICKS) * CONFIG.WEIGHTS.CLICKS);
        
        const sectorsCount = Math.max(1, state.visitedSections.length);
        const sectionScore = Math.min(
            CONFIG.WEIGHTS.SECTIONS,
            (sectorsCount / CONFIG.CAPS.TOTAL_SECTIONS) * CONFIG.WEIGHTS.SECTIONS
        );

        const curiosityIndex = Math.min(100, Math.round(timeScore + scrollScore + clickScore + sectionScore));

        // Determine Ranks
        const rankObj = CONFIG.RANKS.find((r) => curiosityIndex >= r.min) || CONFIG.RANKS[CONFIG.RANKS.length - 1];
        const explorerRank = rankObj.title;

        // Emit Curiosity Change Event
        if (curiosityIndex !== state.lastEmittedScore) {
            state.lastEmittedScore = curiosityIndex;
            window.dispatchEvent(
                new CustomEvent(EVENTS.CURIOSITY_CHANGED, {
                    detail: { index: curiosityIndex, rank: explorerRank }
                })
            );
        }

        // Monitor Milestone unlocks
        CONFIG.MILESTONES.forEach((milestone) => {
            if (curiosityIndex >= milestone.threshold && !state.unlockedMilestones.includes(milestone.label)) {
                state.unlockedMilestones.push(milestone.label);
                saveStateToStorage();
                
                // Trigger Toast Alert
                triggerToastAlert(`✨ ${milestone.label}`, milestone.desc);
                
                // Dispatch Event
                window.dispatchEvent(
                    new CustomEvent(EVENTS.MILESTONE_UNLOCKED, {
                        detail: { milestone: milestone.label, description: milestone.desc }
                    })
                );
            }
        });

        // Re-render components
        renderHUD();
    }

    // --- ACHIEVEMENT TOAST DISPATCHER ---
    function triggerToastAlert(title, message) {
        if (!elements.toastContainer) return;

        const toast = document.createElement('div');
        toast.className = 'hud-toast';
        toast.innerHTML = `
            <div class="hud-toast-icon-container">
                <i class="ph-fill ph-award"></i>
            </div>
            <div class="hud-toast-content">
                <div class="hud-toast-title">${title}</div>
                <div class="hud-toast-desc">${message}</div>
            </div>
        `;
        elements.toastContainer.appendChild(toast);

        // Slide in
        setTimeout(() => toast.classList.add('show'), 50);

        // Slide out & remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400);
        }, CONFIG.TOAST_DURATION_MS);
    }

    // --- RENDER HUD ENGINE ---
    function renderHUD() {
        if (!elements.hudWrapper) return;

        const score = state.lastEmittedScore;
        const rankObj = CONFIG.RANKS.find((r) => score >= r.min) || CONFIG.RANKS[CONFIG.RANKS.length - 1];
        const rankName = rankObj.title;

        // Derived Learning Momentum
        let momentum = 'Initializing...';
        if (state.timeOnPage >= CONFIG.MOMENTUM_THRESHOLDS.IMMERSION) momentum = 'Knowledge Immersion';
        else if (state.timeOnPage >= CONFIG.MOMENTUM_THRESHOLDS.DEEP_DIVE) momentum = 'Deep Dive';
        else if (state.timeOnPage >= CONFIG.MOMENTUM_THRESHOLDS.EXPLORING) momentum = 'Exploring';

        // Format Timer display
        const min = Math.floor(state.timeOnPage / 60);
        const sec = (state.timeOnPage % 60).toString().padStart(2, '0');
        const formattedTime = `${min}:${sec}`;

        if (state.isOpen) {
            // Render Maximized Layout Panel
            elements.hudWrapper.innerHTML = `
                <div class="hud-panel">
                    <div class="hud-header">
                        <div class="hud-title-container">
                            <span class="hud-title-icon"><i class="ph ph-compass"></i></span>
                            <span class="hud-title">Learning HUD</span>
                        </div>
                        <button class="hud-btn-toggle" id="hud-toggle-close-btn" aria-label="Collapse HUD">
                            <i class="ph ph-caret-down"></i>
                        </button>
                    </div>
                    <div class="hud-body">
                        <div>
                            <div class="hud-index-header">
                                <span class="hud-index-label">Curiosity Index</span>
                                <span class="hud-index-val">${score}%</span>
                            </div>
                            <div class="hud-progress-bg">
                                <div class="hud-progress-fill" style="width: ${score}%"></div>
                            </div>
                            <div class="hud-rank-label">${rankName}</div>
                        </div>

                        <hr class="hud-divider" />

                        <div class="hud-stats-grid">
                            <div class="hud-stat-box">
                                <span class="hud-stat-label">Momentum</span>
                                <div class="hud-stat-value-container">
                                    <span class="hud-stat-icon active"><i class="ph ph-activity"></i></span>
                                    <span class="hud-stat-value">${momentum}</span>
                                </div>
                            </div>
                            <div class="hud-stat-box">
                                <span class="hud-stat-label">Session Dwell</span>
                                <div class="hud-stat-value-container">
                                    <span class="hud-stat-icon"><i class="ph ph-clock"></i></span>
                                    <span class="hud-stat-value">${formattedTime}</span>
                                </div>
                            </div>
                        </div>

                        <div class="hud-stats-grid">
                            <div class="hud-stat-box">
                                <span class="hud-stat-label">Max Scroll</span>
                                <div class="hud-stat-value-container">
                                    <span class="hud-stat-icon"><i class="ph ph-compass"></i></span>
                                    <span class="hud-stat-value">${state.maxScrollDepth}%</span>
                                </div>
                            </div>
                            <div class="hud-stat-box">
                                <span class="hud-stat-label">Key Actions</span>
                                <div class="hud-stat-value-container">
                                    <span class="hud-stat-icon"><i class="ph ph-mouse-pointer"></i></span>
                                    <span class="hud-stat-value">${state.clickCount} clicks</span>
                                </div>
                            </div>
                        </div>

                        <div class="hud-stat-box">
                            <span class="hud-stat-label">Academy Explored</span>
                            <div class="hud-stat-value-container">
                                <span class="hud-stat-icon"><i class="ph ph-check-square"></i></span>
                                <span class="hud-stat-value">${state.visitedSections.length} of ${CONFIG.CAPS.TOTAL_SECTIONS} sectors</span>
                            </div>
                        </div>

                        ${state.unlockedMilestones.length > 0 ? `
                            <hr class="hud-divider" />
                            <div class="hud-milestones-container">
                                <span class="hud-milestones-label">Milestones Unlocked</span>
                                <div class="hud-milestones-list">
                                    ${state.unlockedMilestones.map(m => `
                                        <div class="hud-milestone-item">
                                            <span class="hud-milestone-check">✓</span>
                                            <span>${m}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;

            // Bind toggle close click
            document.getElementById('hud-toggle-close-btn').addEventListener('click', () => {
                state.isOpen = false;
                renderHUD();
            });
        } else {
            // Render Minimized Trigger Pill
            const animationPulseClass = state.prefersReducedMotion ? '' : 'neon-pulse';
            elements.hudWrapper.innerHTML = `
                <button class="hud-trigger ${animationPulseClass}" id="hud-toggle-open-btn" aria-label="Expand Learning HUD">
                    <i class="ph ph-compass"></i>
                    <span class="hud-trigger-text">HUD ${score}%</span>
                </button>
            `;

            // Bind toggle open click
            document.getElementById('hud-toggle-open-btn').addEventListener('click', () => {
                state.isOpen = true;
                renderHUD();
            });
        }
    }
})();
