from pathlib import Path

import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")

def export_category_csv(base_dir: Path, selected_category: str = "全部") -> bytes:
    """根据选中品类筛选数据，并返回 utf-8-sig 编码的 CSV 字节串。"""
    data_dir = base_dir / "data"
    category_df = _read_csv(data_dir / "category_analysis.csv")

    table_df = category_df.copy()
    if selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category]
    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )[["偏好品类", "用户数", "流失率", "平均订单数"]]

    return table_df.to_csv(index=False).encode("utf-8-sig")


def load_dashboard_data(base_dir: Path, selected_category: str = "全部") -> dict:
    data_dir = base_dir / "data"
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    metric_map = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    # TODO 2-1：在已有两张指标卡基础上，增加“总体流失率”和“平均订单数”。
    metrics = [
    {"label": "总用户数", "value": f"{int(metric_map['用户数']):,}", "note": "人"},
    {"label": "流失用户", "value": f"{int(metric_map['流失人数']):,}", "note": "人"},
    {"label": "总体流失率", "value": f"{metric_map['流失率']:.2%}", "note": ""},
    {"label": "平均订单数", "value": f"{metric_map['平均订单数']:.2f}", "note": "单"},
]

    categories = ["全部", *category_df["PreferedOrderCat"].tolist()]
    table_df = category_df.copy()
    # TODO 3-1：选择具体品类后筛选table_df。
    # 提示：教师参考项目中使用布尔条件筛选。
    if selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category]
    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )[["偏好品类", "用户数", "流失率", "平均订单数"]]
    table_df["流失率"] = table_df["流失率"].map(lambda value: f"{value:.1%}")
    table_df["平均订单数"] = table_df["平均订单数"].map(lambda value: f"{value:.2f}")

    # TODO 2-2：找出流失率最高的生命周期阶段，并生成一句数据观察。
    max_churn_segment = segment_df.loc[segment_df["流失率"].idxmax()]
    stage = max_churn_segment["TenureGroup"]
    churn_rate = max_churn_segment["流失率"]

    # 生成数据洞察
    insight = f"风险预警：{stage}阶段流失率最高，达到{churn_rate:.2%}，建议重点关注该群体的留存策略。"

    return {
            "metrics": metrics,
            "categories": categories,
            "category_rows": table_df.to_dict("records"),
            "insight": insight,
        }
