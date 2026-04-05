from datetime import datetime, timedelta
from typing import List, Dict, Any


def format_predictions_for_timeline(predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format predictions for timeline display (Risk Trend).
    Ensures chronological order from oldest to newest.
    """
    # Sort by created_at to ensure ascending order (oldest first)
    sorted_predictions = sorted(predictions, key=lambda x: x["created_at"])
    
    timeline = []
    for i, pred in enumerate(sorted_predictions):
        timeline.append({
            "index": i + 1,
            "date": pred["created_at"].strftime("%Y-%m-%d"),
            "time": pred["created_at"].strftime("%H:%M:%S"),
            "risk": pred["prediction"],
            "risk_label": "Positive [WARN]" if pred["prediction"] == 1 else "Negative [OK]",
            "glucose": round(pred["glucose"], 2),
            "bmi": round(pred["bmi"], 2),
            "blood_pressure": round(pred["blood_pressure"], 2),
            "insulin": round(pred["insulin"], 2),
        })
    return timeline


def calculate_risk_distribution(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def calculate_health_metrics_average(predictions: List[Dict[str, Any]], group_by: str = "all") -> List[Dict[str, Any]]:
    """
    Calculate average health metrics over time.
    Ensures predictions are sorted chronologically before grouping.
    """
    if not predictions:
        return {}

    # Sort predictions by created_at to ensure chronological order
    sorted_predictions = sorted(predictions, key=lambda x: x["created_at"])

    if group_by == "all":
        # All predictions together
        groups = {"all_time": sorted_predictions}
    elif group_by == "monthly":
        # Group by month
        groups = {}
        for pred in sorted_predictions:
            month_key = pred["created_at"].strftime("%Y-%m")
            if month_key not in groups:
                groups[month_key] = []
            groups[month_key].append(pred)
    elif group_by == "weekly":
        # Group by week
        groups = {}
        for pred in sorted_predictions:
            week_key = pred["created_at"].strftime("%Y-W%W")
            if week_key not in groups:
                groups[week_key] = []
            groups[week_key].append(pred)
    else:
        groups = {"all_time": sorted_predictions}

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


def get_chart_data(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prepare all chart data in one call.
    All data is returned in chronological order (ascending).
    """
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

    # Ensure predictions are in ascending order
    sorted_predictions = sorted(predictions, key=lambda x: x["created_at"])
    
    timeline = format_predictions_for_timeline(sorted_predictions)
    distribution = calculate_risk_distribution(sorted_predictions)
    metrics = calculate_health_metrics_average(sorted_predictions, "all")

    return {
        "timeline": timeline,
        "risk_distribution": distribution,
        "health_metrics": metrics,
        "summary": {
            "total_tests": len(sorted_predictions),
            "positive_count": distribution["positive"],
            "negative_count": distribution["negative"],
            "positive_percentage": distribution["positive_percentage"],
            "negative_percentage": distribution["negative_percentage"]
        }
    }


def format_for_json(data: Any) -> Any:
    """Convert datetime objects to ISO format for JSON serialization"""
    if isinstance(data, dict):
        return {key: format_for_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [format_for_json(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data
