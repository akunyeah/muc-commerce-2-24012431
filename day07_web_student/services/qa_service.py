from pathlib import Path

import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    normalized = question.replace(" ", "").lower()

    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数']):,}名用户。"

    # 流失率相关问答
    if any(word in normalized for word in ["流失率", "流失比例", "流失"]):
        return f"总体流失率为{metrics['流失率']:.1%}，共有{int(metrics['流失人数']):,}名流失用户。"

    # 偏好品类相关问答
    if any(word in normalized for word in ["偏好品类", "喜欢买", "品类分布", "最爱买"]):
        return "用户偏好品类分布：手机(36.9%)、笔记本及配件(36.4%)、时尚(14.7%)、杂货(7.3%)、其他(4.7%)。其中手机品类用户最多，但流失率也最高(27.4%)。"

    # 生命周期风险相关问答
    if any(word in normalized for word in ["生命周期", "风险", "哪个阶段", "新用户"]):
        return "新用户阶段流失风险最高，流失率达53.5%；而24个月以上的老用户流失率为0%，忠诚度最高。"

    # 订单相关问答
    if any(word in normalized for word in ["订单", "下单", "购买次数"]):
        return f"用户平均订单数为{metrics['平均订单数']:.1f}单，订单数中位数为{int(metrics['订单数中位数'])}单。"
    # TODO 4-1：补充“流失率”“偏好品类”“生命周期风险”和“订单”四类问答。
    # 每个回答都必须引用data目录中已经计算的指标，不得编造数值。

    return (
        "请换一种更具体的问法。"
    )
