# zox-push

一个最小可用的企业微信推送服务，形态类似 Server 酱：

- 容器首次启动时自动生成 `send key`
- 通过 `GET` 或 `POST` 请求 `/send/{key}` 触发推送
- 支持 `text`、`markdown`、`image`
- `send key` 会持久化到挂载目录，重启容器不会变化

## 环境变量

| 变量名 | 必填 | 说明 |
| --- | --- | --- |
| `WECOM_CID` | 是 | 企业 ID |
| `WECOM_AID` | 是 | 企业微信应用 AgentId |
| `WECOM_SECRET` | 是 | 企业微信应用 Secret |
| `DEFAULT_TOUSER` | 否 | 默认接收人，默认 `@all` |
| `DATA_DIR` | 否 | 数据目录，默认 `/data` |
| `PUBLIC_BASE_URL` | 否 | 公网访问前缀，用于在日志里打印完整发送地址 |

## 启动

### Docker Compose

```bash
cp .env.example .env
# 编辑 .env，填入你的企业微信参数

docker compose up -d --build
```

首次启动后，查看日志获取发送路径：

```bash
docker logs zox-push
```

也可以直接查看持久化文件：

```bash
cat ./data/send_key.json
```

示例内容：

```json
{
  "send_key": "Q1x2y3z4..."
}
```

对应发送地址：

```text
http://你的域名:38127/send/Q1x2y3z4...
```

## API

### 1. 类似 Server 酱的 Markdown 推送

当同时传 `text` + `desp` 时，会自动按 Markdown 发送：

```bash
curl -X POST "http://127.0.0.1:38127/send/<your-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "服务告警",
    "desp": "接口错误率超过 5%"
  }'
```

### 2. 普通文本推送

```bash
curl "http://127.0.0.1:38127/send/<your-key>?msgtype=text&text=hello"
```

也支持标题 + 正文：

```bash
curl -X POST "http://127.0.0.1:38127/send/<your-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "msgtype": "text",
    "title": "任务完成",
    "text": "备份已结束"
  }'
```

### 3. Markdown 推送

```bash
curl -X POST "http://127.0.0.1:38127/send/<your-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "msgtype": "markdown",
    "title": "日报",
    "desp": "- 成功 120\n- 失败 3"
  }'
```

### 4. 图片推送

先把图片转成 Base64，再调用：

```bash
curl -X POST "http://127.0.0.1:38127/send/<your-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "msgtype": "image",
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
  }'
```

如果是 Data URL，也支持：

```text
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
```

## 请求参数

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `msgtype` | 否 | `auto` / `text` / `markdown` / `image`，默认 `auto` |
| `touser` | 否 | 指定接收人，不传则走 `DEFAULT_TOUSER` |
| `title` | 否 | 标题 |
| `text` | 否 | 文本内容；当与 `desp` 同时存在时，会被视为 Markdown 标题 |
| `desp` | 否 | Markdown 正文 |
| `image_base64` | 否 | Base64 图片内容，仅 `image` 类型需要 |

## 返回示例

```json
{
  "ok": true,
  "msgtype": "markdown",
  "touser": "@all",
  "wecom": {
    "errcode": 0,
    "errmsg": "ok"
  }
}
```

## 本地开发

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```
