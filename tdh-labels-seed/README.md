# tdh-labels (private)

Auto-collected blind labels from the `tdh-labeler` / `tdh-bluff` tools.

```
expert/<rater_id>/<timestamp>.json   # one submission; payload.labels keyed by transcript_id
lay/<handle>/<timestamp>.json
```

Append-only — every submission is a new file; git history is the audit trail.

## Pull into the detector eval pipeline
```bash
git pull
python pull_labels.py . ../transfer-detector-v0/data/labels/human_a   # per rater dest
python ../transfer-detector-v0/eval/human_ceiling.py
```

Never open `transfer-detector-v0/data/transcripts/synthetic/_key.SEALED.json` until labels are final.
