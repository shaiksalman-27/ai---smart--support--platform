from app.env import SupportOpsEnv
from app.graders import grade_episode
from app.models import Action


def test_easy_task_runs():
    env = SupportOpsEnv()
    obs = env.reset("easy_password_reset")
    assert obs.task_id == "easy_password_reset"

    env.step(Action(action_type="classify", category="account_access"))
    env.step(Action(action_type="set_priority", priority="low"))
    env.step(Action(action_type="resolve", resolution="send_password_reset_steps"))
    env.step(Action(action_type="close"))

    assert env.current_state is not None
    result = grade_episode(env.current_state)

    assert 0.0 <= result.score <= 1.0
    assert result.score == 1.0