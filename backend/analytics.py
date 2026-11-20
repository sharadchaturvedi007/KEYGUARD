from database import get_connection

def get_analytics(session_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if session_id:
        cursor.execute("""
            SELECT event_category, COUNT(*)
            FROM activity_logs
            WHERE session_id = ?
            GROUP BY event_category
        """, (session_id,))
    else:
        cursor.execute("""
            SELECT event_category, COUNT(*)
            FROM activity_logs
            GROUP BY event_category
        """)

    rows = cursor.fetchall()
    conn.close()

    categories = {}

    for category, count in rows:
        categories[category] = count

    return {
        "total_events": sum(categories.values()),
        "categories": categories,
        "status": "Analytics generated"
    }