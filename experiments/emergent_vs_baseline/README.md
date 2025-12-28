# Corridor-Width Ablation Experiment

## Overview
This experiment quantifies whether emergent dynamics reduce search space compared to baseline geometric ranking.

## Files
- `run_ablation.py`: Main experiment script
- `parse_logs.py`: Parse JSON logs into CSV summary
- `visualize_ablation.ipynb`: Analysis and visualization
- `RESULTS.md`: Results and interpretation

## Usage

### 1. Run Ablation
```bash
cd experiments/emergent_vs_baseline
python run_ablation.py --gates G100 G110 G120 --candidate-halfwidth 5000 --swap-steps 500 --output-dir ../../tests/logs
```

**Note:** Gates with `N < 1_000_000` are skipped by the `MIN_GATE_N` guard. Use the scale-representative balanced gates below to generate results:

```bash
python run_ablation.py --gates G020_BAL G025_BAL G030_BAL --candidate-halfwidth 5000 --swap-steps 500 --output-dir ../../tests/logs
```

### 2. Parse Logs
```bash
cd ../../tests
python ../experiments/emergent_vs_baseline/parse_logs.py
```

### 3. Visualize
Open `visualize_ablation.ipynb` in Jupyter.

## Metrics
- **effective_corridor_width**: Rank of true factor p in sorted candidates
- **corridor_entropy**: Shannon entropy of energy distribution (normalized)
- **viable_region_size**: Count of low-energy candidates

## Expected Results
Emergent method should rank true factor p higher (lower rank number) than baseline geometric distance.
