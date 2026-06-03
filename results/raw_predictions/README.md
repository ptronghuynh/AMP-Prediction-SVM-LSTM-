# Raw Predictions

This directory is reserved for paired per-sample prediction files:

- `svm_predictions.csv`
- `lstm_predictions.csv`
- `bilstm_mha_predictions.csv`

Required columns:

```text
sample_id,true_label,pred_label,pred_score
```

Do not run McNemar or DeLong tests from manually reconstructed counts. Regenerate these files from the fixed split manifest and the saved models so all methods use identical sample ordering.

