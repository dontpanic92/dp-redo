import logging

class CustomFormatter():
    info_formatter = logging.Formatter("%(message)s")
    formatter = logging.Formatter("%(levelname)s: %(message)s")

    def format(self, record):
        if record.levelno == logging.INFO:
            return self.info_formatter.format(record)
        else:
            return self.formatter.format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

def get_logger():
    return logger