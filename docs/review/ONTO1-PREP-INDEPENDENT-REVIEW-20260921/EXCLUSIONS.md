# 排除项

- `*.pem`
- `*.key`
- `*.p12`
- `*.jks`
- `.env`
- `*.env`
- `.env.*`
- `.envrc`
- `id_rsa`
- `id_ed25519`
- `*.password`
- `*secret*.txt`
- `*credential*`
- `node_modules`
- `__pycache__`
- `.venv`
- `venv`
- `.tox`
- `.mypy_cache`
- `.pytest_cache`
- `*.pyc`
- `target/`
- `*.class`
- `*.jar`
- `dist/`
- `build/`

说明：源码包保留必要目录结构；**排除**密钥、真实银行客户数据、虚拟环境与缓存。
本仓库未包含真实客户数据文件（该判断由文件名与目录模式筛查得出，非内容级扫描）。
