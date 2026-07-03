# Data description

## Held-out feature matrix

`data/Data_6kGoc/features.csv` contains the balanced 6,000-record held-out feature matrix used for the internal SVM-combined, LSTM-combined, and BiLSTM-MHA summary tables.

Expected columns:

- `ID`: accession or record identifier.
- `Label`: `AMP` or `nAMP`.
- `Sequence`: amino-acid sequence.
- GPSD descriptor columns: 126 physicochemical descriptor features.

## Split manifests

The files in `data/splits/` are audit manifests. They store normalized labels, sequence lengths, and SHA-256 hashes of normalized amino-acid sequences for exact-sequence overlap checks.

- `train_manifest.csv`: training split manifest.
- `validation_manifest.csv`: validation split manifest.
- `heldout_test_manifest.csv`: held-out 6,000-record feature-table manifest.
- `split_audit_summary.csv`: row counts, unique sequence-hash counts, label counts, and duplicate-hash counts per manifest.

Create manifests and leakage status files with:

```bash
python scripts/audit_sequence_overlap.py --build-manifests
```

Manifest generation excludes exact train/validation sequence hashes already present in `Data_6kGoc/features.csv`.
