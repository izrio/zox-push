# Frontend

当前目录是 `zox-push` 的 uni-app x 移动端项目，用于展示后端保存的推送消息。

## 功能范围

- 消息列表
- 消息详情
- 手动下拉刷新
- 基础轮询刷新

## 运行前配置

编辑：

- `common/config.uts`

将 `API_BASE_URL` 改成后端可被手机访问的地址，例如：

```text
http://192.168.1.10:38127
```

不要在真机环境中使用 `127.0.0.1` 或 `localhost`。

## 运行方式

1. 使用支持 uni-app x 的 HBuilderX 打开 `frontend/`
2. 选择运行到 Android 或 iOS
3. 首页查看消息列表，点击进入消息详情

## 说明

- iOS 构建通常需要 macOS 与 Xcode 环境
- 当前仓库只提供项目骨架与页面逻辑，未在本机完成 HBuilderX 编译验证
