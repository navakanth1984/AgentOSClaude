use crossbeam::queue::ArrayQueue;
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct TelemetryEvent {
    pub timestamp_ns: u64,
    pub kind: u32,
    pub tensor_id: u64,
    pub value: f64,
}

pub struct Ring {
    queue: ArrayQueue<TelemetryEvent>,
    dropped: AtomicU64,
}

impl Ring {
    pub fn new(capacity: usize) -> Self {
        Self { queue: ArrayQueue::new(capacity), dropped: AtomicU64::new(0) }
    }

    /// Never blocks. Returns false and counts the drop when full.
    pub fn record(&self, ev: TelemetryEvent) -> bool {
        match self.queue.push(ev) {
            Ok(()) => true,
            Err(_) => {
                self.dropped.fetch_add(1, Ordering::Relaxed);
                false
            }
        }
    }

    pub fn drain(&self, max: usize) -> Vec<TelemetryEvent> {
        let mut out = Vec::with_capacity(max.min(self.queue.len()));
        while out.len() < max {
            match self.queue.pop() {
                Some(ev) => out.push(ev),
                None => break,
            }
        }
        out
    }

    pub fn dropped(&self) -> u64 {
        self.dropped.load(Ordering::Relaxed)
    }

    pub fn len(&self) -> usize {
        self.queue.len()
    }

    pub fn is_empty(&self) -> bool {
        self.queue.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ev(k: u32) -> TelemetryEvent {
        TelemetryEvent { timestamp_ns: 1, kind: k, tensor_id: 7, value: 0.5 }
    }

    #[test]
    fn record_then_drain_roundtrips() {
        let r = Ring::new(4);
        assert!(r.record(ev(1)));
        assert!(r.record(ev(2)));
        let out = r.drain(10);
        assert_eq!(out.len(), 2);
        assert_eq!(out[0].kind, 1);
        assert_eq!(out[1].kind, 2);
    }

    #[test]
    fn full_buffer_drops_and_counts_without_blocking() {
        let r = Ring::new(2);
        assert!(r.record(ev(1)));
        assert!(r.record(ev(2)));
        assert!(!r.record(ev(3))); // dropped, not blocked
        assert_eq!(r.dropped(), 1);
        assert_eq!(r.len(), 2);
    }

    #[test]
    fn drain_respects_max() {
        let r = Ring::new(8);
        for k in 0..5 { r.record(ev(k)); }
        assert_eq!(r.drain(3).len(), 3);
        assert_eq!(r.len(), 2);
    }
}
