from copy import deepcopy
from typing import Any, Dict, Tuple

from app.models import Action, Observation, RewardModel, TicketState
from app.tasks import TASKS, get_task


class SupportOpsEnv:
    def __init__(self) -> None:
        self.current_state: TicketState | None = None

    def reset(self, task_id: str) -> Observation:
        if task_id not in TASKS:
            raise ValueError(f"Unknown task_id: {task_id}")

        # Use a fresh copy every time
        self.current_state = get_task(task_id)
        return self._build_observation()

    def state(self) -> Dict[str, Any]:
        if self.current_state is None:
            return {"error": "Environment not initialized. Call reset() first."}
        return self.current_state.model_dump()

    def step(self, action: Action) -> Tuple[Observation, RewardModel, bool, Dict[str, Any]]:
        if self.current_state is None:
            raise ValueError("Environment not initialized. Call reset() first.")

        state = self.current_state

        if state.done:
            reward = RewardModel(
                value=0.1,
                reason="Episode already finished.",
                progress={},
            )
            return self._build_observation(), reward, True, {"message": "done"}

        state.step_count += 1
        reward_value = 0.1
        reward_reason = "Action processed."
        progress: Dict[str, float] = {}

        action_dict = action.model_dump()
        state.history.append(action_dict)

        if action.action_type == "classify":
            if action.category == state.true_category:
                state.classified_category = action.category
                reward_value = 0.2
                progress["category"] = 0.2
                reward_reason = "Correct classification."
            else:
                reward_value = 0.1
                reward_reason = "Incorrect classification."

        elif action.action_type == "set_priority":
            if action.priority == state.true_priority:
                state.assigned_priority = action.priority
                reward_value = 0.2
                progress["priority"] = 0.2
                reward_reason = "Correct priority."
            else:
                reward_value = 0.1
                reward_reason = "Incorrect priority."

        elif action.action_type == "ask_info":
            if state.required_info_request:
                message = (action.message or "").lower()
                matched_fields = []

                for field in state.required_missing_fields:
                    simple_name = field.replace("_", " ").lower()
                    if simple_name in message or field.lower() in message:
                        matched_fields.append(field)

                if matched_fields:
                    for field in matched_fields:
                        if field not in state.asked_info_fields:
                            state.asked_info_fields.append(field)
                    reward_value = 0.2
                    progress["info_request"] = 0.2
                    reward_reason = "Useful missing information requested."
                else:
                    reward_value = 0.1
                    reward_reason = "Asked for information, but not the required information."
            else:
                reward_value = 0.1
                reward_reason = "Unnecessary information request."

        elif action.action_type == "resolve":
            if state.expected_resolution and action.resolution == state.expected_resolution:
                state.resolution_given = action.resolution
                reward_value = 0.2
                progress["resolution"] = 0.2
                reward_reason = "Correct resolution."
            else:
                reward_value = 0.1
                reward_reason = "Incorrect resolution."

        elif action.action_type == "escalate":
            if state.expected_escalation_team and action.escalation_team == state.expected_escalation_team:
                state.escalated_to = action.escalation_team
                reward_value = 0.2
                progress["escalation"] = 0.2
                reward_reason = "Correct escalation."
            else:
                reward_value = 0.1
                reward_reason = "Incorrect escalation."

        elif action.action_type == "close":
            unsafe_close = False

            if state.required_info_request:
                needed = set(state.required_missing_fields or [])
                asked = set(state.asked_info_fields or [])
                if not needed.issubset(asked):
                    unsafe_close = True

            if state.expected_escalation_team and state.escalated_to != state.expected_escalation_team:
                unsafe_close = True

            if state.expected_resolution and state.resolution_given != state.expected_resolution:
                unsafe_close = True

            if unsafe_close and state.unsafe_to_close_early:
                reward_value = 0.1
                reward_reason = "Unsafe early closure."
            else:
                state.closed = True
                state.done = True
                reward_value = 0.2
                progress["closure"] = 0.2
                reward_reason = "Ticket closed safely."

        else:
            reward_value = 0.1
            reward_reason = "Invalid action."

        if state.step_count >= state.max_steps and not state.done:
            state.done = True
            reward_reason += " Max steps reached."

        reward = RewardModel(
            value=round(reward_value, 3),
            reason=reward_reason,
            progress=progress,
        )

        return self._build_observation(), reward, state.done, {"step_count": state.step_count}

    def _build_observation(self) -> Observation:
        assert self.current_state is not None
        state = self.current_state

        known_facts = {
            "classified_category": state.classified_category,
            "assigned_priority": state.assigned_priority,
            "resolution_given": state.resolution_given,
            "escalated_to": state.escalated_to,
            "closed": state.closed,
        }

        missing_fields = []
        if state.required_info_request:
            missing_fields = [
                field for field in state.required_missing_fields
                if field not in state.asked_info_fields
            ]

        return Observation(
            task_id=state.task_id,
            difficulty=state.difficulty,
            customer_message=state.customer_message,
            current_status="done" if state.done else "in_progress",
            known_facts=known_facts,
            missing_fields=missing_fields,
            action_history=state.history,
            remaining_steps=max(0, state.max_steps - state.step_count),
            done=state.done,
        )