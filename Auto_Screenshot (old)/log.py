import logging
import os

if os.path.exists("app.log"):
    os.remove("app.log")

    #ロガーの作成
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    #通常のハンドラーの作成と設定
    handler = logging.FileHandler("app.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    #ロガーにハンドラーを追加
    logger.addHandler(handler)
else:
    #ロガーの作成
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    #通常のハンドラーの作成と設定
    handler = logging.FileHandler("app.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    #ロガーにハンドラーを追加
    logger.addHandler(handler)
