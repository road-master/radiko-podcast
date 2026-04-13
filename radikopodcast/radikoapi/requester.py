"""To unify error check and logging process."""

from http import HTTPStatus
from logging import getLogger

import requests
from radikoplaylist.exceptions import BadHttpStatusCodeError
from radikoplaylist.exceptions import HttpRequestTimeoutError
from requests import Response
from requests import Timeout


class Requester:
    """To unify error check and logging process."""

    @staticmethod
    def get(url: str) -> Response:
        """Get request with error check and logging process."""
        logger = getLogger(__name__)
        try:
            res = requests.get(url=url, timeout=20.0)
        except Timeout as error:
            logger.exception("failed in %s.\nRequest Timeout", url)
            raise HttpRequestTimeoutError("failed in " + url + ".") from error
        if res.status_code != HTTPStatus.OK:
            logger.error("failed in %s.", url)
            logger.error("status_code:%s", res.status_code)
            logger.error("content:%s", res.content)
            raise BadHttpStatusCodeError("failed in " + url + ".")
        logger.debug("Request %s succeed.", url)
        return res
