#!/usr/bin/env bash
# Strict environment calibration. Maven is provided by the repository wrapper
# (./mvnw), NOT by the system. Wrapper-first, fail-closed: never silently fall
# back to a system Maven that may be older than the project baseline.
set -euo pipefail

fail=0
err_file="$(mktemp)"
trap 'rm -f "${err_file}"' EXIT

require_command() {
    local name="$1"
    if ! command -v "${name}" >/dev/null 2>&1; then
        echo "FAIL: required command missing: ${name}"
        fail=1
    else
        echo "OK: ${name} -> $(command -v "${name}")"
    fi
}

# Tools that must exist on PATH. Maven is validated via the wrapper below.
for tool in java javac node npm python3 git rg; do
    require_command "${tool}"
done

# --- Java 21 gate (strict, fail-closed) ---
java_major="$(java -version 2>&1 | awk -F'[\".]' '/version/ {print $2; exit}')"
if [[ "${java_major}" != "21" ]]; then
    echo "FAIL: Java 21 required, found ${java_major:-unknown}"
    fail=1
else
    echo "OK: Java ${java_major}"
fi
javac_major="$(javac -version 2>&1 | awk '{print $2}' | cut -d. -f1)"
if [[ "${javac_major}" != "21" ]]; then
    echo "FAIL: javac 21 required, found ${javac_major:-unknown}"
    fail=1
else
    echo "OK: javac ${javac_major}"
fi

# --- Maven Wrapper gate (wrapper-first, fail-closed) ---
MVNW="./mvnw"
if [[ ! -f "${MVNW}" ]]; then
    echo "FAIL: Maven Wrapper missing: ${MVNW}"
    fail=1
elif [[ ! -x "${MVNW}" ]]; then
    echo "FAIL: Maven Wrapper not executable: ${MVNW}"
    fail=1
else
    if ! mvnw_out="$("${MVNW}" -version 2>"${err_file}")"; then
        echo "FAIL: Maven Wrapper failed to report version"
        head -n 5 "${err_file}" | sed 's/^/  /'
        fail=1
    else
        mvnw_version="$(printf '%s\n' "${mvnw_out}" | awk 'NR==1 {print $3}')"
        if [[ -z "${mvnw_version}" ]]; then
            echo "FAIL: could not parse Maven Wrapper version"
            fail=1
        elif [[ "$(printf '%s\n' "3.9.0" "${mvnw_version}" | sort -V | head -n1)" != "3.9.0" ]]; then
            echo "FAIL: Maven Wrapper version 3.9+ required, found ${mvnw_version}"
            fail=1
        else
            echo "OK: Maven Wrapper ${mvnw_version}"
        fi
    fi
fi

# --- Node 22+ gate ---
node_major="$(node --version | sed 's/^v//' | cut -d. -f1)"
if [[ "${node_major}" -ge 22 ]]; then
    echo "OK: Node ${node_major}"
else
    echo "FAIL: Node 22+ required, found ${node_major}"
    fail=1
fi

# --- Python 3.11+ gate ---
# 优先取 .venv 的解释器（与 Makefile 的 PYTHON 选择一致）。
# 动因：仓库 requires-python >= 3.11，而系统 python3 常为 3.10 ——
# 2026-09-13 实测系统 python3=3.10.12 使本项直接失败，
# 导致整个 `make verify` 链**不可用**（第一个目标即退出），
# 而 .venv 内为 3.12。检查器应认工程实际使用的解释器。
PY_BIN="python3"
for cand in .venv/bin/python .venv/bin/python3; do
    [[ -x "${cand}" ]] && { PY_BIN="${cand}"; break; }
done
python_version="$("${PY_BIN}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ "$(printf '%s\n' "3.11" "${python_version}" | sort -V | head -n1)" == "3.11" ]]; then
    echo "OK: Python ${python_version}"
else
    echo "FAIL: Python 3.11+ required, found ${python_version}"
    fail=1
fi

if [[ "${fail}" -ne 0 ]]; then
    echo "bootstrap-check: FAIL"
    exit 2
fi
echo "bootstrap-check: PASS"
