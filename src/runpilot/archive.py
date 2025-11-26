from __future__ import annotations

# TODO: Add support for partial exports (only metadata, only logs, etc.)
# TODO: Implement archive compression level configuration
# TODO: Add support for encrypted archives for sensitive data
# TODO: Implement archive format versioning for backwards compatibility
# TODO: Add support for exporting to cloud storage (S3, GCS)
# TODO: Implement archive signing for integrity verification
# TODO: Add support for importing from URLs (http://, s3://)
# TODO: Implement archive merging for combining multiple runs
# TODO: Add support for archive metadata (description, tags)
# TODO: Implement archive streaming for large datasets

import tarfile
from pathlib import Path
from typing import Optional

from .paths import get_run_dir


class RunNotFoundError(FileNotFoundError):
    pass


def export_run(run_id: str, output_path: Optional[Path] = None) -> Path:
    """
    Export a run directory to a tar.gz archive.

    The archive layout is:

        <run_id>/
          run.json
          logs.txt
          metrics.json (optional)
          outputs/     (optional)
    """
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        raise RunNotFoundError(f"Run directory not found for id: {run_id}")

    if output_path is None:
        output_path = Path(f"{run_id}.tar.gz")
    else:
        output_path = Path(output_path)

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(output_path, "w:gz") as tf:
        # arcname ensures the root folder in the archive is exactly run_id
        tf.add(run_dir, arcname=run_dir.name)

    return output_path


def import_run(archive_path: Path, overwrite: bool = False) -> str:
    """
    Import a run from a tar.gz archive created by export_run.

    Returns the run_id that was imported.
    """
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    with tarfile.open(archive_path, "r:gz") as tf:
        members = tf.getmembers()
        if not members:
            raise ValueError(f"Archive {archive_path} is empty")

        # First path component of the first member is the run_id
        root_name = members[0].name.split("/", 1)[0]
        run_id = root_name

        target_dir = get_run_dir(run_id)
        runs_root = target_dir.parent
        runs_root.mkdir(parents=True, exist_ok=True)

        if target_dir.exists():
            if not overwrite:
                raise FileExistsError(
                    f"Run directory already exists for id {run_id}: {target_dir}"
                )

        # Extract into the runs root; archive already contains <run_id>/...
        tf.extractall(path=runs_root)

    return run_id
