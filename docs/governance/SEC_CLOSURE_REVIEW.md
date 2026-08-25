# 安全闭环审查报告

> **编号**：SEC-CLOSURE-REVIEW-001
> **创建日期**：2026-08-24
> **创建角色**：Feature Pilot (P24 Architecture Remediation)
> **关联发现**：REM-P1-05 (ARCH-REVIEW-2026-08-23-001)
> **状态**：ENGINEERING_CANDIDATE

---

## 1. 审查范围

| 维度 | 审查内容 | 状态 |
|------|----------|------|
| Suppression 审查 | `dependency-check-suppressions.xml` 每条豁免的合理性 | ✅ 通过 |
| Secret Scan | 源码和配置中是否存在硬编码密钥 | ✅ 通过 |
| 生产配置安全 | `application-prod.yaml` 安全配置完整性 | ✅ 通过 |
| API Key 认证 | fail-closed 语义验证 | ✅ 通过 (P0-04 已修复) |

## 2. Suppression 审查结果

### 2.1 豁免清单

| # | CVE | 组件 | 分类 | 理由 | 审批 | 结论 |
|---|-----|------|------|------|------|------|
| 1 | CVE-2024-34759, CVE-2025-24813 | tomcat-embed-core | DEV_ONLY | 嵌入式 Tomcat 仅开发使用 | P16 | ✅ 合理 |
| 2 | CVE-2024-54679 | jackson-databind | BOM_MANAGED | Spring Boot BOM 管理 | P16 | ✅ 合理 |
| 3 | HTTP Request Smuggling | Apache Jena | NO_EXTERNAL_EXPOSURE | 本体存储无外网暴露 | P16 | ✅ 合理 |
| 4 | CVE-2026-0994 | protobuf-java | FALSE_POSITIVE | Python CVE，不影响 Java | P20 | ✅ 合理 |
| 5 | CVE-2026-34477~34481, CVE-2025-68161 | log4j-api | COMPONENT_MISMATCH | 无 log4j-core，不可利用 | P20 | ✅ 合理 |
| 6 | CVE-2026-42154 | micrometer-registry-prometheus | COMPONENT_MISMATCH | Prometheus server CVE，非 Java client | P20 | ✅ 合理 |
| 7 | CVE-2026-66299 | tomcat-embed-core/websocket | FEATURE_NOT_PRESENT | 无 examples webapp | P20 | ✅ 合理 |
| 8 | CVE-2026-65898~66010, CVE-2026-49458~49978 | DOMPurify (swagger-ui) | BELOW_THRESHOLD+DEV_ONLY | CVSS < 7.0，生产禁用 Swagger | P20 | ✅ 合理 |
| 9 | CVE-2026-67214 | nanoid | VERSION_MISMATCH | 实际 3.3.16，非 5.x | P22 | ✅ 合理 |

### 2.2 审查结论

- **所有豁免均有明确分类、理由和审批记录**
- **无宽泛正则**：每条抑制精确绑定 CVE 编号
- **无过期豁免**：所有 REVIEW_REQUIRED=YES，需定期复审
- **建议**：下次 P20/P22 复审时确认 CVE 是否已在上游修复

## 3. Secret Scan 结果

### 3.1 扫描方法

```bash
# 1. 密钥文件搜索
git log --all --diff-filter=A --name-only -- "*.key" "*.pem" "*.p12" "*.jks" "*.secret"
# 结果: 无命中

# 2. 常见 API key 模式
grep -rn "sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36,}|AKIA[0-9A-Z]{16}|AIza[a-zA-Z0-9_-]{35}"
# 结果: 无命中

# 3. 配置文件硬编码检查
grep -rn "api.key|api-key|apiKey|secret|password|token" --include="*.yaml" --include="*.properties"
# 结果: 所有密钥均使用环境变量占位符
```

### 3.2 配置文件密钥管理

| 配置文件 | 密钥字段 | 格式 | 安全性 |
|----------|----------|------|--------|
| `application-prod.yaml` | `api-key` | `${API_KEY}` | ✅ 无默认值，fail-closed |
| `application-prod.yaml` | `password` | `${MYSQL_PASSWORD}` | ✅ 环境变量 |
| `application-prod.yaml` | `api-key` (LLM) | `${LLM_API_KEY:}` | ✅ 环境变量 |
| `application-prod.yaml` | `auth-token` | `${CRM_AUTH_TOKEN:}` | ✅ 环境变量 |
| `application.yaml` | `api-key` | `""` | ✅ 开发模式空值 |
| `application-local.yaml` | `password` | `${GITS_KEDB_PASSWORD:root}` | ⚠️ 默认 root（仅本地） |

### 3.3 本地配置风险

`application-local.yaml` 中 `GITS_KEDB_PASSWORD:root` 是本地 H2 开发默认值，不用于生产。**可接受**，但建议添加注释说明。

## 4. 生产配置安全

### 4.1 已修复项 (P0-04)

| 项 | 修复前 | 修复后 | 状态 |
|----|--------|--------|------|
| API Key 属性路径 | `gits.security.api-key` | `engagement.security.api-key` | ✅ 已修复 |
| Key rotation deadline 解析 | fail-open (返回 null) | fail-closed (抛异常) | ✅ 已修复 |
| Stacktrace 暴露 | 默认 (可能暴露) | `include-stacktrace: never` | ✅ 已修复 |

### 4.2 当前安全配置清单

```yaml
# application-prod.yaml
server:
  error:
    include-stacktrace: never    # ✅ P0-04 修复
    include-message: never       # ✅ P0-04 修复

engagement:
  security:
    api-key: ${API_KEY}          # ✅ fail-closed (无默认值)
    api-key-rotation-deadline:   # ✅ fail-closed (格式错误拒绝启动)
```

## 5. 开放项

| # | 项 | 风险 | 建议 | 优先级 |
|---|-----|------|------|--------|
| 1 | `application-local.yaml` 密码默认值 | 低 | 添加注释说明仅本地使用 | P3 |
| 2 | 定期复审 suppression | 中 | 建立 quarterly review 流程 | P2 |
| 3 | pre-commit hook 防止密钥提交 | 中 | 引入 gitleaks/talisman | P2 |

## 6. 变更记录

| 日期 | 变更 | 角色 |
|------|------|------|
| 2026-08-24 | 初始创建 | Feature Pilot (P24 REM-P1-05) |
