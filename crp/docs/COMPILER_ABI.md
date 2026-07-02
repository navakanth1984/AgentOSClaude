# Compiler ABI Specification (v1)

This document serves as the formal interface and binary layout contract (ABI) for the Cognitive Runtime Platform (CRP) Intermediate Representation (IR) Compiler.

---

## 1. ABI Definitions

To prevent coupling between the compiler version, templates, and language schema, we distinguish each version field:

- **IR Version**: Defines the language grammar and schema parameters (e.g., `1.0.0`).
- **IR ABI**: Defines structural schema compatibility (e.g. `1` represents JSON structure schema matching `IR_SPEC.md`).
- **Compiler Version**: Tracks the implementation release of the compiler pipeline codebase (e.g., `1.0.1`).
- **Compiler ABI**: Defines output compatibility and manifest layout contract (e.g., `1` represents 6-stage parser and RFC 8785 output).
- **Template ABI**: Defines the input/output interface signatures of the populated representation plugins (e.g. `1` represents methods `analyze()`, `estimate()`, `convert()`, `execute()`, and `restore()`).

---

## 2. ABI Compatibility Matrix

The compatibility relationship across ABI releases is defined below:

| Compiler ABI | Accepts IR ABI | Emits Template ABI | Target Manifest Version |
|---|---|---|---|
| `1` | `1` | `1` | `"1.0.0"` |
| `2` | `1, 2` | `2` | `"2.0.0"` |

- **ABI Mismatch Policy**: If the incoming IR declares `ir_abi` values not supported by the active `Compiler ABI` class, the compiler MUST abort immediately during Schema Validation with error `IR:SCH_002` before evaluating any strategy-specific semantic rules.

---

## 3. Invariant Code Generation

The compiler uses a fixed set of audited code templates. Each template target has an immutable identifier, version, and ABI version.

### Template Registry (ABI 1)

| Template ID | Version | ABI | Strategy Key | Output Class Signature |
|---|---|---|---|---|
| `TEMPLATE-001` | `1.0.0` | `1` | `quantization.uniform.v1` | `class UniformQuantizer` |
| `TEMPLATE-002` | `1.0.0` | `1` | `quantization.block.v1` | `class BlockQuantizer` |
| `TEMPLATE-003` | `1.0.0` | `1` | `sparsity.threshold.v1` | `class ThresholdSparsifier` |
| `TEMPLATE-004` | `1.0.0` | `1` | `decomposition.svd.v1` | `class SVDDecomposer` |

### Template Immobility Rule
Template IDs and their signature contracts are immutable. Under ABI 1:
- A template implementation's logic can never be altered in a way that shifts output class signatures or mathematical operations.
- Formatting changes that alter bytes but not runtime behavior are permitted only under a template minor version bump (e.g. `1.0.1`), but this will change `template_hash` and `plugin_hash`.
- Behavior-changing modifications require a new Template ID (e.g. `TEMPLATE-005`).

---

## 4. Output Manifest Schema

Every successful compilation produces a deterministic build manifest file named `manifest.json`.

### Required Fields

| Field Name | Type | Value / Description |
|---|---|---|
| `manifest_version` | `string` | `"1.0.0"` |
| `compiler_pipeline` | `string` | `"IRCompiler-v1"` |
| `compiler_abi` | `integer` | `1` |
| `compiler_version` | `string` | Exact compiler software version |
| `ir_version` | `string` | Derived from input IR |
| `ir_abi` | `integer` | Derived from input IR |
| `ir_hash` | `string` | SHA256 of canonicalized IR JSON |
| `template_id` | `string` | Immutable template identifier matching strategy |
| `template_version` | `string` | Version of the populated template |
| `template_abi` | `integer` | ABI of the populated template |
| `template_hash` | `string` | SHA256 of template source before substitution |
| `registry_version` | `integer` | `1` |
| `registry_hash` | `string` | SHA256 of the StrategyRegistry structural metadata |
| `plugin_hash` | `string` | SHA256 of generated `plugin.py` code |
| `manifest_hash` | `string` | SHA256 of manifest content |
| `generated_at` | `string` | ISO 8601 UTC timestamp (informational only) |
| `generator` | `string` | `"IRCompiler"` |
| `deterministic` | `boolean` | `true` |
| `canonicalization` | `string` | `"RFC8785"` |
| `ast_guard_version` | `string` | `"1"` |

### Hash Computation Rules

1. `ir_hash` = `SHA256(RFC8785(Input_IR))`
2. `template_hash` = `SHA256(Raw_Template_String_Before_Substitution)`
3. `plugin_hash` = `SHA256(Generated_plugin.py)`
4. `registry_hash` = `SHA256(RFC8785(StrategyRegistry_Data))`
   - Standardized layout: `[[template_id, version, abi, key, template_hash_hex], ...]` sorted alphabetically by `template_id`. Notice it hashes template metadata, not raw template source strings.
5. `manifest_hash` = `SHA256(RFC8785(Manifest_Without_Hash_And_Timestamp))`
   - When computing `manifest_hash`, the fields `manifest_hash` and `generated_at` are deleted from the temporary manifest dictionary before canonicalization.

---

## 5. Error Interface ABI (Stable Taxonomy)

The compiler must map internal exceptions to stable, external error namespaces. External codes are stable APIs and must never be recycled or reassigned.

```
CompilerError (External Interface Exception Mapping)
 ├── ParserError             ──►  IR:PAR_001
 ├── SchemaError             ──►  IR:SCH_002
 ├── CanonicalizationError   ──►  IR:CAN_003
 ├── SemanticError           ──►  IR:SEM_004
 ├── TemplateError           ──►  IR:TMP_005
 └── ASTError                ──►  IR:AST_006
```

---

## 6. Future Extensions & Ignored Fields

- The compiler ABI guarantees that any JSON fields nested under `extensions` or `metadata` at the root of the IR input object are preserved byte-for-byte in the canonical IR string but are completely ignored during Schema and Semantic validation.
- Future versions of the compiler may define standard namespaces under `extensions` to negotiate capabilities without breaking backward compatibility with ABI 1.
