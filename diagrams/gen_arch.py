#!/usr/bin/env python3
"""GITS-KNE 架构图生成器：数据驱动 + 连线端点几何验证。
所有连线必须从源节点边界出发、终止于目标节点边界，否则程序报错退出。
"""
from __future__ import annotations

# ---------------------------------------------------------------
# 数据定义：节点与连线
# ---------------------------------------------------------------

# 5 列中心（领域/适配器/前端 对齐）；数据层 4 列单独
# 列中心间距 180，节点宽 140 → 相邻节点水平间隙 40px
COL5 = [200, 380, 560, 740, 920]
NODE_W = 140
NODE_X0 = [c - NODE_W // 2 for c in COL5]  # 130, 310, 490, 670, 850
NODE_X1 = [c + NODE_W // 2 for c in COL5]  # 270, 450, 630, 810, 990

# 数据层 4 列（对齐到对应适配器列中心）
DATA_C = [200, 380, 740, 920]
DATA_W = 120

# 层 y 边界（4px 网格）
FRONT_Y, FRONT_H = 84, 44
APPBAND_TOP, APPBAND_BOT = 232, 292
MODULE_Y, MODULE_H = 392, 56
ADAPTER_Y, ADAPTER_H = 640, 52
DATA_Y, DATA_H = 824, 36

ZONE = {
    "front":   (80, 56, 1040, 92),
    "app":     (80, 200, 1040, 104),
    "module":  (80, 360, 1040, 140),
    "adapter": (80, 608, 1040, 116),
    "data":    (80, 800, 1040, 72),
}

# 节点定义
FRONT = [
    ("客户经营概览", "Dashboard", False),
    ("客户经营视图", "CustomerOperatingView", False),
    ("持续经营工作台", "EngagementWorkspace", True),   # coral focal
    ("承诺·任务管理", "Commitment · Task", False),
    ("会中·审计·外部事件", "InMeeting · Audit · Event", False),
]

MODULE = [
    ("运行本体", "operational-ontology", "Port 接口"),
    ("语义运行时", "semantic-runtime", "查询 · 规则"),
    ("证据上下文", "context-evidence", "EvidenceBundle"),
    ("受控动作", "human-action", "门禁 · CRM回写"),
    ("客户旅程编排", "customer-journey", "M17→M22 编排"),
]

ADAPTER = [
    ("关系持久化", "persistence-relational"),
    ("语义仓库", "semantic-jena"),
    ("DKWS 模拟平台", "dkws-platform · 待集成"),
    ("Oracle 只读源", "oracle-source · 隔离"),
    ("事件·回写通道", "Channel 适配器"),
]

DATA = [
    ("H2 / MySQL", "200"),
    ("Jena 语义库", "380"),
    ("Oracle 源库", "740"),
    ("外部事件", "920"),
]

# ---------------------------------------------------------------
# 几何验证
# ---------------------------------------------------------------

def rect_contains(x, y, rx, ry, rw, rh, eps=0.5):
    return (rx - eps <= x <= rx + rw + eps) and (ry - eps <= y <= ry + rh + eps)

errors = []

# 前端节点范围
front_ranges = [(NODE_X0[i], FRONT_Y, NODE_W, FRONT_H) for i in range(5)]
# 领域节点范围
mod_ranges = [(NODE_X0[i], MODULE_Y, NODE_W, MODULE_H) for i in range(5)]
# 适配器节点范围
adp_ranges = [(NODE_X0[i], ADAPTER_Y, NODE_W, ADAPTER_H) for i in range(5)]
# 数据节点范围（x = 中心-80）
data_ranges = [(c - DATA_W // 2, DATA_Y, DATA_W, DATA_H) for c in DATA_C]

def check_endpoint(desc, x, y, ranges):
    ok = any(rect_contains(x, y, *r) for r in ranges)
    if not ok:
        errors.append(f"{desc}: endpoint ({x},{y}) not inside any node {ranges}")

# 1) 前端 → 应用带
for c in COL5:
    check_endpoint(f"front→appband start x={c}", c, FRONT_Y + FRONT_H, front_ranges)
    check_endpoint(f"front→appband end x={c}", c, APPBAND_TOP, [(110, APPBAND_TOP, 900, APPBAND_BOT - APPBAND_TOP)])

# 2) 应用带 → 领域
for c in COL5:
    check_endpoint(f"appband→module start x={c}", c, APPBAND_BOT, [(110, APPBAND_TOP, 900, APPBAND_BOT - APPBAND_TOP)])
    check_endpoint(f"appband→module end x={c}", c, MODULE_Y, mod_ranges)

# 3) 领域 → 适配器
for c in COL5:
    check_endpoint(f"module→adapter start x={c}", c, MODULE_Y + MODULE_H, mod_ranges)
    check_endpoint(f"module→adapter end x={c}", c, ADAPTER_Y, adp_ranges)

# 4) 适配器 → 数据
for c in DATA_C:
    check_endpoint(f"adapter→data start x={c}", c, ADAPTER_Y + ADAPTER_H, adp_ranges)
    check_endpoint(f"adapter→data end x={c}", c, DATA_Y, data_ranges)

# 5) Worker → 客户旅程编排（虚线异步）
# Worker 节点: x=940-1060 y=244-288 (底=288); 客户旅程编排: x=850-990 y=392-448
# 路径 M 1000,288 H 950 V 392
WORKER_BOT = 288
check_endpoint("worker start", 1000, WORKER_BOT, [(940, 244, 120, 44)])
check_endpoint("worker→module end", 950, MODULE_Y, mod_ranges)

# ---------------------------------------------------------------
# HTML 生成
# ---------------------------------------------------------------

FONT = "'Geist', 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif"
FONTM = "'Geist Mono', ui-monospace, 'PingFang SC', monospace"

def node_rect(x, y, w, h, fill, stroke):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'

def text(cx, cy, s, fill, size, font=FONT, weight=400, anchor="middle", lh=0):
    t = f'<text x="{cx}" y="{cy}" fill="{fill}" font-size="{size}" font-family="{font}" text-anchor="{anchor}"'
    if weight != 400:
        t += f' font-weight="{weight}"'
    t += f'>{s}</text>'
    return t

def main():
    if errors:
        print("GEOMETRY ERRORS:")
        for e in errors:
            print("  -", e)
        raise SystemExit(1)
    print(f"GEOMETRY OK: {len(COL5)*3 + len(DATA_C)*2} connections verified")

    parts = []

    # zones
    for label, (zx, zy, zw, zh) in [
        ("前端", ZONE["front"]), ("应用", ZONE["app"]), ("领域模块", ZONE["module"]),
        ("适配器", ZONE["adapter"]), ("数据", ZONE["data"])]:
        parts.append(f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" rx="8" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>')
        lw = 72 if label == "领域模块" else 64
        parts.append(f'<rect x="{zx+4}" y="{zy+4}" width="{lw}" height="12" rx="2" fill="#f5f5f5"/>')
        parts.append(f'<text x="{zx+4+lw//2}" y="{zy+14}" fill="rgba(45,49,66,0.40)" font-size="7" font-family="{FONTM}" text-anchor="middle" letter-spacing="0.14em">{label}</text>')

    # connectors (before nodes)
    # front -> appband
    for c in COL5:
        parts.append(f'<path d="M {c},{FRONT_Y+FRONT_H} V {APPBAND_TOP}" fill="none" stroke="#4f5d75" stroke-width="1.2" marker-end="url(#arrow)"/>')
    parts.append('<rect x="536" y="172" width="48" height="12" rx="2" fill="#f5f5f5"/>')
    parts.append(text(560, 181, "REST", "#4f5d75", 8, FONTM))

    # appband -> module
    for c in COL5:
        parts.append(f'<path d="M {c},{APPBAND_BOT} V {MODULE_Y}" fill="none" stroke="#4f5d75" stroke-width="1.2" marker-end="url(#arrow)"/>')

    # module -> adapter
    for c in COL5:
        parts.append(f'<path d="M {c},{MODULE_Y+MODULE_H} V {ADAPTER_Y}" fill="none" stroke="#4f5d75" stroke-width="1.2" marker-end="url(#arrow)"/>')

    # adapter -> data
    for c in DATA_C:
        parts.append(f'<path d="M {c},{ADAPTER_Y+ADAPTER_H} V {DATA_Y}" fill="none" stroke="#4f5d75" stroke-width="1.2" marker-end="url(#arrow)"/>')

    # Worker -> 客户旅程编排（虚线异步）
    parts.append(f'<path d="M 1000,{WORKER_BOT} H 950 V {MODULE_Y}" fill="none" stroke="#4f5d75" stroke-width="1" stroke-dasharray="5,4" marker-end="url(#arrow)"/>')
    # EVENT 标签（遮罩放在右侧空白）
    parts.append('<rect x="1008" y="308" width="60" height="12" rx="2" fill="#f5f5f5"/>')
    parts.append(text(1038, 317, "EVENT", "#4f5d75", 8, FONTM))

    # front nodes
    for i, (name, sub, focal) in enumerate(FRONT):
        x, c = NODE_X0[i], COL5[i]
        if focal:
            parts.append(f'<rect x="{x}" y="{FRONT_Y}" width="{NODE_W}" height="{FRONT_H}" rx="6" fill="#eb6c36" fill-opacity="0.08" stroke="#eb6c36" stroke-width="1"/>')
        else:
            parts.append(node_rect(x, FRONT_Y, NODE_W, FRONT_H, "#ffffff", "#2d3142"))
        parts.append(text(c, FRONT_Y + 17, name, "#2d3142", 12, FONT, 600))
        parts.append(text(c, FRONT_Y + 32, sub, "#4f5d75", 9, FONTM))

    # app band (container)
    parts.append(f'<rect x="110" y="{APPBAND_TOP}" width="900" height="60" rx="8" fill="rgba(235,108,54,0.04)" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>')
    # API sub-node
    parts.append(f'<rect x="200" y="244" width="720" height="44" rx="6" fill="#eb6c36" fill-opacity="0.08" stroke="#eb6c36" stroke-width="1"/>')
    parts.append(text(560, 261, "GitsKnoApiApplication · apps/api :8080 REST", "#2d3142", 12, FONT, 600))
    parts.append(text(560, 277, "主 API 服务 · 调度领域模块 · 承载 OpenAPI", "#4f5d75", 9, FONTM))
    # Worker sub-node
    parts.append(f'<rect x="940" y="244" width="120" height="44" rx="6" fill="#ffffff" stroke="#2d3142" stroke-width="1"/>')
    parts.append(text(1000, 262, "Worker", "#2d3142", 12, FONT, 600))
    parts.append(text(1000, 277, ":8090 异步", "#4f5d75", 9, FONTM))

    # module nodes
    for i, (name, sub1, sub2) in enumerate(MODULE):
        x, c = NODE_X0[i], COL5[i]
        parts.append(node_rect(x, MODULE_Y, NODE_W, MODULE_H, "#ffffff", "#2d3142"))
        parts.append(text(c, MODULE_Y + 19, name, "#2d3142", 12, FONT, 600))
        parts.append(text(c, MODULE_Y + 35, sub1, "#4f5d75", 9, FONTM))
        parts.append(text(c, MODULE_Y + 47, sub2, "#4f5d75", 9, FONTM))

    # module zone note
    parts.append(text(110, 484, "+ evaluation · knowledge-architecture · scenario 等模块（Port 接口）", "#7a8399", 9, FONTM, anchor="start"))

    # adapter nodes
    for i, (name, sub) in enumerate(ADAPTER):
        x, c = NODE_X0[i], COL5[i]
        parts.append(node_rect(x, ADAPTER_Y, NODE_W, ADAPTER_H, "#ffffff", "#2d3142"))
        parts.append(text(c, ADAPTER_Y + 18, name, "#2d3142", 12, FONT, 600))
        parts.append(text(c, ADAPTER_Y + 34, sub, "#4f5d75", 9, FONTM))

    # data nodes
    for name, cx in DATA:
        c = int(cx)
        parts.append(f'<rect x="{c - DATA_W//2}" y="{DATA_Y}" width="{DATA_W}" height="{DATA_H}" rx="6" fill="rgba(45,49,66,0.05)" stroke="#4f5d75" stroke-width="1"/>')
        parts.append(text(c, DATA_Y + 23, name, "#2d3142", 12, FONT, 600))

    # legend
    parts.append(f'<line x1="120" y1="884" x2="1080" y2="884" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>')
    parts.append(text(120, 892, "LEGEND", "#4f5d75", 8, FONTM, anchor="start", lh=1))
    parts.append(text(340, 892, "实线 = 调用", "#4f5d75", 8, FONTM, anchor="start"))

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GITS-KNE 系统架构图</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --color-paper:   #f5f5f5; --color-ink: #2d3142; --color-muted: #4f5d75; --color-accent: #eb6c36;
      --font-sans: 'Geist', 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
      --font-serif: 'Instrument Serif', 'Noto Serif CJK SC', serif;
      --font-mono: 'Geist Mono', ui-monospace, 'SF Mono', Menlo, monospace;
    }}
    body {{ font-family: var(--font-sans); background: var(--color-paper); color: var(--color-ink); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 3rem 2rem; }}
    .frame {{ max-width: 1280px; width: 100%; }}
    .eyebrow {{ font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: var(--color-muted); margin-bottom: 0.5rem; }}
    h1 {{ font-family: var(--font-serif); font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem); font-weight: 400; letter-spacing: -0.02em; line-height: 1.15; color: var(--color-ink); margin-bottom: 0.5rem; }}
    .subtitle {{ color: var(--color-muted); font-size: 0.9rem; margin-bottom: 1.5rem; }}
    svg {{ width: 100%; min-width: 1080px; display: block; }}
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">Architecture · GITS-KNE</p>
    <h1>客户经理持续经营智能体 — 系统架构</h1>
    <p class="subtitle">杭州银行知识工程体系 · 模块化单体（Spring Modulith）+ 独立 Worker · 语义合同驱动</p>
    <svg viewBox="0 0 1200 900" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="gits-arch-title gits-arch-desc">
      <title id="gits-arch-title">GITS-KNE 客户经理持续经营智能体系统架构</title>
      <desc id="gits-arch-desc">分层架构：Vue3 前端 → Spring Boot API/Worker 应用 → 领域模块 Port 接口 → 适配器实现 → 关系库/语义库/外部数据源，各层通过合同解耦。</desc>
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#4f5d75"/></marker>
        <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#eb6c36"/></marker>
        <marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#2e5aa8"/></marker>
      </defs>
      <rect width="100%" height="100%" fill="#f5f5f5"/>
      {chr(10).join(parts)}
    </svg>
  </div>
</body>
</html>
"""
    with open("diagrams/architecture.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("WROTE diagrams/architecture.html")

if __name__ == "__main__":
    main()
