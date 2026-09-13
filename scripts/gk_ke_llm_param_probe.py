#!/usr/bin/env python3
"""最小验证：请求级 temperature/seed 是否真的生效并**可回读**。

只做 1 次调用，用于在跑完整确定性实验**之前**证明接线正确。
若本步不通过，跑 5 次采样没有意义。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

KERT = Path('/home/szf/dev/Leibniz-KERT')
sys.path.insert(0, str(KERT / 'src'))

# 端点来源：
#  优先 Owner 指定的 DSEEK_2026_SZF_KEY；
#  缺失时回退到仓库自带机制（~/.dsh/.credentials.yaml 的 DEEPSEEK_API_KEY）。
key = os.environ.get('DSEEK_2026_SZF_KEY', '')
key_src = 'DSEEK_2026_SZF_KEY(Owner 指定)'
if not key:
    try:
        import yaml
        cred = yaml.safe_load(open(Path.home() / '.dsh' / '.credentials.yaml'))
        key = (cred or {}).get('DEEPSEEK_API_KEY', '')
        key_src = '~/.dsh/.credentials.yaml:DEEPSEEK_API_KEY(仓库自带机制，回退)'
    except Exception as exc:
        print(f'FAIL: 无法取得密钥 — {exc}')
        raise SystemExit(1)

if not key:
    print('FAIL: 未取到任何 DeepSeek 密钥')
    raise SystemExit(1)

os.environ['KERT_LLM_BASE_URL'] = 'https://api.deepseek.com'
os.environ['KERT_LLM_API_KEY'] = key
os.environ['KERT_LLM_MODEL'] = os.environ.get('KERT_LLM_MODEL', 'deepseek-flash')

from kert.infrastructure.adapters import llm as L  # noqa: E402

ad = L.create_llm_adapter('probe')
print(f'  适配器: {type(ad).__name__}   model={getattr(ad, "model", "-")}')
print(f'  密钥来源: {key_src}（不打印密钥）')
if isinstance(ad, L.DeterministicLlmAdapter):
    print('FAIL: 回退到确定性桩 —— 本次验证无意义，且**不得**用它跑确定性实验')
    raise SystemExit(1)

REQ_TEMP, REQ_SEED = 0.5, 42
print(f'  请求参数: temperature={REQ_TEMP} seed={REQ_SEED}')
try:
    res = ad.complete('你是助手。', '只回答一个词：好', temperature=REQ_TEMP, seed=REQ_SEED)
except Exception as exc:
    print(f'FAIL: 调用失败 — {exc}')
    raise SystemExit(1)

print(f'  ✅ 调用成功  模型回报 model_id={res.model_id}')
print(f'  ★ 生效 temperature={res.temperature}  seed={res.seed}   '
      f'（请求 {REQ_TEMP}/{REQ_SEED}）')
ok = (res.temperature == REQ_TEMP and res.seed == REQ_SEED)
print('  ★ 参数回读一致' if ok else '  ✗ **参数未按请求生效** —— 接线有问题')
print(f'  输出前 60 字符: {res.text[:60]!r}')
raise SystemExit(0 if ok else 1)
