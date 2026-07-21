# Synthetic data provenance

OPSIQ ships only synthetic demonstration evidence. It is not a production operational record set.

## Incident-history recovery

The original `backend/data/synthetic/incident_history.json` artifact was corrupt. Its SHA-256 is:

`2052CBD0B46C7B378052840D01E8CBE18E3358B515F48646E0ECA87CAC393068`

Binary corruption begins inside the twelfth object, `INC-2025-012`, immediately after its `failure_mode` field (approximately byte 3,861 in the 13,206-byte source artifact). The first 11 objects, `INC-2025-001` through `INC-2025-011`, are independently complete JSON records. Runtime data contains only those 11 records. No damaged fields were inferred, repaired, or regenerated.

The exact original artifact is retained at `backend/tests/fixtures/incident_history_corrupted.original` for regression testing and audit provenance. It is never used by production runtime analysis.

## Inspection normalization

The six pre-existing inspection rows are labelled as synthetic `OISD-118` evidence with stable IDs `INS-OISD118-001` through `INS-OISD118-006`. Severity, evidence-source and remediation fields make the existing demonstration findings explicit. No Factory Act, DGMS or PESO evidence is present or claimed.

## Work-order normalization

The 50 pre-existing synthetic work orders were normalized to BOM-safe UTF-8 JSON without changing their substantive record values. Runtime loaders validate explicit schemas and fail closed on malformed or corrupt files.
