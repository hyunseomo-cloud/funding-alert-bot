import json
import os

STATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state", "state.json"
)

DEFAULT_STATE = {
    # 모니터링이 켜져 있는지. 조건 충족 알림을 1회 보내면 False로 바뀌고,
    # 텔레그램으로 "funding_monitoring_restart" 명령이 오면 다시 True로 바뀐다.
    "active": True,
    # 마지막으로 처리한 텔레그램 update_id (getUpdates 재처리 방지용)
    "last_update_id": 0,
}


def load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return dict(DEFAULT_STATE)
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)
    return {**DEFAULT_STATE, **state}


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)
