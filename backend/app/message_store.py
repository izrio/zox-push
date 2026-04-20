from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .settings import MESSAGE_STORE_FILENAME


class MessageStore:
    """使用本地 JSON 文件保存消息，便于 App 读取展示。"""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.file_path = data_dir / MESSAGE_STORE_FILENAME
        self._lock = threading.Lock()
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create_message(
        self,
        *,
        msgtype: str,
        touser: str,
        title: str | None,
        content: str | None,
        image_base64: str | None,
    ) -> dict[str, Any]:
        body = (content or "").strip()
        resolved_title = (title or "").strip() or _default_title(msgtype)
        preview = _build_preview(msgtype=msgtype, title=resolved_title, content=body)

        item = {
            "id": uuid4().hex,
            "msgtype": msgtype,
            "title": resolved_title,
            "content": body,
            "preview": preview,
            "touser": touser,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "image_base64": image_base64,
            "image_data_url": _to_data_url(image_base64),
        }

        with self._lock:
            items = self._load_items()
            items.insert(0, item)
            self._write_items(items)

        return item

    def list_messages(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock:
            items = self._load_items()
        return items[:limit]

    def get_message(self, message_id: str) -> dict[str, Any] | None:
        with self._lock:
            items = self._load_items()
        return next((item for item in items if item["id"] == message_id), None)

    def _load_items(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            return []

        payload = json.loads(self.file_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise RuntimeError(f"{self.file_path} 内容格式无效，预期为数组")
        return payload

    def _write_items(self, items: list[dict[str, Any]]) -> None:
        self.file_path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def _default_title(msgtype: str) -> str:
    if msgtype == "image":
        return "图片消息"
    if msgtype == "markdown":
        return "Markdown 消息"
    return "文本消息"


def _build_preview(*, msgtype: str, title: str, content: str) -> str:
    if msgtype == "image":
        return "[图片消息]"

    candidate = content or title
    preview = candidate.replace("\n", " ").strip()
    if len(preview) <= 80:
        return preview
    return preview[:77] + "..."


def _to_data_url(image_base64: str | None) -> str | None:
    if not image_base64:
        return None
    cleaned = image_base64.strip()
    if cleaned.startswith("data:"):
        return cleaned
    return f"data:image/png;base64,{cleaned}"
