from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path


SEND_KEY_FILENAME = "send_key.json"
MESSAGE_STORE_FILENAME = "messages.json"


@dataclass(frozen=True)
class Settings:
    """后端运行配置。"""

    wecom_cid: str
    wecom_aid: int
    wecom_secret: str
    data_dir: Path
    default_touser: str = "@all"
    request_timeout: int = 10

    @classmethod
    def from_env(cls) -> "Settings":
        missing = [
            key
            for key in ("WECOM_CID", "WECOM_AID", "WECOM_SECRET")
            if not os.getenv(key)
        ]
        if missing:
            raise RuntimeError(f"缺少必要环境变量: {', '.join(missing)}")

        return cls(
            wecom_cid=os.environ["WECOM_CID"].strip(),
            wecom_aid=int(os.environ["WECOM_AID"]),
            wecom_secret=os.environ["WECOM_SECRET"].strip(),
            data_dir=Path(os.getenv("DATA_DIR", "/data")),
            default_touser=os.getenv("DEFAULT_TOUSER", "@all").strip() or "@all",
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "10")),
        )


def load_or_create_send_key(data_dir: Path) -> tuple[str, bool, Path]:
    data_dir.mkdir(parents=True, exist_ok=True)
    key_path = data_dir / SEND_KEY_FILENAME

    if key_path.exists():
        payload = json.loads(key_path.read_text(encoding="utf-8"))
        send_key = str(payload.get("send_key", "")).strip()
        if not send_key:
            raise RuntimeError(f"{key_path} 中未找到有效的 send_key")
        return send_key, False, key_path

    send_key = secrets.token_urlsafe(24)
    key_path.write_text(
        json.dumps({"send_key": send_key}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return send_key, True, key_path
