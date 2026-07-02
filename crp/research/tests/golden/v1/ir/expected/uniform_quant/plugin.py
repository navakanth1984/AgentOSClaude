import numpy as np

class UniformQuant:
    def __init__(self):
        self.bits = 8
        self.symmetric = True

    def analyze(self, tensor):
        return {
            "shape": tuple(tensor.shape),
            "sparsity": float(np.mean(tensor == 0.0)),
            "variance": float(np.var(tensor)),
            "memory_bytes": int(tensor.nbytes)
        }

    def estimate(self, stats, hw):
        ratio = 32 / self.bits
        return {
            "memory_bytes": int(stats["memory_bytes"] // ratio),
            "latency_ms": 0.05
        }

    def convert(self, tensor_data):
        arr = np.array(tensor_data)
        min_val, max_val = arr.min(), arr.max()
        scale = (max_val - min_val) / 255.0 if max_val > min_val else 1.0
        zero_point = int(-min_val / scale) if scale > 0 else 0
        quant = np.clip(np.round(arr / scale) + zero_point, 0, 255).astype(np.uint8)
        return {"quantized": quant.tolist(), "scale": scale, "zero_point": zero_point}

    def execute(self, converted, queries):
        quant = np.array(converted["quantized"])
        scale = converted["scale"]
        zero_point = converted["zero_point"]
        restored = (quant - zero_point) * scale
        return restored @ queries.T

    def restore(self, converted):
        quant = np.array(converted["quantized"])
        scale = converted["scale"]
        zero_point = converted["zero_point"]
        return ((quant - zero_point) * scale).tolist()
