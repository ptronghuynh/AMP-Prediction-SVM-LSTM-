"""Build split manifests and audit exact sequence-hash overlap."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_RELEASE = (
    REPO_ROOT.parent
    / "cluster_split_release"
    / "mmseqs2_docx_component_split_exact"
    / "DOCX_COMPONENT_REPAIR_EXACT_SA"
    / "DOCX_REPAIR_CLOSEFILE_DP"
    / "round_1"
    / "REPAIRED_20260207_201042.csv"
)

MANIFEST_FIELDS = [
    "split",
    "sample_id",
    "label",
    "length",
    "sequence_hash_sha256",
    "source_dataset",
    "source_row_id",
    "cluster_id",
    "component_id",
]


def normalize_sequence(sequence: str) -> str:
    return "".join(str(sequence).split()).upper()


def normalize_label(label: str) -> str:
    value = str(label).strip()
    if value.lower() in {"non-amp", "non_amp", "namp", "0"}:
        return "non-AMP"
    if value.lower() in {"amp", "1"}:
        return "AMP"
    return value


def sequence_hash(sequence: str) -> str:
    return hashlib.sha256(normalize_sequence(sequence).encode("utf-8")).hexdigest()


def write_rows(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_train_validation_manifests(
    source_release: Path,
    split_dir: Path,
    heldout_hashes: set[str] | None = None,
) -> None:
    if not source_release.exists():
        raise FileNotFoundError(f"source release not found: {source_release}")

    rows_by_split: dict[str, list[dict[str, str]]] = {"train": [], "validation": []}
    with source_release.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            source_split = row.get("split", "").strip().lower()
            if source_split not in {"train", "val", "validation"}:
                continue
            out_split = "validation" if source_split in {"val", "validation"} else "train"
            sequence = normalize_sequence(row.get("sequence_clean") or row.get("sequence") or "")
            if not sequence:
                continue
            digest = sequence_hash(sequence)
            if heldout_hashes and digest in heldout_hashes:
                continue
            rows_by_split[out_split].append(
                {
                    "split": out_split,
                    "sample_id": row.get("sample_id") or row.get("row_id") or "",
                    "label": normalize_label(row.get("label", "")),
                    "length": str(len(sequence)),
                    "sequence_hash_sha256": digest,
                    "source_dataset": source_release.name,
                    "source_row_id": row.get("row_id", ""),
                    "cluster_id": row.get("cluster_id", ""),
                    "component_id": row.get("comp_id", ""),
                }
            )

    write_rows(split_dir / "train_manifest.csv", rows_by_split["train"], MANIFEST_FIELDS)
    write_rows(split_dir / "validation_manifest.csv", rows_by_split["validation"], MANIFEST_FIELDS)


def build_heldout_manifest(heldout_features: Path, split_dir: Path) -> None:
    if not heldout_features.exists():
        raise FileNotFoundError(f"held-out feature file not found: {heldout_features}")

    rows: list[dict[str, str]] = []
    with heldout_features.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for idx, row in enumerate(reader):
            sequence = normalize_sequence(row.get("Sequence") or row.get("sequence") or "")
            if not sequence:
                continue
            rows.append(
                {
                    "split": "heldout_test",
                    "sample_id": row.get("ID") or f"heldout_{idx:06d}",
                    "label": normalize_label(row.get("Label", "")),
                    "length": str(len(sequence)),
                    "sequence_hash_sha256": sequence_hash(sequence),
                    "source_dataset": "Data_6kGoc/features.csv",
                    "source_row_id": str(idx),
                    "cluster_id": "",
                    "component_id": "",
                }
            )

    write_rows(split_dir / "heldout_test_manifest.csv", rows, MANIFEST_FIELDS)


def read_hashes(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row["sequence_hash_sha256"]
            for row in csv.DictReader(handle)
            if row.get("sequence_hash_sha256")
        }


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize_manifest(name: str, rows: list[dict[str, str]]) -> dict[str, str]:
    labels = Counter(row.get("label", "") for row in rows)
    hashes = [row.get("sequence_hash_sha256", "") for row in rows if row.get("sequence_hash_sha256")]
    unique_hashes = set(hashes)
    return {
        "manifest": name,
        "records": str(len(rows)),
        "unique_sequence_hashes": str(len(unique_hashes)),
        "duplicate_hash_records": str(len(hashes) - len(unique_hashes)),
        "amp_records": str(labels.get("AMP", 0)),
        "non_amp_records": str(labels.get("non-AMP", 0)),
    }


def audit(split_dir: Path, leakage_dir: Path) -> None:
    manifests = {
        "train": load_manifest(split_dir / "train_manifest.csv"),
        "validation": load_manifest(split_dir / "validation_manifest.csv"),
        "heldout_test": load_manifest(split_dir / "heldout_test_manifest.csv"),
    }

    summary_rows = [summarize_manifest(name, rows) for name, rows in manifests.items()]
    write_rows(
        split_dir / "split_audit_summary.csv",
        summary_rows,
        [
            "manifest",
            "records",
            "unique_sequence_hashes",
            "duplicate_hash_records",
            "amp_records",
            "non_amp_records",
        ],
    )

    hash_sets = {
        name: {row["sequence_hash_sha256"] for row in rows if row.get("sequence_hash_sha256")}
        for name, rows in manifests.items()
    }
    pair_rows = []
    names = list(manifests)
    for idx, left in enumerate(names):
        for right in names[idx + 1 :]:
            overlap = hash_sets[left] & hash_sets[right]
            pair_rows.append(
                {
                    "comparison": f"{left}_vs_{right}",
                    "left_unique_hashes": str(len(hash_sets[left])),
                    "right_unique_hashes": str(len(hash_sets[right])),
                    "unique_overlap_hashes": str(len(overlap)),
                    "status": "PASS" if not overlap else "REVIEW_REQUIRED",
                    "note": "Exact SHA-256 sequence-hash comparison.",
                }
            )

    write_rows(
        leakage_dir / "train_validation_heldout_overlap_status.csv",
        pair_rows,
        [
            "comparison",
            "left_unique_hashes",
            "right_unique_hashes",
            "unique_overlap_hashes",
            "status",
            "note",
        ],
    )

    external_rows = [
        {
            "external_dataset": name,
            "status": "NOT_ASSESSED_EXTERNAL_RAW_NOT_BUNDLED",
            "training_hashes": str(len(hash_sets["train"])),
            "external_records": "",
            "unique_overlap_hashes": "",
            "note": "Raw external peptide sequences are not bundled in this minimal GitHub package; rerun with the archived external files to reproduce this audit.",
        }
        for name in ["AMPDiscover", "DDBL", "EMBL", "RefSeq", "SSFGM", "XU"]
    ]
    write_rows(
        leakage_dir / "external_sequence_overlap_status.csv",
        external_rows,
        [
            "external_dataset",
            "status",
            "training_hashes",
            "external_records",
            "unique_overlap_hashes",
            "note",
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and audit AMP split manifests.")
    parser.add_argument("--build-manifests", action="store_true", help="Build manifests before auditing.")
    parser.add_argument(
        "--keep-heldout-overlap",
        action="store_true",
        help="Keep train/validation records with exact sequence hashes present in the held-out feature table.",
    )
    parser.add_argument("--source-release", type=Path, default=DEFAULT_SOURCE_RELEASE)
    parser.add_argument(
        "--heldout-features",
        type=Path,
        default=REPO_ROOT / "data" / "Data_6kGoc" / "features.csv",
    )
    parser.add_argument("--split-dir", type=Path, default=REPO_ROOT / "data" / "splits")
    parser.add_argument("--leakage-dir", type=Path, default=REPO_ROOT / "results" / "leakage_checks")
    args = parser.parse_args()

    manifest_paths = [
        args.split_dir / "train_manifest.csv",
        args.split_dir / "validation_manifest.csv",
        args.split_dir / "heldout_test_manifest.csv",
    ]
    if args.build_manifests or not all(path.exists() for path in manifest_paths):
        build_heldout_manifest(args.heldout_features, args.split_dir)
        heldout_hashes = set() if args.keep_heldout_overlap else read_hashes(args.split_dir / "heldout_test_manifest.csv")
        build_train_validation_manifests(args.source_release, args.split_dir, heldout_hashes=heldout_hashes)

    audit(args.split_dir, args.leakage_dir)
    print(f"Wrote split audit files under {args.split_dir} and {args.leakage_dir}")


if __name__ == "__main__":
    main()
