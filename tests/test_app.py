from __future__ import annotations

import base64
from pathlib import Path

from app.main import create_app
from app.settings import Settings


class FakeWeComClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str]] = []

    def send_text(self, content: str, touser: str) -> dict[str, int]:
        self.calls.append(("text", content, touser))
        return {"errcode": 0}

    def send_markdown(self, content: str, touser: str) -> dict[str, int]:
        self.calls.append(("markdown", content, touser))
        return {"errcode": 0}

    def send_image_base64(self, base64_content: str, touser: str) -> dict[str, int]:
        self.calls.append(("image", base64_content, touser))
        return {"errcode": 0}


def build_test_app(tmp_path: Path) -> tuple:
    settings = Settings(
        wecom_cid="cid",
        wecom_aid=1000001,
        wecom_secret="secret",
        data_dir=tmp_path,
        default_touser="@all",
    )
    fake_client = FakeWeComClient()
    app = create_app(settings=settings, wecom_client=fake_client, send_key="test-key")
    app.testing = True
    return app, fake_client


def test_reject_invalid_send_key(tmp_path: Path) -> None:
    app, _ = build_test_app(tmp_path)
    client = app.test_client()

    response = client.get("/send/bad-key", query_string={"text": "hello"})

    assert response.status_code == 403
    assert response.get_json()["ok"] is False


def test_serverchan_style_markdown_request(tmp_path: Path) -> None:
    app, fake_client = build_test_app(tmp_path)
    client = app.test_client()

    response = client.post(
        "/send/test-key",
        json={"text": "告警标题", "desp": "服务异常，请尽快处理。"},
    )

    assert response.status_code == 200
    assert response.get_json()["msgtype"] == "markdown"
    assert fake_client.calls == [
        ("markdown", "# 告警标题\n\n服务异常，请尽快处理。", "@all")
    ]


def test_image_message_request(tmp_path: Path) -> None:
    app, fake_client = build_test_app(tmp_path)
    client = app.test_client()

    image_base64 = base64.b64encode(b"fake-image").decode("utf-8")
    response = client.post(
        "/send/test-key",
        json={"msgtype": "image", "image_base64": image_base64, "touser": "zhangsan"},
    )

    assert response.status_code == 200
    assert response.get_json()["msgtype"] == "image"
    assert fake_client.calls == [("image", image_base64, "zhangsan")]
