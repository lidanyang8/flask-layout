.PHONY: help install install-dev run run-prod test test-cov lint format type-check clean db-init db-upgrade db-downgrade db-migrate db-revision docker-build docker-up docker-down docker-logs shell deploy-supervisor deploy-systemd

# 变量定义
PYTHON := python3
PIP := pip3
VENV := venv
PYTHON_VENV := $(VENV)/bin/python
PIP_VENV := $(VENV)/bin/pip
FLASK := flask
GUNICORN := gunicorn
PROJECT_NAME := flask-layout
APP_DIR := $(shell pwd)

# 颜色定义
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# 默认目标
.DEFAULT_GOAL := help

##@ 帮助信息

help: ## 显示此帮助信息
	@echo "$(CYAN)Flask Layout 项目 Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)可用命令:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ 环境设置

venv: ## 创建虚拟环境
	@echo "$(GREEN)创建虚拟环境...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)虚拟环境创建完成$(NC)"

venv-activate: ## 显示虚拟环境激活命令
	@echo "$(YELLOW)运行以下命令激活虚拟环境:$(NC)"
	@echo "  source $(VENV)/bin/activate"

##@ 依赖管理

install: ## 安装生产依赖
	@echo "$(GREEN)安装生产依赖...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)依赖安装完成$(NC)"

install-dev: ## 安装开发依赖
	@echo "$(GREEN)安装开发依赖...$(NC)"
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)开发依赖安装完成$(NC)"

install-all: venv install-dev ## 创建虚拟环境并安装所有依赖
	@echo "$(GREEN)环境设置完成$(NC)"

update: ## 更新所有依赖包
	@echo "$(GREEN)更新依赖包...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt
	@echo "$(GREEN)依赖更新完成$(NC)"

##@ 运行应用

run: ## 运行开发服务器
	@echo "$(GREEN)启动开发服务器...$(NC)"
	FLASK_ENV=development $(PYTHON) run.py

run-prod: ## 使用 Gunicorn 运行生产服务器（本地测试）
	@echo "$(GREEN)启动生产服务器（Gunicorn）...$(NC)"
	FLASK_ENV=production $(GUNICORN) --config gunicorn.conf.py wsgi:app

run-gunicorn: run-prod ## 使用 Gunicorn 运行（别名）

##@ 测试

test: ## 运行测试
	@echo "$(GREEN)运行测试...$(NC)"
	pytest tests/ -v

test-cov: ## 运行测试并生成覆盖率报告
	@echo "$(GREEN)运行测试并生成覆盖率报告...$(NC)"
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)覆盖率报告已生成，查看 htmlcov/index.html$(NC)"

test-watch: ## 监视文件变化并自动运行测试
	@echo "$(GREEN)启动测试监视模式...$(NC)"
	pytest-watch tests/

##@ 代码质量

lint: ## 运行代码检查（flake8）
	@echo "$(GREEN)运行代码检查...$(NC)"
	flake8 app/ tests/ --max-line-length=120 --exclude=venv,__pycache__,migrations

format: ## 格式化代码（black）
	@echo "$(GREEN)格式化代码...$(NC)"
	black app/ tests/ --line-length=120

format-check: ## 检查代码格式（不修改）
	@echo "$(GREEN)检查代码格式...$(NC)"
	black app/ tests/ --line-length=120 --check

type-check: ## 运行类型检查（mypy）
	@echo "$(GREEN)运行类型检查...$(NC)"
	mypy app/ --ignore-missing-imports

check: format-check lint type-check ## 运行所有代码质量检查（不修改文件）

fix: format ## 自动修复代码格式问题

quality: format lint type-check test ## 运行完整的代码质量检查

##@ 数据库管理

db-init: ## 初始化数据库
	@echo "$(GREEN)初始化数据库...$(NC)"
	FLASK_APP=run.py $(FLASK) init_db

db-migrate: ## 创建数据库迁移
	@echo "$(GREEN)创建数据库迁移...$(NC)"
	@read -p "请输入迁移消息: " msg; \
	FLASK_APP=run.py $(FLASK) db migrate -m "$$msg"

db-upgrade: ## 升级数据库
	@echo "$(GREEN)升级数据库...$(NC)"
	FLASK_APP=run.py $(FLASK) db upgrade

db-downgrade: ## 降级数据库
	@echo "$(YELLOW)降级数据库...$(NC)"
	@read -p "确认要降级数据库吗？(y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		FLASK_APP=run.py $(FLASK) db downgrade; \
	else \
		echo "$(RED)操作已取消$(NC)"; \
	fi

db-revision: ## 创建空的数据库迁移
	@echo "$(GREEN)创建空的数据库迁移...$(NC)"
	@read -p "请输入迁移消息: " msg; \
	FLASK_APP=run.py $(FLASK) db revision -m "$$msg"

db-reset: ## 重置数据库（危险操作）
	@echo "$(RED)警告: 这将删除所有数据！$(NC)"
	@read -p "确认要重置数据库吗？(y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -f app.db dev.db; \
		FLASK_APP=run.py $(FLASK) init_db; \
		FLASK_APP=run.py $(FLASK) db upgrade; \
		echo "$(GREEN)数据库已重置$(NC)"; \
	else \
		echo "$(RED)操作已取消$(NC)"; \
	fi

db-shell: ## 打开数据库 shell
	@echo "$(GREEN)打开数据库 shell...$(NC)"
	FLASK_APP=run.py $(FLASK) shell

##@ Docker 操作

docker-build: ## 构建 Docker 镜像
	@echo "$(GREEN)构建 Docker 镜像...$(NC)"
	docker-compose build

docker-up: ## 启动 Docker 容器
	@echo "$(GREEN)启动 Docker 容器...$(NC)"
	docker-compose up -d

docker-down: ## 停止 Docker 容器
	@echo "$(GREEN)停止 Docker 容器...$(NC)"
	docker-compose down

docker-logs: ## 查看 Docker 日志
	docker-compose logs -f

docker-restart: docker-down docker-up ## 重启 Docker 容器

docker-shell: ## 进入 Docker 容器 shell
	docker-compose exec web bash

docker-db-shell: ## 进入数据库容器 shell
	docker-compose exec db psql -U flaskuser -d flaskdb

docker-clean: ## 清理 Docker 资源（包括卷）
	@echo "$(YELLOW)清理 Docker 资源...$(NC)"
	docker-compose down -v
	docker system prune -f

##@ 部署

deploy-supervisor: ## 部署到 Supervisor（需要 sudo）
	@echo "$(GREEN)部署到 Supervisor...$(NC)"
	@if [ ! -f supervisor.conf ]; then \
		echo "$(RED)错误: supervisor.conf 文件不存在$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)请确保已修改 supervisor.conf 中的路径$(NC)"
	@read -p "继续部署？(y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		sudo cp supervisor.conf /etc/supervisor/conf.d/$(PROJECT_NAME).conf; \
		sudo mkdir -p /var/log/$(PROJECT_NAME) /var/run/$(PROJECT_NAME); \
		sudo supervisorctl reread; \
		sudo supervisorctl update; \
		sudo supervisorctl start $(PROJECT_NAME); \
		echo "$(GREEN)部署完成$(NC)"; \
	else \
		echo "$(RED)操作已取消$(NC)"; \
	fi

deploy-systemd: ## 部署到 Systemd（需要 sudo）
	@echo "$(GREEN)部署到 Systemd...$(NC)"
	@if [ ! -f flask-layout.service ]; then \
		echo "$(RED)错误: flask-layout.service 文件不存在$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)请确保已修改 flask-layout.service 中的路径$(NC)"
	@read -p "继续部署？(y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		sudo cp flask-layout.service /etc/systemd/system/$(PROJECT_NAME).service; \
		sudo mkdir -p /var/log/$(PROJECT_NAME) /var/run/$(PROJECT_NAME); \
		sudo systemctl daemon-reload; \
		sudo systemctl enable $(PROJECT_NAME); \
		sudo systemctl start $(PROJECT_NAME); \
		echo "$(GREEN)部署完成$(NC)"; \
	else \
		echo "$(RED)操作已取消$(NC)"; \
	fi

##@ 清理

clean: ## 清理 Python 缓存文件
	@echo "$(GREEN)清理缓存文件...$(NC)"
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	@echo "$(GREEN)清理完成$(NC)"

clean-all: clean ## 清理所有生成的文件（包括虚拟环境）
	@echo "$(GREEN)清理所有文件...$(NC)"
	rm -rf $(VENV)
	rm -rf *.db
	rm -rf logs/*.log
	@echo "$(GREEN)清理完成$(NC)"

##@ 工具命令

shell: ## 打开 Flask shell
	@echo "$(GREEN)打开 Flask shell...$(NC)"
	FLASK_APP=run.py $(FLASK) shell

routes: ## 显示所有路由
	@echo "$(GREEN)应用路由列表:$(NC)"
	FLASK_APP=run.py $(FLASK) routes

env-check: ## 检查环境变量配置
	@echo "$(GREEN)环境变量检查:$(NC)"
	@echo "FLASK_ENV: $$FLASK_ENV"
	@echo "DATABASE_URL: $$DATABASE_URL"
	@echo "SECRET_KEY: $${SECRET_KEY:+已设置}"
	@echo "PYTHON: $(PYTHON)"
	@echo "PIP: $(PIP)"

requirements: ## 生成 requirements.txt（从已安装的包）
	@echo "$(GREEN)生成 requirements.txt...$(NC)"
	$(PIP) freeze > requirements-generated.txt
	@echo "$(GREEN)已生成 requirements-generated.txt$(NC)"

##@ 开发工作流

dev-setup: install-all db-init db-upgrade ## 完整的开发环境设置

dev: run ## 启动开发服务器（别名）

ci: check test-cov ## CI/CD 流程（代码检查 + 测试）

pre-commit: format lint type-check test ## 提交前检查（格式化、检查、测试）

