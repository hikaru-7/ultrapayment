import logging

import httpx

from ..config import USER_SERVICE_TIMEOUT, USER_SERVICE_URL

logger = logging.getLogger("task-service")


class UserNotFoundError(Exception):
    pass


class UserServiceTimeoutError(Exception):
    pass


class UserServiceUnavailableError(Exception):
    pass


class UserServiceError(Exception):
    pass


class UnexpectedUserServiceResponseError(Exception):
    pass


class UserClient:
    def __init__(
        self,
        base_url: str = USER_SERVICE_URL,
        timeout: float = USER_SERVICE_TIMEOUT,
    ):
        self.base_url = base_url
        self.timeout = timeout

    def ensure_user_exists(
        self,
        user_id: int,
        request_id: str,
    ) -> None:
        try:
            response = httpx.get(
                f"{self.base_url}/users/{user_id}",
                headers={"X-Request-ID": request_id},
                timeout=self.timeout,
            )
        except httpx.TimeoutException as exc:
            logger.error(
                "request_id=%s user-service timeout",
                request_id,
            )
            raise UserServiceTimeoutError() from exc
        except httpx.RequestError as exc:
            logger.error(
                "request_id=%s user-service unavailable",
                request_id,
            )
            raise UserServiceUnavailableError() from exc

        if response.status_code == 404:
            raise UserNotFoundError()

        if response.status_code >= 500:
            raise UserServiceError()

        if response.status_code != 200:
            raise UnexpectedUserServiceResponseError()
