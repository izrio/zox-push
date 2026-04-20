from __future__ import annotations

import base64
from pathlib import Path

from app.main import create_app
from app.settings import Settings


def build_test_app(tmp_path: Path) -> tuple:
    settings = Settings(
        data_dir=tmp_path,
        default_touser="@all",
    )
    app = create_app(settings=settings, send_key="test-key")
    app.testing = True
    return app, None


def test_reject_invalid_send_key(tmp_path: Path) -> None:
    app, _ = build_test_app(tmp_path)
    client = app.test_client()

    response = client.get("/send/bad-key", query_string={"text": "hello"})

    assert response.status_code == 403
    assert response.get_json()["ok"] is False


def test_serverchan_style_markdown_request(tmp_path: Path) -> None:
    app, _ = build_test_app(tmp_path)
    client = app.test_client()

    response = client.post(
        "/send/test-key",
        json={"text": "告警标题", "desp": "服务异常，请尽快处理。"},
    )

    assert response.status_code == 200
    assert response.get_json()["msgtype"] == "markdown"
    assert response.get_json()["message"]["title"] == "告警标题"
    assert response.get_json()["message"]["content"] == "服务异常，请尽快处理。"


def test_image_message_request(tmp_path: Path) -> None:
    app, _ = build_test_app(tmp_path)
    client = app.test_client()

    image_base64 = base64.b64encode(b"fake-image").decode("utf-8")
    response = client.post(
        "/send/test-key",
        json={"msgtype": "image", "image_base64": image_base64, "touser": "zhangsan"},
    )

    assert response.status_code == 200
    assert response.get_json()["msgtype"] == "image"
    assert response.get_json()["message"]["touser"] == "zhangsan"
    assert response.get_json()["message"]["image_base64"] == image_base64


def test_send_message_is_persisted_for_app_api(tmp_path: Path) -> None:
    app, _ = build_test_app(tmp_path)
    client = app.test_client()

    send_response = client.post(
        "/send/test-key",
        json={"msgtype": "text", "title": "任务完成", "text": "备份已结束"},
    )

    assert send_response.status_code == 200
    payload = send_response.get_json()
    message_id = payload["message"]["id"]

    list_response = client.get("/api/messages")
    assert list_response.status_code == 200
    list_payload = list_response.get_json()
    assert len(list_payload["items"]) == 1
    assert list_payload["items"][0]["id"] == message_id
    assert list_payload["items"][0]["title"] == "任务完成"

    detail_response = client.get(f"/api/messages/{message_id}")
    assert detail_response.status_code == 200
    detail_payload = detail_response.get_json()
    assert detail_payload["item"]["content"] == "任务完成\n备份已结束"


def test_get_missing_message_returns_404(tmp_path: Path) -> None:
    app, _ = build_test_app(tmp_path)
    client = app.test_client()

    response = client.get("/api/messages/not-found")

    assert response.status_code == 404
    assert response.get_json()["ok"] is False


def test_create_app_without_wecom_env_vars(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("WECOM_CID", raising=False)
    monkeypatch.delenv("WECOM_AID", raising=False)
    monkeypatch.delenv("WECOM_SECRET", raising=False)
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    app = create_app()

    assert app.config["SEND_KEY"]
