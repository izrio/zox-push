# 自建 App 消息展示与前后端拆分执行计划

## 内部执行等级

- 选择 `L`
- 原因：工作分为目录迁移、后端功能补充、前端骨架新增、文档验证四段，存在依赖顺序，不适合并行改写同一仓库面。

## 波次结构

### Wave 1

- 写入受控运行产物
- 冻结需求与执行计划

### Wave 2

- 迁移现有 Flask 服务到 `backend/`
- 调整测试、Dockerfile、requirements、导入路径
- 新增消息持久化与读取 API

### Wave 3

- 新建 `frontend/` uni-app x 项目骨架
- 实现消息列表页、详情页、请求层、项目说明

### Wave 4

- 更新根目录 README、docker-compose、环境变量模板
- 运行后端测试与基础启动检查
- 写入 cleanup 与验证收据

## 所有权边界

- `backend/`：后端运行时、数据存储、测试与 Docker 镜像定义
- `frontend/`：uni-app x 页面、配置与前端说明
- 根目录：编排、环境变量模板、总说明、治理产物

## 验证命令

```bash
source .venv/bin/activate && PYTHONPATH=backend pytest backend/tests
source .venv/bin/activate && PYTHONPATH=backend WECOM_CID=wwtest WECOM_AID=1000001 WECOM_SECRET=secret DATA_DIR=.tmp-data python - <<'PY'
from app.main import create_app
app = create_app()
print(app.config["SEND_KEY"])
PY
```

## 交付验收计划

1. 后端目录拆分后，测试仍通过。
2. 新 API 能列出消息。
3. 前端目录结构完整，页面与请求逻辑可读且可配置。
4. 文档清晰说明后端启动与前端运行方式。

## 完成语言规则

- 仅对已执行测试与启动检查使用“Confirmed”。
- 对 uni-app x 真机构建与 Docker 构建保留“Unverified”。

## 回滚规则

- 若目录迁移导致导入路径失效，优先恢复后端可运行性，再补前端。
- 若前端骨架与后端冲突，保留后端功能完整性，前端按静态骨架最小交付。

## 阶段清理要求

- 不保留临时 `.tmp-data` 目录。
- 不把真实 `.env` 提交到 Git。
- 写入 cleanup receipt，记录已清理与未清理项。
