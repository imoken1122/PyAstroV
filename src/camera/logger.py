import logging
import logging.handlers
import datetime
import pytz

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        log_formatter = logging.Formatter('[%(asctime)s %(levelname)s %(name)s] - %(message)s', '%Y-%m-%d %H:%M:%S')

        log_file = 'mqtt_camera_client.log'

        jst = pytz.timezone('Asia/Tokyo')

        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8', atTime=datetime.time(0, 0, 0)
        )
        file_handler.setFormatter(log_formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger
