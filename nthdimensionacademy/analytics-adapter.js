/**
 * Nth Dimension Academy - Unified Analytics Adapter
 * Decouples the UI learning HUD from analytics platforms.
 * Listens to custom academy events, applies batching/throttling to minimize noise,
 * and routes them safely to GA4 (gtag) and Vercel Web Analytics.
 */

(function () {
    const EVENTS = {
        SECTION_VISITED: 'academy:sectionVisited',
        MILESTONE_UNLOCKED: 'academy:milestoneUnlocked',
        CURIOSITY_CHANGED: 'academy:curiosityChanged',
        PERFORMANCE_METRIC: 'academy:performanceMetric'
    };

    const ADAPTER_CONFIG = {
        BATCH_FLUSH_INTERVAL_MS: 4000, // Batch and flush every 4 seconds
        DEBUG: false // Logs events to console when enabled
    };

    // Telemetry buffer queue
    let eventBuffer = [];
    let flushTimeout = null;

    // Initialize Analytics adapter on load
    document.addEventListener('DOMContentLoaded', () => {
        setupEventListeners();
        logDebug('Analytics adapter initialized.');
    });

    function setupEventListeners() {
        // 1. Monitor Section Visits (Batched)
        window.addEventListener(EVENTS.SECTION_VISITED, (e) => {
            const section = e.detail?.section;
            if (!section) return;

            queueEvent('section_visited', {
                section_name: section
            });
        });

        // 2. Monitor Curiosity Score/Rank Changes (Batched & debounced)
        window.addEventListener(EVENTS.CURIOSITY_CHANGED, (e) => {
            const score = e.detail?.index;
            const rank = e.detail?.rank;
            if (score === undefined) return;

            // Queue the score change (it will overwrite older scores in the same batch buffer)
            queueEvent('curiosity_score_update', {
                curiosity_index: score,
                explorer_rank: rank
            }, true); // Overwrite existing scores in buffer to only send the latest
        });

        // 3. Monitor Milestone Unlocks (Critical: Flushed immediately)
        window.addEventListener(EVENTS.MILESTONE_UNLOCKED, (e) => {
            const milestone = e.detail?.milestone;
            const desc = e.detail?.description;
            if (!milestone) return;

            // Log and flush immediately
            sendEventDirect('milestone_unlocked', {
                milestone_name: milestone,
                milestone_description: desc
            });
        });

        // 4. Monitor Performance Metrics (Batched)
        window.addEventListener(EVENTS.PERFORMANCE_METRIC, (e) => {
            const metricName = e.detail?.metric;
            const val = e.detail?.value;
            const rating = e.detail?.rating;
            if (!metricName) return;

            queueEvent('performance_metric', {
                metric_name: metricName,
                metric_value: val,
                metric_rating: rating
            });
        });

        // 5. Flush queue immediately on page exit or hide to avoid losing short session data
        window.addEventListener('pagehide', flushQueue);
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                flushQueue();
            }
        });
    }

    /**
     * Helper to enrich event parameters with page context.
     */
    function enrichParameters(params) {
        const connectionType = navigator.connection ? navigator.connection.effectiveType : 'unknown';
        return {
            ...params,
            page_path: window.location.pathname,
            viewport_width: window.innerWidth,
            connection_type: connectionType,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Queues an event for batched delivery.
     * @param {string} eventName 
     * @param {object} params 
     * @param {boolean} overwriteSimilar 
     */
    function queueEvent(eventName, params, overwriteSimilar = false) {
        logDebug(`Queueing event: ${eventName}`, params);

        if (overwriteSimilar) {
            // Remove any previous occurrences of this event type in the buffer to only keep the latest state
            eventBuffer = eventBuffer.filter(e => e.name !== eventName);
        }

        eventBuffer.push({
            name: eventName,
            params: enrichParameters(params)
        });

        // Reset and schedule the batch flush
        if (flushTimeout) {
            clearTimeout(flushTimeout);
        }
        flushTimeout = setTimeout(flushQueue, ADAPTER_CONFIG.BATCH_FLUSH_INTERVAL_MS);
    }

    /**
     * Flush all queued events to Google Analytics 4 and Vercel Analytics.
     */
    function flushQueue() {
        if (eventBuffer.length === 0) return;

        logDebug(`Flushing event buffer (${eventBuffer.length} events)...`, eventBuffer);

        // Process all events in the queue
        eventBuffer.forEach(evt => {
            sendToGA4(evt.name, evt.params);
            sendToVercel(evt.name, evt.params);
        });

        // Clear buffer
        eventBuffer = [];
        flushTimeout = null;
    }

    /**
     * Direct flush for high-value conversion events (Milestones).
     */
    function sendEventDirect(eventName, params) {
        logDebug(`Direct sending critical event: ${eventName}`, params);
        
        sendToGA4(eventName, enrichParameters(params));
        sendToVercel(eventName, enrichParameters(params));
    }

    // --- GOOGLE ANALYTICS 4 CONNECTOR ---
    function sendToGA4(eventName, params) {
        if (typeof window.gtag === 'function') {
            window.gtag('event', eventName, params);
        }
    }

    // --- VERCEL WEB ANALYTICS CONNECTOR ---
    function sendToVercel(eventName, params) {
        // Vercel Analytics uses window.va for custom event dispatches
        if (typeof window.va === 'function') {
            window.va('event', { name: eventName, data: params });
        }
    }

    function logDebug(message, data) {
        if (ADAPTER_CONFIG.DEBUG || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log(`[Telemetry Adapter] ${message}`, data || '');
        }
    }
})();
