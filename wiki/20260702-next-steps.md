# Next Steps – Validator Research (2026‑07‑02)

**Context**: This session focused on reviewing the `HostKernel` validator orchestration, examining `ProdValidator` and `MalformedValidator`, and planning architectural refinements for the `host_management/contracts/runtime.py` layer.

## Immediate Action Items
1. **Finalize `wiki/20260702-next-steps.md`**
   - Ensure the hand‑off captures the current understanding of validator lifecycle, registration flow, and identified gaps.
   - Add explicit links to the examined source files:
     - [prod_validator.py](file:///C:/Users/navka/navakanth001/host_management/validators/prod_validator.py)
     - [malformed.py](file:///C:/Users/navka/navakanth001/host_management/validators/malformed.py)
     - [kernel.py](file:///C:/Users/navka/navakanth001/host_management/kernel.py)
2. **Continue investigation into validator registration**
   - Locate the `ValidatorRegistry` implementation and verify how validators are discovered (e.g., entry‑points, decorators, or explicit imports).
   - Determine whether metadata validation (e.g., required fields, version compatibility) is performed during registration.
3. **Add tests for malformed validator handling**
   - Extend `tests/test_contracts_runtime.py` or create a new test suite that exercises failure paths when a validator raises errors during `initialize`, `check`, or `cleanup`.
   - Validate that `HostKernel` records the exception and continues processing remaining validators.
4. **Review and possibly extend the runtime contract**
   - Confirm that `ValidatorState` enum and `ExecutionResult` dataclass are defined in `host_management/contracts/runtime.py`.
   - Ensure they are dependency‑light and re‑export public models without duplication.
5. **Update CI gate**
   - Add the new compatibility tests to the CI pipeline to enforce API stability before merging.

## Longer‑Term Considerations
- **State machine formalisation**: Implement the validator lifecycle state machine (NEW → INITIALIZED → RUNNING → …) as part of the contract.
- **Typed status fields**: Replace string status fields with enums (`ValidationStatus`) throughout the contracts.
- **Provenance model**: Add an immutable `Provenance` record to capture validator execution metadata (timestamps, version, outcome).

---
*Prepared for the next agent to continue the work.*
