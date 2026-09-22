.PHONY: help install dev test lint build docker-build docker-up docker-down docker-logs clean

help:
@echo "enterprise-rag-knowledge 常用命令"
@echo "  make install       安装前后端依赖"
@echo "  make dev           启动后端开发服务"
@echo "  make test          运行后端测试"
@echo "  make lint          代码检查"
@echo "  make build         构建前端"
@echo "  make docker-build  构建 Docker 镜像"
@echo "  make docker-up     启动所有服务"
@echo "  make docker-down   停止所有服务"
@echo "  make docker-logs   查看日志"
@echo "  make clean         清理临时文件"

install:
cd backend && pip install -r requirements.txt
cd frontend && npm install

dev:
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
cd backend && pytest -q

lint:
cd backend && ruff check .

build:
cd frontend && npm run build

docker-build:
docker compose build

docker-up:
docker compose up -d

docker-down:
docker compose down

docker-logs:
docker compose logs -f

clean:
@echo "清理临时文件..."
-@powershell -Command "Get-ChildItem -Recurse -Include __pycache__,*.pyc,.pytest_cache,.ruff_cache,node_modules,dist -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"