.PHONY: help bootstrap-check generate check contract-diff contract-verify security-check security-verify framework-test tooling-test backend-test frontend-test db-check db-init verify new-loop memory-check evidence-check dry-run semantic-rule-gate docker-build docker-up docker-down coverage test-unit test-integration test-coverage smoke-test e2e-test

PYTHON ?= python3
MVNW ?= ./mvnw
JENA_VERSION := $(shell grep -oE '<jena.version>[^<]+</jena.version>' pom.xml | sed -E 's/<\/?jena.version>//g')
LOOP ?=
HOLDER ?=
BASELINE ?=

help: ## 显示命令
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

bootstrap-check: ## 严格检查Java/Maven/Node/Python/Git/ripgrep环境
	@bash scripts/bootstrap-check.sh

generate: ## 从全部权威合同源生成只读制品
	@test -x scripts/generate-contracts.sh || { echo "FAIL: scripts/generate-contracts.sh missing or not executable"; exit 2; }
	@bash scripts/generate-contracts.sh

check: ## 验证合同、生成物、Loop模板、注册中心契约、数据集与安全基线
	@test -x scripts/check-contracts.sh || { echo "FAIL: scripts/check-contracts.sh missing or not executable"; exit 2; }
	@bash scripts/check-contracts.sh
	@$(PYTHON) scripts/loop_guard.py --template-check
	@$(PYTHON) scripts/secret_scan.py --root . --quiet
	@$(PYTHON) scripts/enum_consistency_check.py --root . --quiet
	@$(PYTHON) scripts/semantic_rule_gate.py
	@$(PYTHON) scripts/gk_ke_contract_examples.py
	@$(PYTHON) scripts/gk_ke_l2_2_registry_tests.py
	@$(PYTHON) scripts/gk_ke_capability_probe_tests.py
	@$(PYTHON) scripts/gk_ke_metric_definitions_check.py
	@$(PYTHON) scripts/generate_gk_ke_dataset_v2.py --verify
	@$(PYTHON) scripts/gk_ke_acceptance_pack.py
	@$(PYTHON) scripts/gk_ke_plan_compiler.py

metric-check: ## 指标定义核验（七组合同 + 可复算性）
	@$(PYTHON) scripts/gk_ke_metric_definitions_check.py

metric-write: ## 指标定义回填 hash 与复算证据
	@$(PYTHON) scripts/gk_ke_metric_definitions_check.py --write

registry-check: ## 能力注册中心契约检查（必填字段/探针枚举/callable 一致性）
	@$(PYTHON) scripts/gk_ke_l2_2_registry_tests.py

probe-check: ## 能力语义探针（报告；不改文件）
	@$(PYTHON) scripts/gk_ke_capability_probe.py

probe-write: ## 能力语义探针回填 probeStatus/callable
	@$(PYTHON) scripts/gk_ke_capability_probe.py --write

probe-tests: ## 探针变异测试（证明断言非空转）
	@$(PYTHON) scripts/gk_ke_capability_probe_tests.py

dataset-verify: ## 数据集 v2 校验（时间泄漏守卫、三层隔离、禁止署名）
	@$(PYTHON) scripts/generate_gk_ke_dataset_v2.py --verify
	@$(PYTHON) scripts/gk_ke_acceptance_pack.py
	@$(PYTHON) scripts/gk_ke_plan_compiler.py

semantic-rule-gate: ## 验证生成的语义与规则合同制品格式自洽(fail-closed)
	@$(PYTHON) scripts/semantic_rule_gate.py

contract-diff: ## 与指定基线目录比较兼容性：BASELINE=path
	@test -n "$(BASELINE)" || { echo "FAIL: BASELINE is required"; exit 2; }
	@$(PYTHON) scripts/contract_diff.py --baseline "$(BASELINE)" --current generated

security-check: ## 秘密、敏感目录权限和隔离资产检查
	@$(PYTHON) scripts/secret_scan.py --root .
	@$(PYTHON) scripts/sensitive_permissions.py --root .
	@$(PYTHON) tools/quarantine/oracle/readonly_guard.py --self-test

framework-test: ## 安装器plan/apply/idempotency/conflict/rollback测试
	@$(PYTHON) -m unittest discover -s tools/sdd-installer/tests -v

tooling-test: ## 合同、Loop、安全与Oracle guard单元测试
	@$(PYTHON) -m unittest discover -s tests/tooling -v

backend-deps-check: ## 验证semantic-jena的Jena依赖可从根统一治理解析
	@test -x $(MVNW) || { echo "FAIL: $(MVNW) missing or not executable"; exit 2; }
	@$(MVNW) --batch-mode --no-transfer-progress -pl adapters/semantic-jena -am dependency:tree -Dincludes=org.apache.jena:jena-arq,org.apache.jena:jena-shacl > /tmp/gits-deps.tree 2>&1 || { cat /tmp/gits-deps.tree; echo "FAIL: dependency:tree failed"; exit 2; }
	@grep -q 'org.apache.jena:jena-arq:jar:$(JENA_VERSION)' /tmp/gits-deps.tree && grep -q 'org.apache.jena:jena-shacl:jar:$(JENA_VERSION)' /tmp/gits-deps.tree || { cat /tmp/gits-deps.tree; echo "FAIL: jena-arq/jena-shacl not resolved to governed version $(JENA_VERSION)"; exit 2; }
	@echo "backend-deps-check: PASS"

backend-test: backend-deps-check ## Java 21/Maven真实编译和测试
	@test -x $(MVNW) || { echo "FAIL: $(MVNW) missing or not executable"; exit 2; }
	@$(MVNW) --batch-mode --no-transfer-progress verify
	@$(PYTHON) scripts/dependency-check-guard.py --search-root .

frontend-test: ## 前端锁文件安装、类型检查、测试和构建
	@test -f frontend/package-lock.json || { echo "FAIL: frontend/package-lock.json missing; lock dependencies before testing"; exit 2; }
	@cd frontend && npm ci && npm run check && npm run test && npm run build

db-check: ## 验证gits_ke管理库可连接可写(需GITS_KEDB_PASSWORD在仓库外设置)
	@bash scripts/db/db_check.sh

db-init: ## 用Flyway初始化/迁移gits_ke schema(需GITS_KEDB_PASSWORD在仓库外设置)
	@bash scripts/db/db_init.sh

verify: bootstrap-check generate check framework-test tooling-test backend-test frontend-test db-check semantic-rule-gate ## 完整本地验证

new-loop: ## 创建批次：make new-loop LOOP=P1-xxx HOLDER=tech_lead
	@test -n "$(LOOP)" -a -n "$(HOLDER)" || { echo "FAIL: LOOP and HOLDER are required"; exit 2; }
	@$(PYTHON) scripts/new_loop.py --loop-id "$(LOOP)" --holder "$(HOLDER)"

memory-check: ## 检查Baton与共享记忆
	@test -n "$(LOOP)" || { echo "FAIL: LOOP is required"; exit 2; }
	@$(PYTHON) scripts/loop_guard.py --loop "$(LOOP)" --memory-only

evidence-check: ## 检查状态、命令和证据hash
	@test -n "$(LOOP)" || { echo "FAIL: LOOP is required"; exit 2; }
	@$(PYTHON) scripts/loop_guard.py --loop "$(LOOP)" --evidence-only

dry-run: generate check framework-test tooling-test semantic-rule-gate ## 不连接真实外部系统的机制Dry-run
	@echo "DEV_SELF_CHECK_PASS: framework and repository mechanisms; independent QA still required"

docker-build: ## 构建后端和前端Docker镜像
	@docker build -t gits-api .
	@docker build -t gits-frontend ./frontend

docker-up: ## 启动Docker Compose服务
	@docker compose -f compose.local.yaml up -d

docker-down: ## 停止Docker Compose服务
	@docker compose -f compose.local.yaml down

coverage: ## 生成Jacoco覆盖率报告
	@$(MVNW) --batch-mode --no-transfer-progress verify jacoco:report

test-unit: ## 仅运行单元测试(排除IT)
	@$(MVNW) --batch-mode --no-transfer-progress test -pl apps/api -Dtest="**/*Test" -DfailIfNoTests=false

test-integration: ## 仅运行集成测试
	@$(MVNW) --batch-mode --no-transfer-progress verify -pl apps/api -Dtest="**/*IT" -DfailIfNoTests=false

test-coverage: ## 运行测试并生成JaCoCo覆盖率报告
	@$(MVNW) --batch-mode --no-transfer-progress test -pl apps/api jacoco:report
	@echo "Coverage report: apps/api/target/site/jacoco/index.html"

security-verify: ## 验证安全配置(秘密扫描+权限检查+安全基线)
	@$(PYTHON) scripts/secret_scan.py --root .
	@$(PYTHON) scripts/sensitive_permissions.py --root .
	@echo "security-verify: PASS"

contract-verify: ## 运行合同合规验证(测试+脚本)
	@$(MVNW) --batch-mode --no-transfer-progress test -pl apps/api -Dtest="com.gien.gits.api.contract.ContractComplianceTest" -DfailIfNoTests=false
	@bash scripts/contract-verify.sh
	@echo "contract-verify: PASS"

smoke-test: ## 冒烟测试: 验证后端健康检查和前端首页可访问
	@echo "Waiting for services to be ready..."
	@sleep 10
	@curl -sf http://localhost:8080/actuator/health | jq . || { echo "FAIL: api health check failed"; exit 2; }
	@curl -sf -o /dev/null -w "%{http_code}" http://localhost:80 | grep -q "200" || { echo "FAIL: frontend homepage not accessible"; exit 2; }
	@echo "smoke-test: PASS"

e2e-test: ## 端到端测试(Playwright)
	@cd frontend && npx playwright test

plan-compile: ## 计划编译（B1/WP05）；BLOCKED 表示能力不可用，非脚本失败
	@$(PYTHON) scripts/gk_ke_plan_compiler.py

plan-write: ## 写出编译产物 ActivationPlan
	@$(PYTHON) scripts/gk_ke_plan_compiler.py --write
