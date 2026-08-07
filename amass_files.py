import log
import logging
log.start_logging(app = "amass_files",)
logging.info("Hello cruel world")
logging.info({"foo": "bar"})
logging.info(["item 1", "item2"])
print("Hello cruel world")