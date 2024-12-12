# app/helpers.py

def fetch_feedback(conn, message_ids):
    feedback_data = []
    for message_id in message_ids:
        feedback = conn.execute(
            "SELECT * FROM Feedback WHERE message_id = ?", (message_id,)
        ).fetchall()
        for fb in feedback:
            feedback_data.append({
                "feedback_id": fb["feedback_id"],
                "message_id": fb["message_id"],
                "feedback_type": fb["feedback_type"],
                "feedback_content": fb["feedback_content"]
            })
    return feedback_data

def fetch_model_comparisons(conn, message_ids):
    model_comparisons = []
    for message_id in message_ids:
        comparisons = conn.execute(
            "SELECT * FROM ModelComparisons WHERE message_id = ?", (message_id,)
        ).fetchall()
        for comp in comparisons:
            model_comparisons.append({
                "comparison_id": comp["comparison_id"],
                "message_id": comp["message_id"],
                "model_name": comp["model_name"],
                "response_time": comp["response_time"],
                "comparison_data": comp["comparison_data"]
            })
    return model_comparisons
