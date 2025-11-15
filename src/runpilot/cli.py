import argparse
from pathlib import Path

from .config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="runpilot",
        description="RunPilot - reproducible AI training runner",
    )

    subparsers = parser.add_subparsers(dest="command")

    # run subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Run a training job from a config file",
    )
    run_parser.add_argument(
        "config_path",
        type=str,
        help="Path to the run config YAML file",
    )

    # list subcommand
    subparsers.add_parser(
        "list",
        help="List recorded runs (placeholder for now)",
    )

    args = parser.parse_args()

    if args.command == "run":
        config_path = Path(args.config_path)
        cfg = load_config(config_path)
        print(
            f"[RunPilot] Would run job '{cfg.name}' "
            f"using image '{cfg.image}' and entrypoint '{cfg.entrypoint}'"
        )
        print("[RunPilot] Actual container execution is not implemented yet.")
    elif args.command == "list":
        print("[RunPilot] Listing runs is not implemented yet.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
