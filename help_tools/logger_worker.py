import loguru
from pathlib import Path, PurePath


class LoggerWorker:
    """Class logger worker."""

    def __init__(self, cfg: dict) -> None:
        self._abs_path: Path = Path(__file__).parents[1]
        self.log_dir_path: Path = Path(cfg["LOG_PATH"])
        self.log_file_name: Path = Path(cfg["LOG_FILENAME"])
        self.abs_file_path: Path = Path(
            PurePath(
                self._abs_path, self.log_dir_path, self.log_file_name
            )
        )
        self.logger: loguru.Logger = self._get_custom_logger()

    def _get_custom_logger(self):
        loguru.logger.add(
            self.abs_file_path,
            format="| {time:DD-MM-YYYY HH:mm:ss:SSS} | {level} | {message} | {module} |",
            encoding="utf-8",
            level="INFO",
            rotation="00:00",
            retention="1 month",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )
        return loguru.logger
