from app.models import GraderResult, TicketState


def grade_episode(state: TicketState) -> GraderResult:
    details = {
        "category_correct": 0.0,
        "priority_correct": 0.0,
        "info_request_correct": 0.0,
        "resolution_or_escalation_correct": 0.0,
        "safe_completion": 0.0,
    }

    if state.classified_category == state.true_category:
        details["category_correct"] = 0.2

    if state.assigned_priority == state.true_priority:
        details["priority_correct"] = 0.2

    if state.required_info_request:
        required = set(state.required_missing_fields or [])
        asked = set(state.asked_info_fields or [])

        if required and required.issubset(asked):
            details["info_request_correct"] = 0.2
        elif asked:
            details["info_request_correct"] = 0.1
    else:
        details["info_request_correct"] = 0.2

    if state.expected_resolution:
        if state.resolution_given == state.expected_resolution:
            details["resolution_or_escalation_correct"] = 0.2
    elif state.expected_escalation_team:
        if state.escalated_to == state.expected_escalation_team:
            details["resolution_or_escalation_correct"] = 0.2

    safe_completion = False

    if state.expected_resolution:
        if state.resolution_given == state.expected_resolution and state.closed:
            safe_completion = True

    elif state.expected_escalation_team:
        required_info_ok = True
        if state.required_info_request:
            required_info_ok = set(state.required_missing_fields or []).issubset(
                set(state.asked_info_fields or [])
            )

        if state.escalated_to == state.expected_escalation_team and state.closed and required_info_ok:
            safe_completion = True

    else:
        if state.closed and not state.unsafe_to_close_early:
            safe_completion = True

    if safe_completion:
        details["safe_completion"] = 0.2

    raw_score = round(sum(details.values()), 3)

    if raw_score <= 0.0:
        total_score = 0.1
    elif raw_score >= 1.0:
        total_score = 0.9
    else:
        total_score = raw_score

    return GraderResult(
        task_id=state.task_id,
        score=total_score,
        details=details,
    )