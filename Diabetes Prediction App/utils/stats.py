from datetime import datetime, timedelta


def format_predictions_for_timeline(predictions):
    """Format predictions for timeline display (Risk Trend)"""
    timeline = []
    for i, pred in enumerate(predictions):
        timeline.append({
            "index": i + 1,
            "date": pred["created_at"].strftime("%Y-%m-%d"),
            "time": pred["created_at"].strftime("%H:%M:%S"),
            "risk": pred["prediction"],
            "risk_label": "Positive ⚠️" if pred["prediction"] == 1 else "Negative ✓",
            "glucose": round(pred["glucose"], 2),
            "bmi": round(pred["bmi"], 2),
            "blood_pressure": round(pred["blood_pressure"], 2),
            "insulin": round(pred["insulin"], 2),
        })
    return timeline


def calculate_risk_distribution(predictions):
    """Calculate risk distribution (Pie Chart Data)"""
    if not predictions:
        return {"positive": 0, "negative": 0, "total": 0}

    total = len(predictions)
    positive = sum(1 for p in predictions if p["prediction"] == 1)
    negative = total - positive

    return {
        "positive": positive,
        "negative": negative,
        "total": total,
        "positive_percentage": round((positive / total) * 100, 1) if total > 0 else 0,
        "negative_percentage": round((negative / total) * 100, 1) if total > 0 else 0
    }


def calculate_health_metrics_average(predictions, group_by="all"):
    """Calculate average health metrics over time"""
    if not predictions:
        return {}

    if group_by == "all":
        # All predictions together
        groups = {"all_time": predictions}
    elif group_by == "monthly":
        # Group by month
        groups = {}
        for pred in predictions:
            month_key = pred["created_at"].strftime("%Y-%m")
            if month_key not in groups:
                groups[month_key] = []
            groups[month_key].append(pred)
    elif group_by == "weekly":
        # Group by week
        groups = {}
        for pred in predictions:
            week_key = pred["created_at"].strftime("%Y-W%W")
            if week_key not in groups:
                groups[week_key] = []
            groups[week_key].append(pred)
    else:
        groups = {"all_time": predictions}

    # Calculate averages for each group
    metrics = []
    for group_name, group_preds in groups.items():
        if group_preds:
            avg_glucose = sum(p["glucose"] for p in group_preds) / len(group_preds)
            avg_bmi = sum(p["bmi"] for p in group_preds) / len(group_preds)
            avg_bp = sum(p["blood_pressure"] for p in group_preds) / len(group_preds)
            avg_insulin = sum(p["insulin"] for p in group_preds) / len(group_preds)

            metrics.append({
                "period": group_name,
                "glucose": round(avg_glucose, 2),
                "bmi": round(avg_bmi, 2),
                "blood_pressure": round(avg_bp, 2),
                "insulin": round(avg_insulin, 2)
            })

    return metrics


def get_chart_data(predictions):
    """Prepare all chart data in one call"""
    if not predictions:
        return {
            "timeline": [],
            "risk_distribution": {"positive": 0, "negative": 0, "total": 0},
            "health_metrics": [],
            "summary": {
                "total_tests": 0,
                "positive_count": 0,
                "negative_count": 0,
                "positive_percentage": 0,
                "negative_percentage": 0
            }
        }

    timeline = format_predictions_for_timeline(predictions)
    distribution = calculate_risk_distribution(predictions)
    metrics = calculate_health_metrics_average(predictions, "all")

    return {
        "timeline": timeline,
        "risk_distribution": distribution,
        "health_metrics": metrics,
        "summary": {
            "total_tests": len(predictions),
            "positive_count": distribution["positive"],
            "negative_count": distribution["negative"],
            "positive_percentage": distribution["positive_percentage"],
            "negative_percentage": distribution["negative_percentage"]
        }
    }


def format_for_json(data):
    """Convert datetime objects to ISO format for JSON serialization"""
    if isinstance(data, dict):
        return {key: format_for_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [format_for_json(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data
