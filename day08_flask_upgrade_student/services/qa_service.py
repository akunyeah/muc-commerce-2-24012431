from pathlib import Path

import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    segment_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")
    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    normalized = question.replace(" ", "").lower()

    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数']):,}名用户。"
    if "流失率" in normalized or "流失比例" in normalized:
        return f"总体流失率为{metrics['流失率']:.1%}，共有{int(metrics['流失人数']):,}名流失用户。"
    if any(word in normalized for word in ["品类", "类别", "最受欢迎"]):
        row = category_df.loc[category_df["用户数"].idxmax()]
        return f"用户数最多的偏好品类是{row['PreferedOrderCat']}，共有{int(row['用户数']):,}名用户。"
    if any(word in normalized for word in ["新用户", "任期", "生命周期", "高风险"]):
        row = segment_df.loc[segment_df["流失率"].idxmax()]
        return f"{row['TenureGroup']}的流失率最高，为{row['流失率']:.1%}。该结论仅描述数据现象。"
    if any(word in normalized for word in ["订单", "下单"]):
        return f"用户平均订单数为{metrics['平均订单数']:.2f}单，中位数为{metrics['订单数中位数']:.0f}单。"

    return (
        "我暂时只能回答总用户数、总体流失率、偏好品类、生命周期风险和订单情况。"
        "请换一种更具体的问法。"
    )
