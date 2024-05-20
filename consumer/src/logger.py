import os
import logging

# Get log level from environment variable, defaulting to INFO if not set or invalid
log_level = os.getenv("LOGLEVEL", "INFO").upper()
numeric_log_level = logging.getLevelName(log_level)
if not isinstance(numeric_log_level, int):
    numeric_log_level = logging.INFO

# Get log format from environment variable, defaulting to a specified format if not set
log_format = os.getenv(
    "LOGFORMAT", "[%(asctime)s] %(levelname)s | %(name)s | %(message)s"
)

# Adding a handler for more control
console_handler = logging.StreamHandler()
console_handler.setLevel(numeric_log_level)
console_handler.setFormatter(logging.Formatter(log_format))

# Add a filter to exclude SQLAlchemy logs
class ExcludeSQLAlchemyFilter(logging.Filter):
    def filter(self, record):
        return not record.name.startswith("sqlalchemy")

console_handler.addFilter(ExcludeSQLAlchemyFilter())

# Add handler to the root logger
logging.getLogger().addHandler(console_handler)

# Set the root logger level
logging.getLogger().setLevel(numeric_log_level)
