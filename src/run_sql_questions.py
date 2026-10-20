"""Execute the SQL question bank and export answer tables and a study guide."""
from __future__ import annotations
import json
import re
import sqlite3
from pathlib import Path
import pandas as pd
from src.config import DATABASE_PATH, SQL_RESULTS, REPORTS, PROJECT_ROOT
from src.sql_catalog import QUESTIONS


def to_mysql8(sql: str) -> str:
    """Translate date and scalar math functions in this curated query bank to MySQL 8."""
    result = sql
    # Replace the full CAST expressions before their inner strftime calls.
    result = result.replace("CAST(strftime('%w', AccidentDate) AS INTEGER)", "(DAYOFWEEK(AccidentDate) - 1)")
    result = result.replace("CAST(strftime('%H', AccidentDate) AS INTEGER)", "HOUR(AccidentDate)")
    result = result.replace("CAST(strftime('%Y', AccidentDate) AS INTEGER)", "YEAR(AccidentDate)")
    result = result.replace("strftime('%Y-%m', AccidentDate)", "DATE_FORMAT(AccidentDate, '%Y-%m')")
    result = result.replace("strftime('%Y', AccidentDate)", "CAST(YEAR(AccidentDate) AS CHAR)")
    result = result.replace("strftime('%m', AccidentDate)", "LPAD(MONTH(AccidentDate), 2, '0')")
    result = result.replace("sqrt(MAX(s.var_cost, 0))", "SQRT(GREATEST(s.var_cost, 0))")
    return result


def run_questions() -> tuple[list[dict], int]:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("SQLite database is missing; run src.run_pipeline first.")
    SQL_RESULTS.mkdir(parents=True, exist_ok=True)
    # Remove stale answer exports when question titles or SQL definitions change.
    for previous_export in SQL_RESULTS.glob("*.csv"):
        previous_export.unlink()
    query_results = []
    successes = 0
    with sqlite3.connect(DATABASE_PATH) as conn:
        for q in QUESTIONS:
            try:
                df = pd.read_sql_query(q["sql"], conn)
                df.to_csv(SQL_RESULTS / f"{q['id']}_{_slug(q['title'])}.csv", index=False)
                result = {**q, "status": "PASS", "row_count": int(len(df)), "columns": list(df.columns), "preview": df.head(8).to_dict(orient="records")}
                successes += 1
            except Exception as exc:  # Record failure in guide; pipeline validation will report it.
                result = {**q, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}", "row_count": 0, "columns": [], "preview": []}
            query_results.append(result)

    (REPORTS / "sql_question_run.json").write_text(json.dumps(query_results, indent=2, default=str), encoding="utf-8")
    sqlite_sql = ["-- SQLite SQL practice bank. Tables are created by src/build_sqlite_database.py.\n"]
    mysql_sql = ["-- MySQL 8 query bank. Import the source CSVs and routing/model output tables first.\n"]
    md = ["# SQL Questions and Executed Answers", "", f"**Executed:** {successes}/{len(QUESTIONS)} questions passed on the current dataset.", "", "SQL result CSVs are in `reports/sql_results/`. This is simulated portfolio data, so interpret patterns as demonstrations, not real insurer findings.", ""]
    for q in query_results:
        label = f"-- {q['id']} [{q['category']}]: {q['title']}\n"
        sqlite_sql.append(label + q["sql"].rstrip(";") + ";\n\n")
        mysql_sql.append(label + to_mysql8(q["sql"]).rstrip(";") + ";\n\n")
        md.extend([f"## {q['id']}. {q['title']}", "", f"**Category:** {q['category']}  ", f"**Business value:** {q['business_value']}", ""])
        md.extend(["```sql", q["sql"], "```", ""])
        if q["status"] == "PASS":
            md.append(f"**Result:** {q['row_count']} row(s) returned. Preview:")
            if q["preview"]:
                df = pd.DataFrame(q["preview"])
                preview = df.head(8)
                md.append("| " + " | ".join(map(str, preview.columns)) + " |")
                md.append("| " + " | ".join(["---"] * len(preview.columns)) + " |")
                for _, row in preview.iterrows():
                    md.append("| " + " | ".join(str(v).replace("|", "\\|") for v in row.tolist()) + " |")
            else:
                md.append("Query returned no rows.")
        else:
            md.append(f"**Execution issue:** `{q['error']}`. See `reports/sql_question_run.json`.")
        md.append("")

    (PROJECT_ROOT / "sql" / "analytics_questions_sqlite.sql").write_text("".join(sqlite_sql), encoding="utf-8")
    (PROJECT_ROOT / "sql" / "analytics_questions_mysql8.sql").write_text("".join(mysql_sql), encoding="utf-8")
    (REPORTS / "SQL_Questions_and_Answers.md").write_text("\n".join(md), encoding="utf-8")
    return query_results, successes


def _slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return text[:70]


if __name__ == "__main__":
    results, successes = run_questions()
    print(f"SQL questions passed: {successes}/{len(results)}")
    for r in results:
        if r["status"] != "PASS":
            print(r["id"], r["error"])
