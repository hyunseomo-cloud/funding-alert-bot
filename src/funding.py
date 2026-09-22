import requests

MEXC_URL = "https://contract.mexc.com/api/v1/contract/funding_rate/{symbol}"

# fapi.binance.com은 GitHub Actions(미국 Azure 리전) IP를 지역 제한(451)으로 막는 경우가
# 있어서, 같은 데이터를 제공하는 www.binance.com 미러를 폴백으로 둔다.
BINANCE_URLS = [
    "https://fapi.binance.com/fapi/v1/premiumIndex",
    "https://www.binance.com/fapi/v1/premiumIndex",
]


def get_mexc_funding_rate_pct(symbol: str) -> float:
    """MEXC 선물(contract.mexc.com) 현재 펀딩비를 %로 반환. 공개 API, 키 불필요."""
    resp = requests.get(MEXC_URL.format(symbol=symbol), timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"MEXC funding rate API error: {data}")
    return float(data["data"]["fundingRate"]) * 100


def get_binance_funding_rate_pct(symbol: str) -> float:
    """Binance USDT-M 선물 다음 정산 예정 펀딩비를 %로 반환. 공개 API, 키 불필요."""
    last_error: Exception = RuntimeError("no Binance URL configured")
    for url in BINANCE_URLS:
        try:
            resp = requests.get(url, params={"symbol": symbol}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return float(data["lastFundingRate"]) * 100
        except Exception as exc:  # try next mirror on any failure (HTTP error, timeout, etc.)
            last_error = exc
            continue
    raise last_error
