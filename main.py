import os
import sys
import traceback

from src.funding import get_binance_funding_rate_pct, get_mexc_funding_rate_pct
from src.notify import send_telegram_message
from src.state import load_state, save_state
from src.telegram_commands import RESTART_COMMAND, check_restart_command

MEXC_SYMBOL = os.environ.get("MEXC_SYMBOL", "INJ_USDT")
BINANCE_SYMBOL = os.environ.get("BINANCE_SYMBOL", "INJUSDT")
THRESHOLD_PCT = float(os.environ.get("FUNDING_DIFF_THRESHOLD_PCT", "0.01"))


def main() -> int:
    state = load_state()

    try:
        if check_restart_command(state):
            state["active"] = True
            print(f'"{RESTART_COMMAND}" 명령 수신 -> 모니터링 재시작.')
    except Exception:
        print("텔레그램 명령 확인 실패 (non-fatal):", file=sys.stderr)
        traceback.print_exc()

    if not state.get("active", True):
        save_state(state)
        print("모니터링이 중지된 상태입니다. (재시작하려면 텔레그램으로 "
              f'"{RESTART_COMMAND}" 전송)')
        return 0

    try:
        mexc_pct = get_mexc_funding_rate_pct(MEXC_SYMBOL)
        binance_pct = get_binance_funding_rate_pct(BINANCE_SYMBOL)
    except Exception:
        save_state(state)
        print("펀딩비 조회 실패:", file=sys.stderr)
        traceback.print_exc()
        return 1

    diff_pct = mexc_pct - binance_pct
    print(
        f"MEXC {MEXC_SYMBOL} funding={mexc_pct:.4f}% / "
        f"Binance {BINANCE_SYMBOL} funding={binance_pct:.4f}% / diff={diff_pct:.4f}%"
    )

    if diff_pct <= THRESHOLD_PCT:
        try:
            send_telegram_message(
                "🔔 <b>INJ 펀딩비 조건 충족</b>\n"
                f"MEXC 펀딩비: {mexc_pct:.4f}%\n"
                f"Binance 펀딩비: {binance_pct:.4f}%\n"
                f"차이(MEXC-Binance): {diff_pct:.4f}% (기준: {THRESHOLD_PCT:.4f}% 이하)\n\n"
                f'모니터링을 종료합니다. 다시 시작하려면 이 방에 "{RESTART_COMMAND}" 를 보내세요.'
            )
        except Exception:
            save_state(state)
            print("텔레그램 알림 전송 실패:", file=sys.stderr)
            traceback.print_exc()
            return 1
        state["active"] = False
        print("조건 충족 -> 알림 전송 후 모니터링 종료.")

    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
