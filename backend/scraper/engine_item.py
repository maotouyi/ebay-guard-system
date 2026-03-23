import re
import json
import os
from curl_cffi import requests
from core.config import settings


def fetch_item_details(item_id: str, proxy_url: str = None, target_zipcode: str = "90001"):
    print(f"[*] 🎯 锁定目标: Item {item_id} | 注入邮编: {target_zipcode}")

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
        response = session.get(url, timeout=25, allow_redirects=True)
        html = response.text

        # 拦截检测
        if "Pardon Our Interruption" in html or "captcha" in html.lower() or response.status_code in (403, 429):
            print("[-] 🛑 致命拦截：Akamai / Cloudflare 风控！建议换代理或等 5-10 分钟")
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

        # ================== 第一层：旧 JSON-LD（保留兼容） ==================
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

        # ================== 第二层：Meta 标签兜底 ==================
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

        # ================== 第三层：旧 class 暴力抓取 ==================
        if item_data["price"] == 0.0:
            raw_price_match = re.search(r'class="x-price-primary"[^>]*>\$?([\d,\.]+)</', html)
            if raw_price_match:
                item_data["price"] = float(raw_price_match.group(1).replace(',', ''))
                item_data["extraction_method"] = "Layer 3 (Old x-price-primary)"

        # ================== 第四层：2026 新结构纯文本终极兜底（最关键！） ==================
        if item_data["price"] == 0.0:
            # 优先匹配 "US $99.99/ea or Best Offer"
            price_match = re.search(r'US \$?([\d,]+\.?\d*)', html)
            if not price_match:
                price_match = re.search(r'\$([\d,]+\.?\d*)', html)  # 纯 $ 兜底

            if price_match:
                clean_price = price_match.group(1).replace(',', '')
                item_data["price"] = float(clean_price)
                item_data["currency"] = "USD"
                item_data["extraction_method"] = "Layer 4 (Plain Text - 2026 最稳)"

                # 是否支持 Best Offer
                if "Best Offer" in html or "best offer" in html.lower():
                    item_data["best_offer"] = True

        # ================== 标题最终兜底 ==================
        if item_data["title"] == "Unknown":
            title_match = re.search(r'<title>(.+?)\s*\|\s*eBay', html)
            if title_match:
                item_data["title"] = title_match.group(1).strip()

        # ================== 图片最终兜底（大图优先） ==================
        if not item_data["image"]:
            img_match = re.search(r'(https?://i\.ebayimg\.com/[^"\']+\.(?:jpg|png|webp))', html, re.IGNORECASE)
            if img_match:
                item_data["image"] = img_match.group(1)

        # ================== 卖家 & 库存提取 ==================
        seller_match = re.search(r'seller(?:\s*[:|])\s*([^<"\n]+)', html, re.IGNORECASE)
        if seller_match:
            item_data["seller"] = seller_match.group(1).strip()

        # 库存判断
        if re.search(r'(out of stock|sold out|0 available)', html, re.IGNORECASE):
            item_data["in_stock"] = False
        else:
            qty_match = re.search(r'(\d+)\s+available', html, re.IGNORECASE)
            if qty_match:
                item_data["available_qty"] = int(qty_match.group(1))
                item_data["in_stock"] = item_data["available_qty"] > 0

        # ================== 最终校验 ==================
        if item_data["price"] == 0.0:
            print(f"[-] ⚠️ 四层装甲全部击穿！保存 debug_html_{item_id}.html")
            with open(f"debug_html_{item_id}.html", "w", encoding="utf-8") as f:
                f.write(html)
            return None

        print(f"[+] ✅ 成功捕获! [{item_data['extraction_method']}] "
              f"价格: {item_data['price']} {item_data['currency']} | "
              f"库存: {item_data['available_qty']} | "
              f"标题: {item_data['title'][:50]}...")

        return item_data

    except Exception as e:
        print(f"[-] 💥 引擎故障: {e}")
        return None


if __name__ == "__main__":
    test_item = "117044439320"
    result = fetch_item_details(
        item_id=test_item,
        proxy_url=settings.PROXY_URL,
        target_zipcode=settings.TARGET_ZIPCODE
    )

    if result:
        print("\n=== 🎯 数据解剖完毕 ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))