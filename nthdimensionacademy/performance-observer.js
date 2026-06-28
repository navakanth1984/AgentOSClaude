/**
 * Nth Dimension Academy - Core Web Vitals & Performance Observer
 * Logs crucial web performance metrics (FCP, LCP, CLS, INP) and resource timings
 * to console for baseline telemetry auditing.
 */

(function () {
    const METRICS = {
        fcp: null,
        lcp: null,
        cls: 0,
        inp: null
    };

    // Initialize PerformanceObservers on load
    document.addEventListener('DOMContentLoaded', () => {
        setupObservers();
    });

    function setupObservers() {
        // 1. First Contentful Paint (FCP)
        try {
            const fcpObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                entries.forEach((entry) => {
                    if (entry.name === 'first-contentful-paint') {
                        METRICS.fcp = Math.round(entry.startTime);
                        logMetric('FCP (First Contentful Paint)', `${METRICS.fcp}ms`, getRating(METRICS.fcp, 1800, 3000));
                        fcpObserver.disconnect();
                    }
                });
            });
            fcpObserver.observe({ type: 'paint', buffered: true });
        } catch (e) {
            console.warn('FCP observer not supported:', e);
        }

        // 2. Largest Contentful Paint (LCP)
        try {
            const lcpObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                entries.forEach((entry) => {
                    METRICS.lcp = Math.round(entry.startTime);
                    logMetric('LCP (Largest Contentful Paint)', `${METRICS.lcp}ms`, getRating(METRICS.lcp, 2500, 4000), {
                        element: entry.element,
                        url: entry.url,
                        size: entry.size
                    });
                });
            });
            lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
        } catch (e) {
            console.warn('LCP observer not supported:', e);
        }

        // 3. Cumulative Layout Shift (CLS)
        try {
            const clsObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                entries.forEach((entry) => {
                    if (!entry.hadRecentInput) {
                        METRICS.cls += entry.value;
                        // Limit to 4 decimal places
                        const formattedCls = parseFloat(METRICS.cls.toFixed(4));
                        logMetric('CLS (Cumulative Layout Shift)', formattedCls, getRating(METRICS.cls, 0.1, 0.25));
                    }
                });
            });
            clsObserver.observe({ type: 'layout-shift', buffered: true });
        } catch (e) {
            console.warn('CLS observer not supported:', e);
        }

        // 4. Interaction to Next Paint (INP)
        try {
            const inpObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                entries.forEach((entry) => {
                    METRICS.inp = Math.round(entry.duration);
                    logMetric('INP (Interaction to Next Paint)', `${METRICS.inp}ms`, getRating(METRICS.inp, 200, 500), {
                        interactionType: entry.name,
                        target: entry.target
                    });
                });
            });
            inpObserver.observe({ type: 'first-input', buffered: true });
            // Observe overall event timings for modern browsers
            inpObserver.observe({ type: 'event', durationThreshold: 16, buffered: true });
        } catch (e) {
            console.warn('INP observer not supported:', e);
        }

        // 5. Heavy Resource Loading Audit (Assets over 500KB)
        try {
            const resourceObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                entries.forEach((entry) => {
                    const transferSizeKB = Math.round(entry.transferSize / 1024);
                    if (entry.entryType === 'resource' && (transferSizeKB > 500 || entry.duration > 1500)) {
                        console.warn(
                            `[Perf Audit] Heavy resource detected: ${entry.name.split('/').pop()} ` +
                            `(${transferSizeKB}KB) loaded in ${Math.round(entry.duration)}ms ` +
                            `(Initiator: ${entry.initiatorType})`
                        );
                    }
                });
            });
            resourceObserver.observe({ type: 'resource', buffered: true });
        } catch (e) {
            console.warn('Resource observer not supported:', e);
        }
    }

    function getRating(value, goodBound, poorBound) {
        if (value <= goodBound) return { label: 'GOOD', color: '#10b981' };
        if (value <= poorBound) return { label: 'NEEDS IMPROVEMENT', color: '#f59e0b' };
        return { label: 'POOR', color: '#ef4444' };
    }

    function logMetric(name, value, rating, meta) {
        // Dispatch Custom DOM Event for telemetry adapter integration
        window.dispatchEvent(new CustomEvent('academy:performanceMetric', {
            detail: {
                metric: name,
                value: value,
                rating: rating.label
            }
        }));

        // Output styled logs on localhost/dev
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log(
                `%c[Metric] ${name}: %c${value} %c(${rating.label})`,
                'color: #94a3b8; font-weight: 500;',
                'color: #3b82f6; font-weight: bold; font-family: monospace;',
                `color: ${rating.color}; font-weight: bold;`,
                meta || ''
            );
        }
    }
})();
