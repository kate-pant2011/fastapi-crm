import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        "%s %s - %s - %.3f sec",
        request.method,
        request.url.path,
        response.status_code,
        process_time
    )
    return response