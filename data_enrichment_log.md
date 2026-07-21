# Data Enrichment Log

## Task 1: Data Exploration and Enrichment

### Additions

| Record ID | Type | Description | Source | Confidence | Date Added |
|-----------|------|--------------|--------|------------|-------------|
| REC_0034 | observation | Fayda Digital ID enrollment reached 30M (Mar 2026), up from 15M (May 2025) | [Integrated Biometrics / Biometric Update](https://www.biometricupdate.com/202603/integrated-biometrics-fingerprint-scanners-facilitate-digital-id-for-inclusion-in-ethiopia) | medium | 2026-07-21 |
| EVT_0011 | event (regulation) | Fayda Mandatory for Banking Directive: all bank account holders must link Fayda ID by Dec 31, 2026 | [ID Tech Wire](https://idtechwire.com/ethiopia-mandates-national-digital-id-fayda-for-all-banking-transactions-by-2026/) | high | 2026-07-21 |
| IMP_0015 | impact_link | EVT_0011 → ACC_OWNERSHIP (ACCESS), increase, medium magnitude, 12-month lag | Documented: Cooperative Bank of Oromia opens accounts via Fayda eKYC without physical documents | medium | 2026-07-21 |

### Rationale

- **REC_0034** extends the ACC_FAYDA time series with the most recent enrollment figure available, showing enrollment nearly doubled in ~10 months (15M → 30M), which is directly relevant to forecasting ACCESS given Fayda's role as a KYC enabler.
- **EVT_0011** was added as a distinct event from EVT_0004 (Fayda Digital ID Program Rollout, Jan 2024) because it captures a *regulatory mandate* (forcing existing account holders to link IDs) rather than the *infrastructure launch* itself — these are different mechanisms with different expected effects on ACCESS.
- **IMP_0015** models the plausible channel through which this regulation could raise ACC_OWNERSHIP: easier KYC-based account opening at partner banks lowers a historical barrier to account ownership for undocumented adults.

### Considered but not added

- Latest Telebirr user count (54.84M, Jun 2025) and 4G coverage (70.8%, Jun 2025) were checked against the existing dataset and found **already present** (REC_0021, REC_0010) — not duplicated.

### Data Quality Notes

- New observation confidence set to `medium` (news source reporting a program figure, not an official audited report).
- New event confidence set to `high` (multiple corroborating regulatory/industry sources on the mandate and deadline).
