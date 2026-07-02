import hashlib
from dataclasses import dataclass
from types import MappingProxyType

from research.compiler.parser import CompilerError, CompilerStage
from research.compiler.canonicalizer import jcs_serialize
from research.compiler.semantic import SemanticIR

class TemplateError(CompilerError):
    """Template substitution failure (IR:TMP_005)."""
    pass

@dataclass(frozen=True, slots=True)
class CompilationPlan:
    template_id: str
    template_version: str
    template_abi: int
    template_hash: str
    registry_version: int
    registry_hash: str

@dataclass(frozen=True, slots=True)
class GeneratedPlugin:
    plugin_source: str
    plan: CompilationPlan

# ---------------------------------------------------------------------------
# Audited Template Definitions
# ---------------------------------------------------------------------------

UNIFORM_TEMPLATE = '''import numpy as np

class {name}:
    def __init__(self):
        self.bits = {bits}
        self.symmetric = {symmetric}

    def analyze(self, tensor):
        return {{
            "shape": tuple(tensor.shape),
            "sparsity": float(np.mean(tensor == 0.0)),
            "variance": float(np.var(tensor)),
            "memory_bytes": int(tensor.nbytes)
        }}

    def estimate(self, stats, hw):
        ratio = 32 / self.bits
        return {{
            "memory_bytes": int(stats["memory_bytes"] // ratio),
            "latency_ms": 0.05
        }}

    def convert(self, tensor_data):
        arr = np.array(tensor_data)
        min_val, max_val = arr.min(), arr.max()
        scale = (max_val - min_val) / 255.0 if max_val > min_val else 1.0
        zero_point = int(-min_val / scale) if scale > 0 else 0
        quant = np.clip(np.round(arr / scale) + zero_point, 0, 255).astype(np.uint8)
        return {{"quantized": quant.tolist(), "scale": scale, "zero_point": zero_point}}

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
'''

BLOCK_TEMPLATE = '''import numpy as np

class {name}:
    def __init__(self):
        self.block_size = {block_size}
        self.bits = {bits}
        self.symmetric = {symmetric}

    def analyze(self, tensor):
        return {{
            "shape": tuple(tensor.shape),
            "sparsity": float(np.mean(tensor == 0.0)),
            "variance": float(np.var(tensor)),
            "memory_bytes": int(tensor.nbytes)
        }}

    def estimate(self, stats, hw):
        ratio = 32 / self.bits
        return {{
            "memory_bytes": int(stats["memory_bytes"] // ratio),
            "latency_ms": 0.1
        }}

    def convert(self, tensor):
        arr = np.array(tensor)
        h, w = arr.shape
        num_blocks = w // self.block_size
        quantized = []
        scales = []
        zero_points = []
        for i in range(h):
            row_quant = []
            row_scales = []
            row_zps = []
            for b in range(num_blocks):
                block = arr[i, b * self.block_size : (b + 1) * self.block_size]
                min_val, max_val = block.min(), block.max()
                scale = (max_val - min_val) / 255.0 if max_val > min_val else 1.0
                zp = int(-min_val / scale) if scale > 0 else 0
                q = np.clip(np.round(block / scale) + zp, 0, 255).astype(np.uint8)
                row_quant.extend(q.tolist())
                row_scales.append(scale)
                row_zps.append(zp)
            quantized.append(row_quant)
            scales.append(row_scales)
            zero_points.append(row_zps)
        return {{"quantized": quantized, "scales": scales, "zero_points": zero_points, "shape": [h, w]}}

    def execute(self, converted, queries):
        h, w = converted["shape"]
        restored = np.zeros((h, w))
        quantized = converted["quantized"]
        scales = converted["scales"]
        zero_points = converted["zero_points"]
        num_blocks = w // self.block_size
        for i in range(h):
            for b in range(num_blocks):
                q = np.array(quantized[i][b * self.block_size : (b + 1) * self.block_size])
                zp = zero_points[i][b]
                scale = scales[i][b]
                restored[i, b * self.block_size : (b + 1) * self.block_size] = (q - zp) * scale
        return restored @ queries.T

    def restore(self, converted):
        h, w = converted["shape"]
        restored = np.zeros((h, w))
        quantized = converted["quantized"]
        scales = converted["scales"]
        zero_points = converted["zero_points"]
        num_blocks = w // self.block_size
        for i in range(h):
            for b in range(num_blocks):
                q = np.array(quantized[i][b * self.block_size : (b + 1) * self.block_size])
                zp = zero_points[i][b]
                scale = scales[i][b]
                restored[i, b * self.block_size : (b + 1) * self.block_size] = (q - zp) * scale
        return restored.tolist()
'''

THRESHOLD_TEMPLATE = '''import numpy as np

class {name}:
    def __init__(self):
        self.threshold = {threshold}
        self.relative = {relative}

    def analyze(self, tensor):
        return {{
            "shape": tuple(tensor.shape),
            "sparsity": float(np.mean(tensor == 0.0)),
            "variance": float(np.var(tensor)),
            "memory_bytes": int(tensor.nbytes)
        }}

    def estimate(self, stats, hw):
        return {{
            "memory_bytes": int(stats["memory_bytes"] * (1.0 - self.threshold)),
            "latency_ms": 0.08
        }}

    def convert(self, tensor):
        arr = np.array(tensor)
        if self.relative:
            var = np.var(arr)
            abs_thresh = self.threshold * np.sqrt(var)
        else:
            abs_thresh = self.threshold
        sparse_mask = np.abs(arr) >= abs_thresh
        sparse_val = arr * sparse_mask
        return {{"values": sparse_val.tolist(), "shape": list(arr.shape)}}

    def execute(self, converted, queries):
        val = np.array(converted["values"])
        return val @ queries.T

    def restore(self, converted):
        return converted["values"]
'''

SVD_TEMPLATE = '''import numpy as np

class {name}:
    def __init__(self):
        self.target_rank = {target_rank}

    def analyze(self, tensor):
        return {{
            "shape": tuple(tensor.shape),
            "sparsity": float(np.mean(tensor == 0.0)),
            "variance": float(np.var(tensor)),
            "memory_bytes": int(tensor.nbytes)
        }}

    def estimate(self, stats, hw):
        h, w = stats["shape"]
        orig_bytes = stats["memory_bytes"]
        comp_elements = self.target_rank * (h + w)
        ratio = comp_elements / (h * w)
        return {{
            "memory_bytes": int(orig_bytes * ratio),
            "latency_ms": 0.15
        }}

    def convert(self, tensor):
        arr = np.array(tensor)
        u, s, vt = np.linalg.svd(arr, full_matrices=False)
        ur = u[:, :self.target_rank]
        sr = s[:self.target_rank]
        vtr = vt[:self.target_rank, :]
        return {{"u_s": (ur * sr).tolist(), "vt": vtr.tolist(), "shape": list(arr.shape)}}

    def execute(self, converted, queries):
        us = np.array(converted["u_s"])
        vt = np.array(converted["vt"])
        restored = us @ vt
        return restored @ queries.T

    def restore(self, converted):
        us = np.array(converted["u_s"])
        vt = np.array(converted["vt"])
        return (us @ vt).tolist()
'''

# ---------------------------------------------------------------------------
# Immutable Strategy Registry & Hashing
# ---------------------------------------------------------------------------

StrategyRegistry = MappingProxyType({
    "quantization.uniform.v1": ("TEMPLATE-001", "1.0.0", 1, UNIFORM_TEMPLATE),
    "quantization.block.v1": ("TEMPLATE-002", "1.0.0", 1, BLOCK_TEMPLATE),
    "sparsity.threshold.v1": ("TEMPLATE-003", "1.0.0", 1, THRESHOLD_TEMPLATE),
    "decomposition.svd.v1": ("TEMPLATE-004", "1.0.0", 1, SVD_TEMPLATE)
})

# Compute registry_hash strictly based on RFC 8785 list serialization:
# [[template_id, version, abi, key, template_hash_hex], ...] sorted by template_id
REGISTRY_VERSION = 1

def _compute_registry_hash() -> str:
    registry_list = []
    for key, (t_id, t_ver, t_abi, source) in StrategyRegistry.items():
        t_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        registry_list.append([t_id, t_ver, t_abi, key, t_hash])
    
    # Sort by template_id (first item)
    registry_list.sort(key=lambda x: x[0])
    
    serialized = jcs_serialize(registry_list)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

REGISTRY_HASH = _compute_registry_hash()

# ---------------------------------------------------------------------------
# Template Generation Execution Stage
# ---------------------------------------------------------------------------

class TemplateStage(CompilerStage[SemanticIR, GeneratedPlugin]):
    def execute(self, input: SemanticIR) -> GeneratedPlugin:
        """Populate the audited template matching the strategy definition.
        
        Raises TemplateError if generation fails.
        """
        strategy = input.strategy_key
        data = input.data
        name = data["name"]
        parameters = data["parameters"]

        if strategy not in StrategyRegistry:
            raise TemplateError(f"Strategy {strategy} not registered.")

        t_id, t_ver, t_abi, source = StrategyRegistry[strategy]
        t_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()

        try:
            # Strategy specific replacements
            if strategy == "quantization.uniform.v1":
                code = source.format(
                    name=name,
                    bits=int(parameters["quantization_bits"]),
                    symmetric="True" if parameters["symmetric"] else "False"
                )
            elif strategy == "quantization.block.v1":
                code = source.format(
                    name=name,
                    block_size=int(parameters["block_size"]),
                    bits=int(parameters["quantization_bits"]),
                    symmetric="True" if parameters["symmetric"] else "False"
                )
            elif strategy == "sparsity.threshold.v1":
                code = source.format(
                    name=name,
                    threshold=float(parameters["threshold"]),
                    relative="True" if parameters["relative"] else "False"
                )
            elif strategy == "decomposition.svd.v1":
                code = source.format(
                    name=name,
                    target_rank=int(parameters["target_rank"])
                )
            else:
                raise TemplateError(f"Unhandled strategy code gen: {strategy}")

            plan = CompilationPlan(
                template_id=t_id,
                template_version=t_ver,
                template_abi=t_abi,
                template_hash=t_hash,
                registry_version=REGISTRY_VERSION,
                registry_hash=REGISTRY_HASH
            )

            return GeneratedPlugin(plugin_source=code, plan=plan)

        except Exception as exc:
            raise TemplateError(f"Template populate failure: {exc}") from exc
