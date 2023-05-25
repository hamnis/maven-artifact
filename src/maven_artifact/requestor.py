import base64
import requests

from maven_artifact.utils import Utils


class RequestException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Requestor(object):
    def __init__(self, username=None, password=None, token=None, user_agent="Maven Artifact Downloader/1.0"):
        self.user_agent = user_agent
        self.username = username
        self.password = password
        self.token = token

    def request(self, url, onFail, onSuccess=None, method: str = "get", **kwargs):
        headers = {"User-Agent": self.user_agent}

        if self.username and self.password:
            token = self.username + ":" + self.password
            headers["Authorization"] = f"Basic {base64.b64encode(token.encode()).decode()}"
        elif Utils.is_base64(self.password):
            headers["Authorization"] = f"Basic {self.password}"
        elif self.token:
            headers["Authorization"] = f"Bearer {base64.b64encode(self.token.encode()).decode()}"

        try:
            response = getattr(requests, method)(url, headers=headers, **kwargs)
            response.raise_for_status()
            if onSuccess:
                return onSuccess(response)
            return response
        except Exception as ex:
            if onFail:
                return onFail(url, ex)
            raise
