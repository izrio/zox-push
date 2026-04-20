from __future__ import annotations

import base64
from typing import Any

import requests

from .settings import Settings


class WeComError(RuntimeError):
    """企业微信 API 调用失败。"""


class WeComClient:
    def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
        self.settings = settings
        self.session = session or requests.Session()

    def send_text(self, content: str, touser: str) -> dict[str, Any]:
        access_token = self._get_access_token()
        payload = {
            "touser": touser,
            "agentid": self.settings.wecom_aid,
            "msgtype": "text",
            "text": {"content": content},
            "duplicate_check_interval": 600,
        }
        return self._send_message(access_token, payload)

    def send_markdown(self, content: str, touser: str) -> dict[str, Any]:
        access_token = self._get_access_token()
        payload = {
            "touser": touser,
            "agentid": self.settings.wecom_aid,
            "msgtype": "markdown",
            "markdown": {"content": content},
            "duplicate_check_interval": 600,
        }
        return self._send_message(access_token, payload)

    def send_image_base64(self, base64_content: str, touser: str) -> dict[str, Any]:
        access_token = self._get_access_token()
        media_id = self._upload_image(access_token, base64_content)
        payload = {
            "touser": touser,
            "agentid": self.settings.wecom_aid,
            "msgtype": "image",
            "image": {"media_id": media_id},
            "duplicate_check_interval": 600,
        }
        return self._send_message(access_token, payload)

    def _get_access_token(self) -> str:
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        response = self.session.get(
            url,
            params={
                "corpid": self.settings.wecom_cid,
                "corpsecret": self.settings.wecom_secret,
            },
            timeout=self.settings.request_timeout,
        )
        response.raise_for_status()

        data = response.json()
        if data.get("errcode", 0) != 0:
            raise WeComError(f"获取 access_token 失败: {data}")

        access_token = str(data.get("access_token", "")).strip()
        if not access_token:
            raise WeComError(f"企业微信未返回 access_token: {data}")
        return access_token

    def _upload_image(self, access_token: str, base64_content: str) -> str:
        raw_bytes = _decode_base64_image(base64_content)
        url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload"
        response = self.session.post(
            url,
            params={"access_token": access_token, "type": "image"},
            files={"media": ("image.png", raw_bytes, "image/png")},
            timeout=self.settings.request_timeout,
        )
        response.raise_for_status()

        data = response.json()
        if data.get("errcode", 0) != 0:
            raise WeComError(f"上传图片失败: {data}")

        media_id = str(data.get("media_id", "")).strip()
        if not media_id:
            raise WeComError(f"企业微信未返回 media_id: {data}")
        return media_id

    def _send_message(self, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
        response = self.session.post(
            url,
            params={"access_token": access_token},
            json=payload,
            timeout=self.settings.request_timeout,
        )
        response.raise_for_status()

        data = response.json()
        if data.get("errcode", 0) != 0:
            raise WeComError(f"发送消息失败: {data}")
        return data


def _decode_base64_image(base64_content: str) -> bytes:
    cleaned = base64_content.strip()
    if "," in cleaned and cleaned.lower().startswith("data:"):
        cleaned = cleaned.split(",", 1)[1]

    try:
        return base64.b64decode(cleaned, validate=True)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("image_base64 不是合法的 Base64 图片内容") from exc
