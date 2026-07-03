# Data description

## Held-out feature matrix

`data/Data_6kGoc/features.csv` contains the balanced 6,000-record held-out feature matrix used for the internal SVM-combined, LSTM-combined, and BiLSTM-MHA summary tables.

Expected columns:

- `ID`: accession or record identifier.
- `Label`: `AMP` or `nAMP`.
- `Sequence`: amino-acid sequence.
- GPSD descriptor columns: 126 physicochemical descriptor features.

## Split manifests

The files in `data/splits/` are audit manifests. They store normalized labels, sequence lengths, and SHA-256 hashes of normalized amino-acid sequences so reviewers can check exact-sequence overlap without requiring all raw source files in Git.

- `train_manifest.csv`: training split manifest.
- `validation_manifest.csv`: validation split manifest.
- `heldout_test_manifest.csv`: held-out 6,000-record feature-table manifest.
- `split_audit_summary.csv`: row counts, unique sequence-hash counts, label counts, and duplicate-hash counts per manifest.

Regenerate manifests and leakage status files with:

```bash
python scripts/audit_sequence_overlap.py --build-manifests
```

By default, manifest generation removes exact train/validation sequence hashes that are already present in `Data_6kGoc/features.csv`. This keeps the committed audit manifests aligned with the held-out exact-sequence screening described in the revised manuscript. Pass `--keep-heldout-overlap` only when auditing the unfiltered local source release.

The default source release path used by the script is the local repair release:

```text
../cluster_split_release/mmseqs2_docx_component_split_exact/DOCX_COMPONENT_REPAIR_EXACT_SA/DOCX_REPAIR_CLOSEFILE_DP/round_1/REPAIRED_20260207_201042.csv
```

If that source file is not available, the script audits the committed manifests.
