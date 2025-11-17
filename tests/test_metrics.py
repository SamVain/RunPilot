from pathlib import Path

from runpilot.metrics import parse_metrics_from_log


def test_parse_metrics_from_log_simple(tmp_path: Path) -> None:
    log_path = tmp_path / "logs.txt"
    log_path.write_text(
        "\n".join(
            [
                "some normal line",
                "METRIC {\"step\": 1, \"loss\": 0.92}",
                "METRIC {\"step\": 2, \"loss\": 0.81, \"accuracy\": 0.64}",
                "another line",
            ]
        ),
        encoding="utf-8",
    )

    metrics = parse_metrics_from_log(log_path)

    assert "loss" in metrics
    assert "accuracy" in metrics
    assert "final" in metrics

    loss_series = metrics["loss"]
    accuracy_series = metrics["accuracy"]
    final = metrics["final"]

    assert loss_series == [
        {"step": 1, "value": 0.92},
        {"step": 2, "value": 0.81},
    ]
    assert accuracy_series == [
        {"step": 2, "value": 0.64},
    ]
    assert final["loss"] == 0.81
    assert final["accuracy"] == 0.64


def test_parse_metrics_from_log_empty_or_invalid(tmp_path: Path) -> None:
    log_path = tmp_path / "logs.txt"
    log_path.write_text(
        "\n".join(
            [
                "no metrics here",
                "METRIC not-json",
                "METRIC 123",
            ]
        ),
        encoding="utf-8",
    )

    metrics = parse_metrics_from_log(log_path)
    assert metrics == {}
