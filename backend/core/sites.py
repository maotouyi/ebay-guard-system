# backend/core/sites.py
# eBay 多国站点配置表（2026 版，已覆盖主要高用户国家）
from enum import Enum
from typing import Dict

class EbaySite(str, Enum):
    US = "US"   # 美国
    UK = "UK"   # 英国
    DE = "DE"   # 德国
    FR = "FR"   # 法国
    CA = "CA"   # 加拿大
    AU = "AU"   # 澳大利亚
    IT = "IT"   # 意大利
    ES = "ES"   # 西班牙
    NL = "NL"   # 荷兰
    AT = "AT"   # 奥地利
    CH = "CH"   # 瑞士
    IE = "IE"   # 爱尔兰
    MX = "MX"   # 墨西哥
    IN = "IN"   # 印度
    HK = "HK"   # 香港
    BE = "BE"   # 比利时
    KR = "KR"  # 韩国
    JP = "JP"  # 日本
    RU = "RU"  # 俄罗斯

EBAY_SITES: Dict[str, Dict] = {
    "US": {
        "domain": "www.ebay.com",
        "cookie_key": "dp1",
        "example": "90001 (Zip Code)",
        "currency": "USD",
        "lang": "en-US",
    },
    "UK": {
        "domain": "www.ebay.co.uk",
        "cookie_key": "dp1",
        "example": "SW1A 1AA (Postcode)",
        "currency": "GBP",
        "lang": "en-GB",
    },
    "DE": {
        "domain": "www.ebay.de",
        "cookie_key": "dp1",
        "example": "10115 (PLZ)",
        "currency": "EUR",
        "lang": "de-DE",
    },
    "FR": {
        "domain": "www.ebay.fr",
        "cookie_key": "dp1",
        "example": "75001 (Code postal)",
        "currency": "EUR",
        "lang": "fr-FR",
    },
    "CA": {
        "domain": "www.ebay.ca",
        "cookie_key": "dp1",
        "example": "M5V 2T6 (Postal Code)",
        "currency": "CAD",
        "lang": "en-CA",
    },
    "AU": {
        "domain": "www.ebay.com.au",
        "cookie_key": "dp1",
        "example": "2000 (Postcode)",
        "currency": "AUD",
        "lang": "en-AU",
    },
    "IT": {
        "domain": "www.ebay.it",
        "cookie_key": "dp1",
        "example": "00100 (CAP)",
        "currency": "EUR",
        "lang": "it-IT",
    },
    "ES": {
        "domain": "www.ebay.es",
        "cookie_key": "dp1",
        "example": "28001 (Código postal)",
        "currency": "EUR",
        "lang": "es-ES",
    },
    "NL": {
        "domain": "www.ebay.nl",
        "cookie_key": "dp1",
        "example": "1011 (Postcode)",
        "currency": "EUR",
        "lang": "nl-NL",
    },
    "AT": {
        "domain": "www.ebay.at",
        "cookie_key": "dp1",
        "example": "1010 (PLZ)",
        "currency": "EUR",
        "lang": "de-AT",
    },
    "CH": {
        "domain": "www.ebay.ch",
        "cookie_key": "dp1",
        "example": "8001 (PLZ)",
        "currency": "CHF",
        "lang": "de-CH",
    },
    "IE": {
        "domain": "www.ebay.ie",
        "cookie_key": "dp1",
        "example": "D01 (Eircode)",
        "currency": "EUR",
        "lang": "en-IE",
    },
    "MX": {
        "domain": "www.ebay.com.mx",
        "cookie_key": "dp1",
        "example": "01000 (Código postal)",
        "currency": "MXN",
        "lang": "es-MX",
    },
    "IN": {
        "domain": "www.ebay.in",
        "cookie_key": "dp1",
        "example": "110001 (Pin Code)",
        "currency": "INR",
        "lang": "en-IN",
    },
    "HK": {
        "domain": "www.ebay.com.hk",
        "cookie_key": "dp1",
        "example": "999077 (Postal Code)",
        "currency": "HKD",
        "lang": "zh-HK",
    },
    "BE": {
        "domain": "www.ebay.be",
        "cookie_key": "dp1",
        "example": "1000 (Code postal)",
        "currency": "EUR",
        "lang": "fr-BE",
    },
    "KR": {
        "domain": "www.ebay.co.kr",
        "cookie_key": "dp1",
        "example": "06000 (우편번호)",
        "currency": "KRW",
        "lang": "ko-KR",
    },
    "JP": {
        "domain": "www.ebay.co.jp",
        "cookie_key": "dp1",
        "example": "100-0001 (郵便番号)",
        "currency": "JPY",
        "lang": "ja-JP",
    },
    "RU": {
        "domain": "www.ebay.ru",
        "cookie_key": "dp1",
        "example": "101000 (Индекс)",
        "currency": "RUB",
        "lang": "ru-RU",
    },
}

def get_site_config(site: str):
    """获取站点配置（不存在则返回 US）"""
    config = EBAY_SITES.get(site.upper())
    if not config:
        print(f"[⚠️] 未知站点 {site}，降级使用 US 配置")
        return EBAY_SITES["US"]
    return config