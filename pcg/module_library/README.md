# Independent offline Module library

Default store: `pcg/module_library/store/candidates/`. Existing documents, cases and records are relocated byte-for-byte; this is not new certification or a production promotion.

- `library.py`: candidate records, scoped evidence and withdrawal checks. No Map enrollment/retrieval methods.
- `matching.py`: exact matching for existing offline recipe requests. Family/count/dimensions here describe the caller's local recipe, never a general future Map contract.
- `validate_document.mjs`: canonical document validation only; no layout/query bridge.
- `paths.py` and `relocations.json`: checksum-bound historical **file** references. No old directory, import alias, live old root discovery, automatic restore or algorithm fallback.
- Workshop's existing `WorkshopLibrary` extends multi-route records. Candidate, human quality and production status stay separate.

Historical Map-specific records live under `archive/mapgen-failed/library/` and cannot be used as a candidate root. The new Map repository must consume an explicitly versioned publication rather than these implementation modules.

Run `python3 -m pcg.module_library.audit` and `npm run check:modules` from the repository root.
