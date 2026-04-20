#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SERVICE_NAME="zox-push"
BRANCH="${1:-$(git branch --show-current)}"

log() {
  printf '[deploy] %s\n' "$1"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf '[deploy] 缺少命令: %s\n' "$1" >&2
    exit 1
  fi
}

ensure_clean_worktree() {
  if [[ -n "$(git status --porcelain)" ]]; then
    printf '[deploy] 当前工作区不干净，已停止部署，避免覆盖未提交修改。\n' >&2
    git status --short
    exit 1
  fi
}

ensure_env_file() {
  if [[ -f .env ]]; then
    return
  fi

  if [[ -f .env.example ]]; then
    cp .env.example .env
    log "未找到 .env，已根据 .env.example 生成，请按需补充配置后重新执行。"
    exit 1
  fi

  printf '[deploy] 缺少 .env 和 .env.example，无法继续部署。\n' >&2
  exit 1
}

pull_latest_code() {
  log "拉取远端分支 origin/${BRANCH}"
  git fetch origin "$BRANCH"

  local local_rev
  local remote_rev
  local base_rev
  local_rev="$(git rev-parse HEAD)"
  remote_rev="$(git rev-parse "origin/${BRANCH}")"
  base_rev="$(git merge-base HEAD "origin/${BRANCH}")"

  if [[ "$local_rev" == "$remote_rev" ]]; then
    log "当前代码已是最新，无需更新。"
    return
  fi

  if [[ "$local_rev" != "$base_rev" ]]; then
    printf '[deploy] 当前分支落后且存在非 fast-forward 情况，请先手动处理合并。\n' >&2
    exit 1
  fi

  git pull --ff-only origin "$BRANCH"
}

deploy_backend() {
  mkdir -p data
  log "开始构建并启动后端容器"
  docker compose up -d --build
  log "容器状态"
  docker compose ps
  log "最近 50 行后端日志"
  docker compose logs --tail=50 "$SERVICE_NAME"
}

main() {
  require_command git
  require_command docker

  docker compose version >/dev/null

  ensure_clean_worktree
  ensure_env_file
  pull_latest_code
  deploy_backend
}

main "$@"
