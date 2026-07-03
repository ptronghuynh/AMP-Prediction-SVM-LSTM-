# AMP-Prediction-SVM-LSTM

Source code and analysis files for the manuscript:

**Antimicrobial Peptide Prediction from Microbial Protein Sequences: Evaluation of Descriptor-Based and Recurrent Neural Models**

Repository URL: https://github.com/ptronghuynh/AMP-Prediction-SVM-LSTM

The repository contains the balanced 6,000-record held-out feature file, split manifests with sequence hashes, internal and external result tables, leakage-check outputs, figure files, and analysis scripts for AMP/non-AMP classification.

## Repository layout

```text
AMP-Prediction-SVM-LSTM/
|-- README.md
|-- requirements.txt
|-- LICENSE
|-- .gitignore
|-- data/
|   |-- Data_6kGoc/features.csv
|   |-- splits/
|   `-- README_data.md
|-- notebooks/
|-- scripts/
|-- results/
`-- figures/
```

## Main reported results

Internal held-out evaluation uses a balanced 6,000-record feature table with 3,000 AMP and 3,000 non-AMP records.

| Model | Test n | Accuracy | 95% CI | Macro F1 | Note |
|---|---:|---:|---:|---:|---|
| SVM-combined | 6,000 | 0.9700 | 0.9654-0.9740 | 0.9700 | Sequence-index plus 126 GPSD descriptors; AUC-ROC = 0.9962 |
| LSTM-combined | 6,000 | 0.9550 | 0.9495-0.9600 | 0.9550 | Two-branch sequence plus GPSD model |
| BiLSTM-MHA | 6,000 | approx. 0.9700 | 0.9654-0.9740 | approx. 0.9700 | Bidirectional recurrent model with multi-head attention |

External validation is reported for the LSTM-combined pipeline only on AMPDiscover, DDBL, EMBL, RefSeq, SSFGM, and XU.

## Usage

Create an environment and install the dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create result tables:

```bash
python scripts/make_result_tables.py
```

Create split manifests and leakage summaries:

```bash
python scripts/audit_sequence_overlap.py --build-manifests
```

Audit the existing manifests:

```bash
python scripts/audit_sequence_overlap.py
```

## Data files

- `data/Data_6kGoc/features.csv` is the held-out feature matrix used for the internal classification-report artifacts.
- `data/splits/*.csv` contains sequence hashes and split metadata.
- `results/leakage_checks/*.csv` contains exact sequence-hash overlap summaries.
- `figures/` contains the manuscript figure files.
