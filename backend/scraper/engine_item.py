# backend/scraper/engine_item.py
import re
import json
import os
import time
import random
from curl_cffi import requests
from core.config import settings

def fetch_item_details(
    item_id: str,
    proxy_url: str = None,
    target_zipcode: str = None
) -> dict:
    """
    eBay单个Item完整抓取引擎（V1.5优化版）
    支持：价格防卫线、下架检测、Best Offer、库存
    特征：Chrome120指纹 + ZipCode强注入 + 随机delay + 多层解析兜底
    """
    if target_zipcode is None:
        target_zipcode = settings.TARGET_ZIPCODE

    print(f"[*] 🎯 锁定目标: Item {item_id} | 注入邮编: {target_zipcode}")

    # ZipCode注入Cookie（eBay核心本地化方式）
    local_cookies = {
        "dp1": f"bpbf/%23{target_zipcode}^pz/{target_zipcode}^"
    }
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

    session = requests.Session(
        impersonate="chrome120",
        proxies=proxies,
        cookies=local_cookies
    )

    session.headers.update({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    url = f"https://www.ebay.com/itm/{item_id}"

    try:
        # 随机delay防风控（1-3秒）
        time.sleep(random.uniform(1.0, 3.0))

        response = session.get(url, timeout=25, allow_redirects=True)
        html = response.text

        # 风控拦截检测
        if "Pardon Our Interruption" in html or "captcha" in html.lower() or response.status_code in (403, 429):
            print("[-] 🛑 致命拦截：Akamai / Cloudflare 风控！建议换代理或等待5-10分钟")
            return None

        if response.status_code == 404:
            print(f"[-] 🚨 警报：Item {item_id} 已下架或不存在！")
            return {"status": "offline", "item_id": item_id}

        # ================== 初始化数据 ==================
        item_data = {
            "status": "online",
            "item_id": item_id,
            "title": "Unknown",
            "price": 0.0,
            "currency": "USD",
            "seller": "Unknown",
            "in_stock": True,
            "available_qty": 0,
            "image": "",
            "url": url,
            "extraction_method": "Unknown",
            "best_offer": False
        }

        # 第一层：JSON-LD（最可靠）
        json_blocks = re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
        for block in json_blocks:
            try:
                data = json.loads(block.strip())
                target = None
                if isinstance(data, dict):
                    if data.get("@type") in ["Product", "ProductGroup"]:
                        target = data
                    elif "@graph" in data:
                        for item in data["@graph"]:
                            if item.get("@type") in ["Product", "ProductGroup"]:
                                target = item
                                break
                if target:
                    item_data["title"] = target.get("name", item_data["title"])
                    item_data["image"] = target.get("image", item_data["image"]) or ""
                    offers = target.get("offers", {})
                    if isinstance(offers, dict):
                        item_data["price"] = float(offers.get("price", 0))
                        item_data["currency"] = offers.get("priceCurrency", "USD")
                        item_data["seller"] = offers.get("seller", {}).get("name", "Unknown")
                    elif isinstance(offers, list) and offers:
                        item_data["price"] = float(offers[0].get("price", 0))
                        item_data["currency"] = offers[0].get("priceCurrency", "USD")
                    item_data["extraction_method"] = "Layer 1 (LD+JSON)"
                    break
            except:
                continue

        # 第二层：Meta标签兜底
        if item_data["price"] == 0.0 or item_data["title"] == "Unknown":
            title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
            if title_match:
                item_data["title"] = title_match.group(1).replace(" | eBay", "").strip()

            img_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)
            if img_match:
                item_data["image"] = img_match.group(1)

            price_match = re.search(r'itemprop="price"\s+content="([\d\.]+)"', html)
            if price_match:
                item_data["price"] = float(price_match.group(1))

            if item_data["price"] > 0:
                item_data["extraction_method"] = "Layer 2 (Meta Tags)"

        # 第三层：旧class暴力抓取
        if item_data["price"] == 0.0:
            raw_price_match = re.search(r'class="x-price-primary"[^>]*>\$?([\d,\.]+)</', html)
            if raw_price_match:
                item_data["price"] = float(raw_price_match.group(1).replace(',', ''))
                item_data["extraction_method"] = "Layer 3 (Old x-price-primary)"

        # 第四层：2026纯文本终极兜底（最稳）
        if item_data["price"] == 0.0:
            price_match = re.search(r'US \$?([\d,]+\.?\d*)', html)
            if not price_match:
                price_match = re.search(r'\$([\d,]+\.?\d*)', html)
            if price_match:
                clean_price = price_match.group(1).replace(',', '')
                item_data["price"] = float(clean_price)
                item_data["currency"] = "USD"
                item_data["extraction_method"] = "Layer 4 (Plain Text - 2026 最稳)"

                if "Best Offer" in html or "best offer" in html.lower():
                    item_data["best_offer"] = True

        # 标题最终兜底
        if item_data["title"] == "Unknown":
            title_match = re.search(r'<title>(.+?)\s*\|\s*eBay', html)
            if title_match:
                item_data["title"] = title_match.group(1).strip()

        # 图片最终兜底
        if not item_data["image"]:
            img_match = re.search(r'(https?://i\.ebayimg\.com/[^"\']+\.(?:jpg|png|webp))', html, re.IGNORECASE)
            if img_match:
                item_data["image"] = img_match.group(1)

        # 卖家 & 库存
        seller_match = re.search(r'seller(?:\s*[:|])\s*([^<"\n]+)', html, re.IGNORECASE)
        if seller_match:
            item_data["seller"] = seller_match.group(1).strip()

        if re.search(r'(out of stock|sold out|0 available)', html, re.IGNORECASE):
            item_data["in_stock"] = False
        else:
            qty_match = re.search(r'(\d+)\s+available', html, re.IGNORECASE)
            if qty_match:
                item_data["available_qty"] = int(qty_match.group(1))
                item_data["in_stock"] = item_data["available_qty"] > 0

        # ================== 最终校验 & Debug ==================
        if item_data["price"] == 0.0:
            print(f"[-] ⚠️ 四层解析全部击穿！已保存 debug_html_{item_id}.html 请检查")
            debug_path = f"debug_html_{item_id}.html"
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(html[:50000])  # 避免文件过大
            return {"status": "parse_failed", "item_id": item_id, "debug_file": debug_path}

        print(f"[+] ✅ 抓取成功 | {item_data['extraction_method']} | 价格: ${item_data['price']}")
        return item_data

    except Exception as e:
        print(f"[-] ❌ fetch_item_details 异常: {e}")
        return None