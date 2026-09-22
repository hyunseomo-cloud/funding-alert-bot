import requests

MEXC_URL = "https://contract.mexc.com/api/v1/contract/funding_rate/{symbol}"
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"


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
    resp = requests.get(BINANCE_URL, params={"symbol": symbol}, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return float(data["lastFundingRate"]) * 100
