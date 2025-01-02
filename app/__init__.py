import logging
from datetime import datetime
from pathlib import Path

formatter = logging.Formatter("%(asctime)s %(levelname)8s | %(name)s : %(message)s")

logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
file_handler = logging.FileHandler(
    logs_dir.joinpath(f"{datetime.now().strftime("%y%m%d.%H%M%S.%f")}.log")
)
file_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
