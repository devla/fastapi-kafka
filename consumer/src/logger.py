import os
import logging


logging.basicConfig(
    level=getattr(logging, os.getenv("LOGLEVEL", "").upper(), "INFO"),
    format="[%(asctime)s] %(levelname)s | %(name)s | %(message)s",
)
