from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
from pathlib import Path
from typing import Union


@dataclass
class FrameData:
    """Data container for frame information."""

    source: Union[str, Path]
    frame_exist: bool
    frame: np.ndarray
    timestamp: datetime

    def get_data_as_dict(self):
        return asdict(self)


@dataclass
class LogsData:
    """Data container for logs information."""

    text: str
    type: str
    module_name: str
    timestamp: str

    def get_data_as_dict(self):
        return asdict(self)
