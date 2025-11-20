import requests
import yaml
from pathlib import Path

CONFIG_PATH = Path.home() / ".runpilot" / "cloud.yaml"

class CloudClient:
    def __init__(self):
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r") as f:
                cfg = yaml.safe_load(f)
        else:
            raise RuntimeError("Not logged in. Run: runpilot login")

        self.base = cfg["api_base"]
        self.token = cfg["token"]

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def list_projects(self):
        url = f"{self.base}/v1/projects"
        r = requests.get(url, headers=self._headers())
        r.raise_for_status()
        return r.json()
