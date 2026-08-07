import log
import logging
log.start_logging(app = "amass_files",)
logging.info("hello world")
logging.info({"foo": "bar"})
logging.info(["baz bat", {"gnu": "elk", "moose": "jaw"}])
print("hello world")