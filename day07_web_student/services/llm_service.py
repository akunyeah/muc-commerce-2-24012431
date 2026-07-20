"""大模型问答服务：把 CSV 数据作为上下文，让大模型基于真实数据回答。

支持两种接入方式（通过 .env 配置切换）：
A. 标准 OpenAI 兼容 API（推荐，可对接 DeepSeek / Ollama / LM Studio / 豆包等）
   必设变量：OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
B. 阿里 DashScope（通义千问）
   必设变量：DASHSCOPE_API_KEY, DASHSCOPE_MODEL
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# 1. 把 data 目录的 CSV 转成大模型能理解的文本上下文
# ---------------------------------------------------------------------------
def build_context(base_dir: Path) -> str:
    """读取 data 目录 CSV，组装成结构化的文本上下文。"""
    data_dir = base_dir / "data"
    parts: list[str] = []

    # --- 总体指标 ---
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    lines = []
    for _, r in metrics_df.iterrows():
        name: str = str(r["指标"])
        value = float(r["数值"])
        if "率" in name or "占比" in name:
            lines.append(f"- {name}: {value:.2%}")
        elif value == int(value):
            lines.append(f"- {name}: {int(value)}")
        else:
            lines.append(f"- {name}: {value:.4f}")
    parts.append("【总体指标】\n" + "\n".join(lines))

    # --- 偏好品类分布 ---
    cat_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    header = "品类, 用户数, 流失率, 平均订单数, 平均优惠券数, 平均返现, 用户占比"
    rows = [header]
    for _, r in cat_df.iterrows():
        rows.append(
            f"{r['PreferedOrderCat']}, "
            f"{int(r['用户数'])}, "
            f"{float(r['流失率']):.2%}, "
            f"{float(r['平均订单数']):.2f}, "
            f"{float(r['平均优惠券数']):.2f}, "
            f"{float(r['平均返现']):.2f}, "
            f"{float(r['用户占比']):.2%}"
        )
    parts.append("【偏好品类分布】\n" + "\n".join(rows))

    # --- 生命周期分段 ---
    seg_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")
    col_days = "平均距上次下单天数" if "平均距上次下单天数" in seg_df.columns else "距上次下单天数"
    header = f"生命周期, 用户数, 流失人数, 流失率, 平均订单数, 平均返现, {col_days}"
    rows = [header]
    for _, r in seg_df.iterrows():
        rows.append(
            f"{r['TenureGroup']}, "
            f"{int(r['用户数'])}, "
            f"{int(r['流失人数'])}, "
            f"{float(r['流失率']):.2%}, "
            f"{float(r['平均订单数']):.2f}, "
            f"{float(r['平均返现']):.2f}, "
            f"{float(r[col_days]):.2f}"
        )
    parts.append("【用户生命周期分段】\n" + "\n".join(rows))

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# 2. 组装提示词（RAG 风格：上下文 + 约束 + 问题）
# ---------------------------------------------------------------------------
def build_system_prompt() -> str:
    """作为 system 消息发送：定义身份和严格的输出格式规则。"""
    return (
        "你是一位严谨的电商用户数据分析助手。\n"
        "你只能基于用户提供的统计数据进行回答，绝不可以编造数据或凭空推断。\n"
        "\n========== 输出格式协议（必须严格遵守）==========\n"
        "\n【关于换行的核心约定】\n"
        "1. 这是一个纯文本对话环境。你输出的每一个换行符（即 \\n，ASCII 码 10）都会被显示为屏幕上的一行换行。\n"
        "2. 每一条信息（每个数字指标、每个对比结论）必须独占一行，行与行之间用 \\n 分隔。\n"
        "3. 绝对禁止把多个条目挤在同一行内用空格或标点隔开。\n"
        "4. 不同主题之间（例如总体指标与分品类分析之间）必须留一个空行（即连续两个 \\n）。\n"
        "5. 每个以「-」或「1)」「2)」开头的条目，必须从新的一行开始。\n"
        "\n【格式要求】\n"
        "- 使用中文，简洁表达。\n"
        "- 百分比保留 2 位小数（例如 16.84%），普通数字保留 2 位小数（例如 2.96）。\n"
        "- 禁止使用竖线 | 、星号 **、反引号 `、三个以上破折号 ---、连续等号 === 等表格或代码标记。\n"
        "- 如果问题在数据中找不到答案，直接输出《无法回答》并简要说明原因。\n"
        "\n【正确的输出示范】\n"
        "总体指标：\n"
        "- 总用户数：5,630 人\n"
        "- 流失率：16.84%\n"
        "- 平均订单数：2.96 单\n"
        "\n"
        "分品类对比：\n"
        "1) 手机：用户数 2,080，流失率 27.40%，平均订单数 2.18\n"
        "2) 笔记本及配件：用户数 2,050，流失率 10.24%，平均订单数 2.77\n"
        "\n【错误的输出示范（绝对禁止）】\n"
        "总体指标：- 总用户数：5,630 - 流失率：16.84% - 平均订单数：2.96\n"
        "（错误原因：把多个条目挤在同一行，阅读困难。每个 - 开头的内容都必须独占一行。）"
    )


def build_user_prompt(context: str, question: str) -> str:
    """作为 user 消息发送：提供数据和具体问题。"""
    return (
        "以下是当前项目的统计数据，请基于这些数据回答问题：\n"
        "\n============ 数据开始 ============\n"
        f"{context}\n"
        "============ 数据结束 ============\n"
        f"\n\n请回答：{question}\n"
        "（请严格按照 system 消息中规定的换行和格式要求输出）"
    )


# ---------------------------------------------------------------------------
# 3. 调用大模型（支持 OpenAI 兼容 API 和 DashScope 两种入口）
# ---------------------------------------------------------------------------
def _call_openai_compatible(system_prompt: str, user_prompt: str) -> str:
    """方式 A：OpenAI 兼容 API（最灵活，可对接 DeepSeek / Ollama / LM Studio 等）。"""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("OPENAI_BASE_URL", "").strip().rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()

    if not api_key or not base_url:
        return (
            "【未配置 OpenAI 兼容 API】\n"
            "请在 day07_web_student/.env 中设置：\n"
            "  OPENAI_API_KEY=你的密钥\n"
            "  OPENAI_BASE_URL=https://api.deepseek.com/v1  (或其他兼容服务地址)\n"
            "  OPENAI_MODEL=deepseek-chat  (或其他模型名)\n"
            "\n然后重启 Flask。"
        )

    try:
        import json
        import urllib.request
        import urllib.error

        body = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            return f"【大模型返回结构异常】原始响应: {str(data)[:300]}"

    except urllib.error.HTTPError as e:
        return f"【大模型调用失败 HTTP {e.code}】{e.read().decode('utf-8', errors='ignore')[:300]}"
    except urllib.error.URLError as e:
        return f"【网络错误】无法访问 {base_url}：{e.reason}\n请检查 base_url 和网络连接。"
    except Exception as e:
        return f"【调用异常】{type(e).__name__}: {e}"


def _call_dashscope(system_prompt: str, user_prompt: str) -> str:
    """方式 B：阿里 DashScope（通义千问）。"""
    api_key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
    model = os.environ.get("DASHSCOPE_MODEL", "qwen-plus").strip()

    if not api_key:
        return (
            "【未配置 DashScope API Key】\n"
            "请在 day07_web_student/.env 中设置：\n"
            "  DASHSCOPE_API_KEY=你的密钥\n"
            "  DASHSCOPE_MODEL=qwen-plus\n"
            "\n然后重启 Flask。"
        )

    try:
        from dashscope import Generation  # type: ignore
    except ImportError:
        return "【缺少依赖】请先执行：pip install dashscope"

    resp = Generation.call(
        model=model,
        api_key=api_key,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    output = getattr(resp, "output", None) or {}
    text = output.get("text", "") if isinstance(output, dict) else ""
    if not text:
        return f"【DashScope 返回异常】原始响应: {str(resp)[:300]}"
    return text.strip()


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """统一入口：优先用 OpenAI 兼容配置，其次用 DashScope。"""
    has_openai = bool(os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_BASE_URL"))
    has_dashscope = bool(os.environ.get("DASHSCOPE_API_KEY"))

    if has_openai:
        return _call_openai_compatible(system_prompt, user_prompt)
    if has_dashscope:
        return _call_dashscope(system_prompt, user_prompt)

    return (
        "【尚未配置任何大模型 API】\n"
        "请在 day07_web_student/.env 中任选一种方式配置：\n"
        "\n方式一 · OpenAI 兼容（推荐，可接 DeepSeek / Ollama / LM Studio 等）：\n"
        "  OPENAI_API_KEY=你的密钥\n"
        "  OPENAI_BASE_URL=https://api.deepseek.com/v1\n"
        "  OPENAI_MODEL=deepseek-chat\n"
        "\n方式二 · 通义千问（DashScope）：\n"
        "  DASHSCOPE_API_KEY=你的密钥\n"
        "  DASHSCOPE_MODEL=qwen-plus\n"
        "\n保存 .env 后重启 Flask 即可生效。"
    )


# ---------------------------------------------------------------------------
# 4. 对外暴露的高层函数（由 qa_service 调用）
# ---------------------------------------------------------------------------
def _normalize_line_breaks(text: str) -> str:
    """
    确定性逐段扫描：把任何格式的模型输出统一为「标题 + 每行一条」。
    思路：
      1. 先全量压平已有的换行 → 变成一整行
      2. 用明确的模式逐个切分：
         - "xx：- " → 在冒号后换行
         - " - " → 换成 "\n- "
         - " N) " / " N）" → 换成 "\nN) "
         - 模式：2-6 字中文标题 + "：" + 中文内容 → 在冒号后换行
      3. 清理多余空行
    """
    import re

    # -------- 0. 基础清理 --------
    text = text.replace("**", "").replace("__", "")       # 去 Markdown 粗体
    # 把 \r\n 和 \r 统一为 \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # 把所有制表符和超长空白压成普通空格
    text = re.sub(r"[ \t]+", " ", text)

    # -------- 1. 先压平所有已有换行 → 我们重新按规则切 --------
    text = text.replace("\n", " ")
    # 再次清理多余空格
    text = re.sub(r" {2,}", " ", text).strip()

    # -------- 2. 逐轮切分 --------
    # 2a) 中文/英文标题 + 冒号 + 条目符号 → 强制在冒号后换行
    #     例："总体指标：- 总用户数..." → "总体指标：\n- 总用户数..."
    #     例："分品类对比：1) 手机..." → "分品类对比：\n1) 手机..."
    text = re.sub(
        r"([\u4e00-\u9fa5A-Za-z]{2,10}[:：])[ ]*(-|\d{1,2}[)）])",
        r"\1\n\2",
        text,
    )

    # 2b) 行内的 " - " → "\n- "（条目换行）
    #     注意：不替换句子开头的 "- "（本来就是换行）
    text = re.sub(r"[ ]+-[ ]+", "\n- ", text)

    # 2c) 行内的数字编号 " N) " 或 " N）" → "\nN) "
    text = re.sub(r"[ ]+(\d{1,2}[)）])[ ]+", r"\n\1 ", text)

    # 2d) 清理：行首的 "- " 或 "N) " 之前如果有残留空格，去掉
    text = re.sub(r"\n[ ]+(-|\d{1,2}[)）])", r"\n\1", text)

    # -------- 3. 清理多余空行和每行首尾空白 --------
    lines = [line.strip() for line in text.split("\n")]
    # 过滤完全空的行（但我们稍后会在主题标题间补一个空行）
    lines = [l for l in lines if l]

    # 4. 主题标题优化：标题行（以"xxx："结尾且不含数字指标）后补空行
    final_lines: list[str] = []
    for line in lines:
        final_lines.append(line)
        # 如果当前行是纯标题（结尾是冒号或内容短且像标题），补一个空行
        if re.search(r"[\u4e00-\u9fa5]{2,}[:：]$", line) or (
            len(line) < 12 and re.search(r"[\u4e00-\u9fa5]{2,}", line)
        ):
            final_lines.append("")  # 空行 → 主题分隔

    # 过滤开头/结尾的空行 + 中间最多 1 个空行
    result: list[str] = []
    prev_empty = False
    for line in final_lines:
        if not line:
            if not prev_empty and result:  # 不是开头，且上一行不是空行
                result.append("")
            prev_empty = True
        else:
            result.append(line)
            prev_empty = False

    return "\n".join(result).strip()


def llm_answer(base_dir: Path, question: str) -> str:
    """构建上下文 + 提示词，调用大模型并返回答案。"""
    context = build_context(base_dir)
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(context, question)
    answer = call_llm(system_prompt, user_prompt)

    # 关键：用确定性扫描把任何输出格式化成易读的分行
    answer = _normalize_line_breaks(answer)
    return answer or "（大模型未返回内容）"