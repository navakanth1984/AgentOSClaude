use criterion::{criterion_group, criterion_main, Criterion};
use crp_telemetry::{Ring, TelemetryEvent};

fn bench_record(c: &mut Criterion) {
    let ring = Ring::new(1 << 16);
    let ev = TelemetryEvent { timestamp_ns: 42, kind: 1, tensor_id: 7, value: 0.5 };
    c.bench_function("ring_record", |b| {
        b.iter(|| {
            if !ring.record(std::hint::black_box(ev)) {
                ring.drain(1 << 15); // keep the buffer from saturating mid-bench
            }
        })
    });
}

criterion_group!(benches, bench_record);
criterion_main!(benches);
