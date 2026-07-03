# AMP-Prediction-SVM-LSTM

Reproducibility package for the revised manuscript:

**Antimicrobial Peptide Prediction from Microbial Protein Sequences: Evaluation of Descriptor-Based and Recurrent Neural Models**

Repository URL: https://github.com/ptronghuynh/AMP-Prediction-SVM-LSTM-

The repository is organized to support reviewer audit of the reported AMP/non-AMP classification experiments without modifying the manuscript text. It contains the balanced 6,000-record held-out feature file, split manifests with sequence hashes, internal and external result tables, leakage-check outputs, figure files, and scripts used to regenerate the summary artifacts.

## Repository layout

```text
AMP-Prediction-SVM-LSTM/
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── data/
│   ├── Data_6kGoc/features.csv
│   ├── splits/
│   └── README_data.md
├── notebooks/
├── scripts/
├── results/
└── figures/
```

## Main reported results

Internal held-out evaluation uses a balanced 6,000-record feature table with 3,000 AMP and 3,000 non-AMP records.

| Model | Test n | Accuracy | 95% CI | Macro F1 | AUC-ROC | Note |
|---|---:|---:|---:|---:|---:|---|
| SVM-combined | 6,000 | 0.9700 | 0.9654-0.9740 | 0.9700 | 0.9962 | Sequence-index plus 126 GPSD descriptors |
| LSTM-combined | 6,000 | 0.9550 | 0.9495-0.9600 | 0.9550 | Not retained | Two-branch sequence plus GPSD model |
| BiLSTM-MHA | 6,000 | approx. 0.9700 | 0.9654-0.9740 | approx. 0.9700 | Not retained | Bidirectional recurrent model with multi-head attention |

External validation is reported for the LSTM-combined pipeline only on AMPDiscover, DDBL, EMBL, RefSeq, SSFGM, and XU.

## Reproduce summary artifacts

Create an environment and install the dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Regenerate result tables and figures:

```bash
python scripts/make_result_tables.py
```

Regenerate split manifests and leakage summaries from the local source release, when the source release is available next to this repository:

```bash
python scripts/audit_sequence_overlap.py --build-manifests
```

Audit the committed manifests only:

```bash
python scripts/audit_sequence_overlap.py
```

## Notes for reviewers

- `data/Data_6kGoc/features.csv` is the held-out feature matrix used for the internal classification-report artifacts.
- `data/splits/*.csv` contains sequence hashes and manifest metadata, not large raw source databases. During manifest generation, exact sequence hashes already present in the held-out feature table are removed from the train/validation manifests unless `--keep-heldout-overlap` is explicitly passed.
- The large raw GenBank/non-GenBank files and saved model binaries are not included in this minimal GitHub package because of normal GitHub size limits. They should be archived through Git LFS, Zenodo, or an institutional repository if the journal requires full binary model deposition.
- `scripts/audit_sequence_overlap.py` reports exact SHA-256 sequence-hash overlap among committed manifests. It does not claim experimental wet-lab validation.
