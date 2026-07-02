use crate::ring::{Ring, TelemetryEvent};
use pyo3::prelude::*;
use std::time::Instant;

#[pyclass]
pub struct Telemetry {
    ring: Ring,
    epoch: Instant,
}

#[pymethods]
impl Telemetry {
    #[new]
    #[pyo3(signature = (capacity))]
    fn new(capacity: usize) -> Self {
        Self { ring: Ring::new(capacity), epoch: Instant::now() }
    }

    #[pyo3(signature = (kind, tensor_id, value))]
    fn record(&self, kind: u32, tensor_id: u64, value: f64) -> bool {
        let ts = self.epoch.elapsed().as_nanos() as u64;
        self.ring.record(TelemetryEvent { timestamp_ns: ts, kind, tensor_id, value })
    }

    #[pyo3(signature = (max))]
    fn drain(&self, max: usize) -> Vec<(u64, u32, u64, f64)> {
        self.ring
            .drain(max)
            .into_iter()
            .map(|e| (e.timestamp_ns, e.kind, e.tensor_id, e.value))
            .collect()
    }

    fn dropped(&self) -> u64 {
        self.ring.dropped()
    }

    fn __len__(&self) -> usize {
        self.ring.len()
    }
}

#[pymodule]
fn crp_telemetry(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Telemetry>()?;
    Ok(())
}
