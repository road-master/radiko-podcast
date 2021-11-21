"""To unify error check and logging process."""
from logging import getLogger

import requests
from radikoplaylist.exceptions import BadHttpStatusCodeError, HttpRequestTimeoutError
from requests import Response, Timeout


class Requester:
    """To unify error check and logging process."""

    @staticmethod
    def get(url: str) -> Response:
        """Get request with error check and logging process."""
        logger = getLogger(__name__)
        try:
            res = requests.get(url=url, timeout=20.0)
        except Timeout as error:
            logger.error("failed in %s.", url)
            logger.error("Request Timeout")
            logger.error(error)
            raise HttpRequestTimeoutError("failed in " + url + ".") from error
        if res.status_code != 200:
            logger.error("failed in %s.", url)
            logger.error("status_code:%s", res.status_code)
            logger.error("content:%s", res.content)
            raise BadHttpStatusCodeError("failed in " + url + ".")
        logger.debug("Request %s succeed.", url)
        return res
