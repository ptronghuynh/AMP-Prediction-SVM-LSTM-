# AMP Prediction with SVM, LSTM, and BiLSTM-MHA

This repository accompanies the manuscript:

**Antimicrobial Peptide Prediction from Microbial Protein Sequences: Evaluation of Descriptor-Based and Recurrent Neural Models**

The package contains source-code notebooks, a balanced 6,000-sample held-out feature file, saved model artifacts, and result tables for AMP/non-AMP classification using:

- SVM-combined: fixed-length sequence indices plus 126 GPSD descriptors.
- LSTM-combined: two-branch sequence plus GPSD model.
- BiLSTM-MHA: bidirectional LSTM with multi-head attention.

Repository URL: https://github.com/ptronghuynh/AMP-Prediction-SVM-LSTM-

## Structure

```text
AMP-Prediction-SVM-LSTM/
|-- README.md
|-- requirements.txt
|-- environment.yml
|-- LICENSE
|-- CITATION.cff
|-- data/
|   |-- Data_6kGoc/features.csv
|   |-- external/
|   `-- splits/
|-- notebooks/
|   |-- 01_train_svm_combined.ipynb
|   |-- 02_train_lstm_combined.ipynb
|   |-- 03_train_bilstm_mha.ipynb
|   |-- 04_external_validation.ipynb
|   |-- 05_statistical_tests.ipynb
|   `-- external/
|-- src/
|-- models/
|-- results/
`-- figures/
```

## Main Results

Internal held-out evaluation uses 6,000 balanced samples: 3,000 AMP and 3,000 non-AMP.

| Model | Test n | Accuracy | Macro F1 | Verification note |
|---|---:|---:|---:|---|
| SVM-combined | 6,000 | 0.97 | 0.97 | AUC 0.9962; approximate FP 60, FN 120 |
| LSTM-combined | 6,000 | 0.95 | 0.95 | Approximate FP 120, FN 150; AUC not used for ranking |
| BiLSTM-MHA | 6,000 | 0.97 | 0.97 | Stronger neural baseline; AUC not used for ranking |

External validation of the LSTM pipeline is summarized in `results/external_validation_metrics.csv` and in the notebooks under `notebooks/external/`.

## Reproducibility Notes

- The held-out 6,000-sample feature matrix is available at `data/Data_6kGoc/features.csv`.
- The public repository should use Git LFS or Zenodo for very large raw GenBank/notGenBank CSV and FASTA files.
- The current `data/splits/test_ids.csv` records the held-out evaluation ordering from `Data_6kGoc/features.csv`.
- `data/splits/train_ids.csv` and `data/splits/validation_ids.csv` are templates until the original training split manifest is exported from the training notebooks.
- Raw paired predictions are represented as templates in `results/raw_predictions/`. Formal McNemar, bootstrap confidence intervals, and DeLong tests should be run only after raw per-sample predictions are regenerated from the fixed split manifest.

## Quick Start

```bash
conda env create -f environment.yml
conda activate amp-prediction
python -m pip install -r requirements.txt
```

Open the notebooks in order:

1. `notebooks/01_train_svm_combined.ipynb`
2. `notebooks/02_train_lstm_combined.ipynb`
3. `notebooks/03_train_bilstm_mha.ipynb`
4. `notebooks/04_external_validation.ipynb`
5. `notebooks/05_statistical_tests.ipynb`
