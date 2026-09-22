import os

from .notify import get_updates

RESTART_COMMAND = "funding_monitoring_restart"


def check_restart_command(state: dict) -> bool:
    """대기 중인 텔레그램 업데이트를 확인해서, 허용된 채팅방에서 재시작 명령이
    왔으면 True를 반환한다. state["last_update_id"]는 처리한 만큼 갱신된다."""
    allowed_chat_id = str(os.environ["TELEGRAM_CHAT_ID"])
    updates = get_updates(offset=state["last_update_id"] + 1)

    restarted = False
    for update in updates:
        state["last_update_id"] = max(state["last_update_id"], update["update_id"])
        message = update.get("message") or update.get("channel_post")
        if not message:
            continue
        chat_id = str(message.get("chat", {}).get("id", ""))
        text = (message.get("text") or "").strip()
        if chat_id == allowed_chat_id and text == RESTART_COMMAND:
            restarted = True
    return restarted
