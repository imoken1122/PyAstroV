import logging
import logging.handlers
import datetime
import pytz

def setup_logger(name):
    # ロガーを作成
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        # フォーマットを設定
        log_formatter = logging.Formatter('[%(asctime)s %(levelname)s %(name)s] - %(message)s', '%Y-%m-%d %H:%M:%S')

        # ログファイル名
        log_file = 'mqtt_camera_client.log'

        # 日本時間に合わせたタイムゾーンを取得
        jst = pytz.timezone('Asia/Tokyo')

        # ログファイルのハンドラを作成
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8', atTime=datetime.time(0, 0, 0)
        )
        file_handler.setFormatter(log_formatter)

        # ログコンソールのハンドラを作成
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        # ロガーにハンドラを追加
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger
