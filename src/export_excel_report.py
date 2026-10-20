"""Create the polished Excel deliverable with artifact_tool (no openpyxl/pandas ExcelWriter)."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from artifact_tool import SpreadsheetFile, Workbook
from src.config import PROJECT_ROOT, OUTPUTS, REPORTS, DATA_RAW


NAVY = "#17365D"
BLUE = "#1F4E78"
PALE_BLUE = "#D9EAF7"
PALE_GREEN = "#E2F0D9"
GREY = "#F3F4F6"
WHITE = "#FFFFFF"


def safe_cell(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            value = value.item()
        except ValueError:
            pass
    if isinstance(value, pd.Timestamp):
        return value.isoformat(sep=" ")
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    return str(value)


def dataframe_matrix(df: pd.DataFrame) -> list[list]:
    return [[safe_cell(x) for x in row] for row in df.astype(object).values.tolist()]


def write_data_sheet(wb, name: str, df: pd.DataFrame, table_name: str | None = None):
    """Write a tidy data sheet with bounded widths and a frozen header."""
    sheet = wb.worksheets.add(name)
    headers = list(df.columns)
    matrix = [headers] + dataframe_matrix(df)
    if matrix:
        sheet.get_range_by_indexes(0, 0, len(matrix), len(headers)).values = matrix
        header = sheet.get_range_by_indexes(0, 0, 1, len(headers))
        header.format = {
            "fill": BLUE,
            "font": {"bold": True, "color": WHITE},
            "horizontal_alignment": "center",
            "vertical_alignment": "center",
            "wrap_text": True,
            "row_height": 30,
        }
        if len(matrix) > 1:
            sheet.get_range_by_indexes(1, 0, len(matrix) - 1, len(headers)).format.wrap_text = False
        sheet.freeze_panes.freeze_rows(1)
        # Avoid per-column autofit calls across thousands of rows. Bounded widths
        # keep large data sheets readable and make export much faster.
        sheet.get_range_by_indexes(0, 0, 1, len(headers)).format.column_width = 20
    return sheet

def _col_letter(n: int) -> str:
    result = ""
    while n:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def build_workbook() -> Path:
    claims = pd.read_csv(OUTPUTS / "telematics_claims_optimized.csv")
    holdout = pd.read_csv(OUTPUTS / "holdout_repair_cost_predictions.csv")
    garages = pd.read_csv(DATA_RAW / "partner_garages.csv")
    brand_summary = pd.read_csv(REPORTS / "brand_claim_cost_summary.csv")
    monthly = pd.read_csv(REPORTS / "monthly_claim_trends.csv")
    garage_summary = pd.read_csv(REPORTS / "garage_coverage_summary.csv")
    routing_summary = pd.read_csv(REPORTS / "routing_summary_by_brand.csv")
    feature_importance = pd.read_csv(REPORTS / "feature_importance.csv").head(25)
    model_metrics = json.loads((REPORTS / "model_evaluation.json").read_text(encoding="utf-8"))
    insights = json.loads((REPORTS / "business_insights.json").read_text(encoding="utf-8"))
    q_results = json.loads((REPORTS / "sql_question_run.json").read_text(encoding="utf-8"))
    q_index = pd.DataFrame([{
        "Question_ID": q["id"], "Category": q["category"], "Business_Question": q["title"],
        "SQL_Status": q["status"], "Rows_Returned": q["row_count"], "Business_Value": q["business_value"],
    } for q in q_results])
    data_dictionary = pd.read_csv(PROJECT_ROOT / "docs" / "data_dictionary_summary.csv")
    metrics_df = pd.DataFrame([
        {"Metric": key, "Value": value}
        for key, value in model_metrics.items()
        if isinstance(value, (str, int, float, bool)) or value is None
    ])

    wb = Workbook.create()
    dashboard = wb.worksheets.add("Executive_Dashboard")
    dashboard.merge_cells("A1:H1")
    dashboard.get_range("A1").values = [["AUTO INSURANCE TELEMATICS & GARAGE ROUTING"]]
    dashboard.get_range("A1:H1").format = {
        "fill": NAVY, "font": {"bold": True, "color": WHITE, "size": 16},
        "horizontal_alignment": "center", "vertical_alignment": "center", "row_height": 34,
    }
    dashboard.merge_cells("A2:H2")
    dashboard.get_range("A2").values = [["Synthetic portfolio analytics | Model test metrics are chronological holdout results"]]
    dashboard.get_range("A2:H2").format = {"fill": PALE_BLUE, "font": {"italic": True, "color": NAVY}, "wrap_text": True}
    kpis = [
        ["Claims", insights["claim_count"], "Distinct vehicles", insights["unique_vehicles"]],
        ["Partner garages", insights["garage_count"], "Claims routed", insights["claims_with_routing_recommendation"]],
        ["Total simulated repair cost (INR)", insights["total_simulated_repair_cost_inr"], "Average repair cost (INR)", insights["average_simulated_repair_cost_inr"]],
        ["Mean recommended distance (km)", insights["average_recommended_distance_km"], "Mean estimated cycle (hours)", insights["average_estimated_cycle_hours"]],
    ]
    dashboard.get_range("A4:D7").values = kpis
    dashboard.get_range("A4:A7").format = {"fill": GREY, "font": {"bold": True, "color": NAVY}, "wrap_text": True}
    dashboard.get_range("C4:C7").format = {"fill": GREY, "font": {"bold": True, "color": NAVY}, "wrap_text": True}
    dashboard.get_range("B4:B7").format = {"font": {"bold": True, "size": 12}}
    dashboard.get_range("D4:D7").format = {"font": {"bold": True, "size": 12}}
    dashboard.get_range("A4:D7").format.row_height = 28
    dashboard.get_range("F4:G10").values = [
        ["Holdout model metric", "Value"],
        ["MAE (INR)", round(model_metrics["MAE_INR"], 2)],
        ["RMSE (INR)", round(model_metrics["RMSE_INR"], 2)],
        ["R²", round(model_metrics["R2"], 4)],
        ["WAPE (%)", round(model_metrics["WAPE_PERCENT"], 2)],
        ["Median baseline MAE (INR)", round(model_metrics["Baseline_Median_MAE_INR"], 2)],
        ["Model MAE beats baseline", str(model_metrics["holdout_beats_baseline_on_MAE"])],
    ]
    dashboard.get_range("F4:G4").format = {"fill": BLUE, "font": {"bold": True, "color": WHITE}}
    dashboard.get_range("F5:F10").format = {"fill": GREY, "font": {"bold": True}}
    dashboard.merge_cells("A9:H9")
    dashboard.get_range("A9").values = [["Portfolio insights (synthetic data; not real insurer findings)"]]
    dashboard.get_range("A9:H9").format = {"fill": BLUE, "font": {"bold": True, "color": WHITE}}
    insight_text = [
        f"Speed-cost correlation: {insights['speed_repair_cost_pearson_correlation']}",
        f"G-force-cost correlation: {insights['gforce_repair_cost_pearson_correlation']}",
        f"Highest mean-cost make in sample: {insights['highest_average_cost_brand_in_sample']} (INR {insights['highest_average_cost_brand_mean_inr']:,.0f})",
        f"Preferred-partner fallback routes: {insights['preferred_partner_fallback_rate_pct']:.1f}%",
        f"Data range: {insights['date_min']} to {insights['date_max']}",
        "Routing heuristic: distance 60%, turnaround 30%, capacity 10% (assumed weights)",
        "All input records and coordinates are synthetic; routing times are modeled assumptions.",
    ]
    for i, text in enumerate(insight_text, start=10):
        dashboard.merge_cells(f"A{i}:H{i}")
        dashboard.get_range(f"A{i}").values = [[text]]
        dashboard.get_range(f"A{i}:H{i}").format = {"fill": WHITE if i % 2 else GREY, "wrap_text": True, "row_height": 23}
    dashboard.merge_cells("A18:H20")
    dashboard.get_range("A18").values = [["Interpretation warning: the repair-cost target is simulated from designed relationships. The reported model metrics measure learning this synthetic target, not real-world claim cost accuracy. The route score is a heuristic, not a guarantee of minimum live claim-cycle time."]]
    dashboard.get_range("A18:H20").format = {"fill": "#FFF2CC", "font": {"color": "#7F6000", "bold": True}, "wrap_text": True, "vertical_alignment": "center"}
    dashboard.get_range("A1:A25").format.column_width = 28
    dashboard.get_range("B1:B25").format.column_width = 21
    dashboard.get_range("C1:C25").format.column_width = 28
    dashboard.get_range("D1:D25").format.column_width = 21
    dashboard.get_range("E1:E25").format.column_width = 3
    dashboard.get_range("F1:F25").format.column_width = 27
    dashboard.get_range("G1:G25").format.column_width = 21
    dashboard.get_range("H1:H25").format.column_width = 18
    dashboard.freeze_panes.freeze_rows(2)

    # Sheet-specific data sheets with named Excel tables for filtering.
    write_data_sheet(wb, "Claims_Optimized", claims, "ClaimsOptimizedTable")
    write_data_sheet(wb, "Holdout_Evaluation", holdout, "HoldoutEvaluationTable")
    write_data_sheet(wb, "Garage_Network", garages, "GarageNetworkTable")
    write_data_sheet(wb, "Brand_Summary", brand_summary, "BrandSummaryTable")
    write_data_sheet(wb, "Garage_Coverage", garage_summary, "GarageCoverageTable")
    write_data_sheet(wb, "Routing_Summary", routing_summary, "RoutingSummaryTable")
    write_data_sheet(wb, "Monthly_Trend", monthly, "MonthlyTrendTable")
    write_data_sheet(wb, "Feature_Importance", feature_importance, "FeatureImportanceTable")
    write_data_sheet(wb, "Model_Metrics", metrics_df, "ModelMetricsTable")
    write_data_sheet(wb, "SQL_Question_Index", q_index, "SQLQuestionIndexTable")
    write_data_sheet(wb, "Data_Dictionary", data_dictionary, "DataDictionaryTable")

    output = OUTPUTS / "telematics_claims_optimized.xlsx"
    output.parent.mkdir(parents=True, exist_ok=True)
    SpreadsheetFile.export_xlsx(wb).save(str(output))
    # Avoid a full workbook-inspection pass here: the workbook contains several
    # thousand data rows. Output contents are checked separately by the pipeline.
    return output


if __name__ == "__main__":
    print(build_workbook())
