import os
from pathlib import Path


def project_root() -> Path:
    return Path(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../..")
        )
    )
