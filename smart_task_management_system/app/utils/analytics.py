import numpy as np
import pandas as pd


def compute_task_analytics(tasks):
    """
    Compute analytics for a list of task dictionaries using Pandas and NumPy.

    Expected input shape for each task:
    {
        "id": int,
        "title": str,
        "description": str,
        "priority": str,
        "status": str,
        "created_date": str,
        "user_id": int
    }
    """
    df = pd.DataFrame(tasks)
    if df.empty:
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_percentage": 0.0,
        }

    # Keep status operations explicit and robust against missing values.
    df["status"] = df["status"].fillna("Pending").astype(str)

    total_tasks = int(df.shape[0])
    completed_tasks = int((df["status"] == "Completed").sum())
    pending_tasks = int((df["status"] != "Completed").sum())

    completion_percentage = float(
        np.round(np.divide(completed_tasks, total_tasks) * 100, 2)
    )

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_percentage": completion_percentage,
    }
