# Data

`Data_6kGoc/features.csv` is the balanced held-out feature file used for internal reporting in the revised manuscript.

The file contains:

- `ID`: peptide/protein accession identifier.
- `Label`: `AMP` or `nAMP`.
- `Sequence`: amino-acid sequence.
- 126 GPSD descriptor features after feature selection.

The full raw GenBank/notGenBank CSV and FASTA files are too large for normal GitHub storage and should be archived through Git LFS or Zenodo.

`splits/test_ids.csv` records the sample order for the 6,000 held-out samples. `train_ids.csv` and `validation_ids.csv` are templates until the exact training split manifest is exported from the original notebooks.

