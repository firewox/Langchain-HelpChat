# @Time  :2024/11/20 23:07
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from loguru import logger
from datetime import datetime
from pathlib import Path
import sys
project_path = Path.cwd()
log_path = Path(project_path, "logs")
# Ensure the log directory exists
log_path.mkdir(parents=True, exist_ok=True)

log_time = datetime.now().strftime("%Y_%m_%d")

# Configure loguru logger
logger.remove()
logger.add(
    f"{log_path}/holaChat_{log_time}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | "
           "{file} | "
           "{process.name} | "
           "{thread.name} | "
           "{module}.{function}:{line} - {level} - {message}",
    level="INFO",
    enqueue=True,
    encoding="utf-8",
    rotation="1 day",  # 每天滚动一次
)

logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} | "
           "{file} | "
           "{process.name} | "
           "{thread.name} | "
           "{module}.{function}:{line} - {level} - {message}",
    level="INFO",
    enqueue=True,
)
logger.info(
    f"Logger is configured and ready to use. log file:{log_path}/holaChat_{log_time}.log"
)