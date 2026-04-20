from __future__ import annotations

import os
import secrets
from typing import Any

from flask import Flask, jsonify, request

from .settings import Settings, load_or_create_send_key
from .wecom import WeComClient, WeComError


def create_app(
    settings: Settings | None = None,
    wecom_client: WeComClient | None = None,
    send_key: str | None = None,
) -> Flask:
    resolved_settings = settings or Settings.from_env()
    resolved_send_key, created, key_path = load_or_create_send_key(resolved_settings.data_dir)
    if send_key:
        resolved_send_key = send_key
    resolved_client = wecom_client or WeComClient(resolved_settings)

    app = Flask(__name__)
    app.config["SETTINGS"] = resolved_settings
    app.config["SEND_KEY"] = resolved_send_key

    public_base_url = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
    send_path = f"/send/{resolved_send_key}"
    if public_base_url:
        print(f"[zox-push] 发送地址: {public_base_url}{send_path}")
    elif created:
        print(f"[zox-push] 已生成 send key，保存在: {key_path}")
        print(f"[zox-push] 当前发送路径: {send_path}")

    @app.get("/")
    def index() -> Any:
        return jsonify(
            {
                "service": "zox-push",
                "ok": True,
                "send_path": "/send/{key}",
                "usage": "GET/POST /send/{key}",
            }
        )

    @app.get("/healthz")
    def healthz() -> Any:
        return jsonify({"ok": True})

    @app.route("/send/<path_key>", methods=["GET", "POST"])
    def send_message(path_key: str) -> Any:
        if not secrets.compare_digest(path_key, resolved_send_key):
            return _json_error("send key 无效", 403)

        payload = _extract_payload()
        touser = str(payload.get("touser") or resolved_settings.default_touser).strip()
        msgtype = str(payload.get("msgtype") or "auto").strip().lower()

        title = _normalize_text(payload.get("title"))
        text = _normalize_text(payload.get("text"))
        desp = _normalize_text(payload.get("desp"))
        image_base64 = _normalize_text(payload.get("image_base64"))

        if not title and not text and not desp and not image_base64:
            return _json_error("至少需要提供 title、text、desp、image_base64 之一", 400)

        if not title and desp and text:
            title, text = text, None

        try:
            actual_msgtype = _resolve_msgtype(msgtype, image_base64, desp)
            if actual_msgtype == "image":
                if not image_base64:
                    return _json_error("msgtype=image 时必须提供 image_base64", 400)
                result = resolved_client.send_image_base64(image_base64, touser)
            elif actual_msgtype == "markdown":
                content = _build_markdown_content(title, desp, text)
                if not content:
                    return _json_error("Markdown 消息内容不能为空", 400)
                result = resolved_client.send_markdown(content, touser)
            else:
                content = _build_text_content(title, text, desp)
                if not content:
                    return _json_error("文本消息内容不能为空", 400)
                result = resolved_client.send_text(content, touser)
        except ValueError as exc:
            return _json_error(str(exc), 400)
        except WeComError as exc:
            return _json_error(str(exc), 502)

        return jsonify(
            {
                "ok": True,
                "msgtype": actual_msgtype,
                "touser": touser,
                "wecom": result,
            }
        )

    return app


def _extract_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {}
    payload.update(request.args.to_dict(flat=True))

    if request.method == "POST":
        if request.form:
            payload.update(request.form.to_dict(flat=True))
        if request.is_json:
            payload.update(request.get_json(silent=True) or {})

    return payload


def _resolve_msgtype(msgtype: str, image_base64: str | None, desp: str | None) -> str:
    if msgtype not in {"auto", "text", "markdown", "image"}:
        raise ValueError("msgtype 仅支持 auto、text、markdown、image")

    if msgtype == "auto":
        if image_base64:
            return "image"
        if desp:
            return "markdown"
        return "text"
    return msgtype


def _build_text_content(title: str | None, text: str | None, desp: str | None) -> str:
    body = text or desp
    if title and body:
        return f"{title}\n{body}".strip()
    return (title or body or "").strip()


def _build_markdown_content(title: str | None, desp: str | None, text: str | None) -> str:
    parts: list[str] = []
    if title:
        parts.append(f"# {title}")
    if desp:
        parts.append(desp.strip())
    elif text:
        parts.append(text.strip())
    return "\n\n".join(part for part in parts if part).strip()


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _json_error(message: str, status_code: int) -> Any:
    return jsonify({"ok": False, "error": message}), status_code


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=int(os.getenv("PORT", "38127")))
