# zox-push

一个拆分后的自建推送项目：

- `backend/`：Flask 后端，负责接收推送、转发企业微信、持久化消息、提供 App 读取 API
- `frontend/`：uni-app x 移动端项目，负责在 Android 与 iOS 上展示消息列表与详情

## 目录结构

```text
.
├── backend/        # Python 后端
├── frontend/       # uni-app x 前端
├── data/           # 运行时数据目录，保存 send key 与消息记录
├── docker-compose.yml
└── .env
```

## 后端启动

```bash
cp .env.example .env
# 编辑 .env，填入企业微信配置

docker compose up -d --build
```

后端默认端口是 `38127`，首次启动会在 `./data/send_key.json` 生成发送密钥。

查看日志：

```bash
docker compose logs -f
```

## 后端接口

### 发送消息

```bash
curl -X POST "http://127.0.0.1:38127/send/<your-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "服务告警",
    "desp": "接口错误率超过 5%"
  }'
```

### 消息列表

```bash
curl "http://127.0.0.1:38127/api/messages"
```

### 消息详情

```bash
curl "http://127.0.0.1:38127/api/messages/<message-id>"
```

## 前端运行

`frontend/` 是一个 uni-app x 项目骨架，建议使用支持 uni-app x 的 HBuilderX 打开。

运行前先修改：

- [frontend/common/config.uts](/Users/chuxionglong/.superset/projects/zox-push/frontend/common/config.uts)

把 `API_BASE_URL` 改成你的服务器真实地址，例如：

```text
http://192.168.1.10:38127
```

不要在真机上继续使用 `127.0.0.1`，否则手机会访问到它自己，而不是你的服务器。

之后：

1. 用 HBuilderX 打开 `frontend/`
2. 运行到 Android 模拟器、Android 真机，或 iOS 设备
3. 首页会读取消息列表，点击进入详情页

## 环境变量

| 变量名 | 必填 | 说明 |
| --- | --- | --- |
| `WECOM_CID` | 是 | 企业微信企业 ID |
| `WECOM_AID` | 是 | 企业微信应用 AgentId |
| `WECOM_SECRET` | 是 | 企业微信应用 Secret |
| `DEFAULT_TOUSER` | 否 | 默认接收人，默认 `@all` |
| `PORT` | 否 | 服务监听端口，默认 `38127` |
| `DATA_DIR` | 否 | 数据目录，默认 `/data` |
| `REQUEST_TIMEOUT` | 否 | 企业微信接口超时秒数，默认 `10` |
| `PUBLIC_BASE_URL` | 否 | 启动时用于日志输出完整发送地址 |

## 验证

后端测试：

```bash
source .venv/bin/activate
PYTHONPATH=backend pytest backend/tests
```

说明：

- 当前仓库已验证后端测试与应用工厂启动。
- 当前仓库未验证 uni-app x 真机构建。
- 当前环境没有 `docker` 命令，因此未验证 Docker 实构建。
