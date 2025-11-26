## 4. Metrics schema: `docs/METRICS.md`

Create `docs/METRICS.md`:

```markdown
# Metrics format

RunPilot stores metrics for a run in `metrics.json` inside the run directory.

<!-- TODO: Add support for real-time metrics streaming to runpilot-cloud -->
<!-- TODO: Implement metric visualization in dashboard -->

The goals are:

- Simple JSON file.
- Easy to extend.
- Suitable for CLI and future cloud sync.

## Schema

Example:

```json
{
  "run_id": "rp_0001",
  "summary": {
    "train_loss": 0.1234,
    "val_loss": 0.1456,
    "accuracy": 0.987
  },
  "time_series": {
    "epoch": [1, 2, 3, 4],
    "train_loss": [0.9, 0.5, 0.2, 0.12],
    "val_loss": [0.95, 0.6, 0.25, 0.14],
    "accuracy": [0.4, 0.7, 0.85, 0.98]
  },
  "tags": ["mnist", "cnn", "baseline"],
  "recorded_at": "2025-11-17T12:34:56Z"
}
```
Fields:
- `run_id`: string. Matches the directory name.
- `summary`: flat key value map of important final metrics.
- `time_series`: optional. Each key is a metric name mapped to a list of values.
- `tags`: optional list of strings, copied from `run.json` if available.
- `recorded_at`: ISO 8601 timestamp of when metrics were written.

<!-- TODO: Add support for metric metadata (description, unit, visualization type) -->
<!-- TODO: Add support for nested/hierarchical metrics -->
<!-- TODO: Implement metric versioning for schema changes -->

## Usage in CLI
The runpilot metrics command can:
- Print `summary` metrics in a table.
- Optionally show basic statistics for time series.
- In future, export metrics to other tools.

<!-- TODO: Add `runpilot metrics compare <run1> <run2>` command -->
<!-- TODO: Add `runpilot metrics export --format prometheus` command -->
<!-- TODO: Add `runpilot metrics plot <run_id>` command for terminal charts -->

## Integrations

<!-- TODO: Add TensorBoard log parsing support -->
<!-- TODO: Add W&B (Weights & Biases) integration -->
<!-- TODO: Add MLflow metrics format support -->
<!-- TODO: Add Prometheus/Grafana export format -->

This is enough to implement and test.