import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("app")

"""
Пример использования
from app.logger import logger

logger.info("Пользователь отправил запрос")
logger.debug("Тело запроса такое-то")
logger.warning("Что-то подозрительное")
logger.error("Ошибка подключения к БД")

"""
