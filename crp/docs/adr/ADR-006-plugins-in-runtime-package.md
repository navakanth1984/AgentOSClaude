# ADR-006: Phase-0 plugins live inside the crp_runtime package

**Status:** Accepted 2026-07-02

**Decision:** Dense and Int8 ship as modules of `crp_runtime`
(`representations.py`, `plugins_int8.py`), not as separately packaged
plugins under `crp/plugins/`.

**Alternatives:** entry-point-based plugin discovery (premature because loader,
sandboxing, and signing are future RFCs); separate pip packages (extra overhead
with zero external consumers in Phase 0).

**Trade-offs:** in-package plugins cannot be third-party-installed yet;
acceptable because the plugin interface is already frozen, so relocation later
is mechanical.
