def analyze_activity(data):

    risk_score = 0
    indicators = []

    event_count = data.get("event_count", 0)

    # Rule 1: Unusually high event frequency
    if event_count > 100:
        risk_score += 20
        indicators.append({
            "name": "Unusual Event Frequency",
            "severity": "MEDIUM",
            "description": "High volume of simulated keyboard events detected."
        })

    # Rule 2: Background monitoring attempt
    if data.get("background_attempt") is True:
        risk_score += 35
        indicators.append({
            "name": "Background Monitoring Attempt",
            "severity": "HIGH",
            "description": "A simulated attempt to monitor activity outside the test area was flagged."
        })

    # Rule 3: Suspicious permission request
    if data.get("permission_warning") is True:
        risk_score += 25
        indicators.append({
            "name": "Suspicious Permission Request",
            "severity": "HIGH",
            "description": "A simulated application requested unnecessary monitoring permissions."
        })

    # Rule 4: Unexpected startup behaviour
    if data.get("startup_warning") is True:
        risk_score += 20
        indicators.append({
            "name": "Unexpected Startup Behaviour",
            "severity": "MEDIUM",
            "description": "Unexpected startup behaviour was simulated."
        })

    risk_score = min(risk_score, 100)

    if risk_score >= 60:
        risk_level = "HIGH"

    elif risk_score >= 30:
        risk_level = "MODERATE"

    else:
        risk_level = "LOW"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "indicators": indicators,
        "total_indicators": len(indicators),
        "assessment": "Completed"
    }