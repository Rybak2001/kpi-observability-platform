from flask import Blueprint, jsonify, request
from app.db import query, execute
from app.routes.auth import login_required

bp = Blueprint("api", __name__)


@bp.route("/sources", methods=["GET"])
@login_required
def get_sources():
    rows = query("SELECT * FROM kpi_sources ORDER BY name")
    return jsonify(rows)


@bp.route("/sources", methods=["POST"])
@login_required
def create_source():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    execute(
        "INSERT INTO kpi_sources (name, source_type, url) VALUES (%s, %s, %s)",
        (data["name"], data.get("source_type", "manual"), data.get("url")),
    )
    return jsonify({"ok": True}), 201


@bp.route("/metrics", methods=["GET"])
@login_required
def get_metrics():
    source_id = request.args.get("source_id")
    metric = request.args.get("metric")
    limit = min(int(request.args.get("limit", 100)), 500)

    sql = "SELECT m.*, s.name as source_name FROM kpi_metrics m JOIN kpi_sources s ON s.id = m.source_id WHERE 1=1"
    params = []

    if source_id:
        sql += " AND m.source_id = %s"
        params.append(int(source_id))
    if metric:
        sql += " AND m.metric_name = %s"
        params.append(metric)

    sql += " ORDER BY m.period_date DESC LIMIT %s"
    params.append(limit)

    rows = query(sql, params)
    return jsonify(rows)


@bp.route("/metrics", methods=["POST"])
@login_required
def create_metric():
    data = request.get_json()
    required = ["source_id", "metric_name", "metric_value", "period_date"]
    if not data or not all(data.get(k) for k in required):
        return jsonify({"error": f"Required: {', '.join(required)}"}), 400
    execute(
        "INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES (%s, %s, %s, %s, %s)",
        (data["source_id"], data["metric_name"], data["metric_value"], data.get("unit", ""), data["period_date"]),
    )
    return jsonify({"ok": True}), 201


@bp.route("/metrics/summary", methods=["GET"])
@login_required
def metrics_summary():
    rows = query("""
        SELECT metric_name,
               ROUND(AVG(metric_value)::numeric, 2) as avg_val,
               ROUND(MAX(metric_value)::numeric, 2) as max_val,
               ROUND(MIN(metric_value)::numeric, 2) as min_val,
               COUNT(*) as data_points
        FROM kpi_metrics
        GROUP BY metric_name
        ORDER BY metric_name
    """)
    return jsonify(rows)


@bp.route("/export/csv", methods=["GET"])
@login_required
def export_csv():
    rows = query("""
        SELECT m.metric_name, m.metric_value, m.unit, m.period_date, s.name as source_name
        FROM kpi_metrics m
        JOIN kpi_sources s ON s.id = m.source_id
        ORDER BY m.period_date DESC
    """)
    lines = ["source,metric,value,unit,date"]
    for r in rows:
        lines.append(f"{r['source_name']},{r['metric_name']},{r['metric_value']},{r['unit']},{r['period_date']}")
    csv_content = "\n".join(lines)
    return csv_content, 200, {"Content-Type": "text/csv", "Content-Disposition": "attachment; filename=kpis.csv"}
