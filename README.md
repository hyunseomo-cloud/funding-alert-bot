# funding-alert-bot

MEXC와 Binance의 INJ 무기한 선물 펀딩비를 10분마다 비교해서, `MEXC 펀딩비 - Binance 펀딩비`가 기준치 이하가 되면 텔레그램으로 알려주는 봇. `coin-event-bot`과 같은 방식으로 GitHub Actions cron으로 동작하며 상시 서버가 필요 없다.

## 동작 방식

- 10분마다 GitHub Actions가 실행되어 MEXC(`contract.mexc.com`)와 Binance(`fapi.binance.com`) 공개 API로 INJ 펀딩비를 조회 (API 키 불필요).
- `MEXC 펀딩비(%) - Binance 펀딩비(%)` 값이 `FUNDING_DIFF_THRESHOLD_PCT`(기본 `0.01`) 이하이면 (음수 포함) 텔레그램 알림을 보내고 모니터링을 **자동 종료**한다.
- 모니터링이 종료된 뒤에는 아무것도 조회하지 않다가, 알림 받은 텔레그램 방에 `funding_monitoring_restart` 라고 메시지를 보내면 다음 실행부터 다시 10분 단위 모니터링을 시작한다.
- 상태(`active` 여부, 마지막으로 읽은 텔레그램 update_id)는 `state/state.json`에 저장되고, 매 실행마다 GitHub Actions가 자동으로 커밋/푸시한다.

## 처음 설정하는 법

### 1. 텔레그램 봇/채팅방

이미 있는 `coin-event-bot`과 같은 봇(@loganevent_bot)과 같은 채팅방을 그대로 재사용합니다. 즉 `coin-event-bot` repo secret에 있는 것과 **동일한** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` 값을 아래 2번에서 그대로 다시 입력하면 됩니다.

(만약 새 봇/채팅방을 쓰고 싶다면: [@BotFather](https://t.me/BotFather)에게 `/newbot` → 토큰 발급 → 알림 받을 방에 봇 초대 → `https://api.telegram.org/bot<TOKEN>/getUpdates` 로 아무 메시지나 보낸 뒤 `chat.id` 확인)

### 2. GitHub repo 준비

1. 이 폴더 내용을 GitHub repo(비공개 추천)로 push
2. repo → Settings → Secrets and variables → Actions → New repository secret
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. repo → Settings → Actions → General → Workflow permissions → **"Read and write permissions"** 로 설정 (state 파일 자동 커밋을 위해 필요)

### 3. 동작 확인

- Actions 탭 → "Check INJ funding rate spread" → Run workflow 로 수동 실행
- 로그에 `MEXC ... funding=... / Binance ... funding=... / diff=...` 가 찍히면 정상 동작.

## 로컬에서 테스트

```bash
pip install -r requirements.txt
set TELEGRAM_BOT_TOKEN=xxx
set TELEGRAM_CHAT_ID=xxx
python main.py
```

## 구조

```
main.py                      실행 진입점: 명령 확인 -> 펀딩비 조회 -> 조건 체크 -> 알림 -> state 저장
src/funding.py                MEXC/Binance 펀딩비 조회 (공개 API)
src/notify.py                 텔레그램 메시지 전송(sendMessage) / 수신(getUpdates)
src/telegram_commands.py      "funding_monitoring_restart" 명령 감지
src/state.py                  모니터링 on/off, 마지막 처리한 텔레그램 update_id 저장/조회 (state/state.json)
.github/workflows/check.yml   10분마다 실행되는 cron
```

## 설정값 바꾸기

- 대상 심볼: repo secret이 아닌 workflow env 또는 실행 환경에 `MEXC_SYMBOL`(기본 `INJ_USDT`), `BINANCE_SYMBOL`(기본 `INJUSDT`) 지정
- 알림 기준(%): `FUNDING_DIFF_THRESHOLD_PCT` (기본 `0.01`, 즉 0.01%p)
- 체크 주기: `.github/workflows/check.yml` 의 `cron: "*/10 * * * *"` 수정
- 재시작 명령어 문구: `src/telegram_commands.py` 의 `RESTART_COMMAND`
