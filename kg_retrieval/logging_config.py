import logging
from datetime import date
from pathlib import Path
from typing import TextIO


class DailyFileHandler(logging.Handler):
    def __init__(self, log_directory: Path):
        super().__init__()
        self.log_directory = log_directory
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self.current_date: date | None = None
        self.stream: TextIO | None = None

    def emit(self, record: logging.LogRecord) -> None:
        try:
            today = date.today()
            if today != self.current_date:
                if self.stream is not None:
                    self.stream.close()
                log_path = self.log_directory / f"app-{today.isoformat()}.log"
                self.stream = log_path.open("a", encoding="utf-8")
                self.current_date = today

            self.stream.write(f"{self.format(record)}\n")
            self.stream.flush()
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        if self.stream is not None:
            self.stream.close()
            self.stream = None
        super().close()


def configure_logging() -> None:
    app_logger = logging.getLogger("kg_retrieval")
    if any(isinstance(handler, DailyFileHandler) for handler in app_logger.handlers):
        return

    project_root = Path(__file__).resolve().parent.parent
    handler = DailyFileHandler(project_root / "logs")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    app_logger.addHandler(handler)
    app_logger.setLevel(logging.INFO)