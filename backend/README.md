# Backend

当前目录是 `zox-push` 的后端服务，职责包括：

- 接收 `/send/{key}` 推送请求
- 调用企业微信接口发送消息
- 将成功发送的消息持久化到本地 JSON 文件
- 提供 `/api/messages` 与 `/api/messages/{id}` 给移动端读取

## 本地开发

```bash
python -m venv .venv
source ../.venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=backend pytest tests
```

## 数据文件

- `send_key.json`：发送密钥
- `messages.json`：App 展示的消息列表

这两个文件都默认保存在 `DATA_DIR` 对应目录下。
