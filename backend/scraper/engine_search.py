# backend/scraper/engine_search.py
import os
from pathlib import Path
from dotenv import load_dotenv

from curl_cffi import requests
from lxml import etree
import urllib.parse
import re

from core.sites import get_site_config, EbaySite
from core.proxy_manager import ProxyManager


# ================== 智能加载 .env + 强制刷新 ProxyManager ==================
def load_env_ultimate():
    possible_paths = []
    script_dir = Path(__file__).resolve().parent
    possible_paths.append(script_dir.parent / ".env")
    possible_paths.append(script_dir.parent.parent / ".env")
    possible_paths.append(Path.cwd() / "backend" / ".env")
    possible_paths.append(Path.cwd() / ".env")

    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path, override=True)
            print(f"[✅] .env 加载成功 → {env_path}")
            print(f"[DEBUG] PROXY_BASE_US = {os.getenv('PROXY_BASE_US', '【空】')[:120]}...")
            return
    print("[❌] 找不到 .env 文件！")


load_env_ultimate()

# 强制刷新 ProxyManager 的代理池（解决 class 属性冻结问题）
ProxyManager.PROXY_BASE["US"] = os.getenv("PROXY_BASE_US", "").split(",") if os.getenv("PROXY_BASE_US") else []


def fetch_ebay_search_rank(
        keyword: str,
        target_item_id: str = None,
        page: int = 1,
        ebay_site: str = EbaySite.US.value,
        location_code: str = "90001",
        monitor_type: str = "rank",
        task_id: int = None
):
    site_config = get_site_config(ebay_site)

    proxy_url = ProxyManager.get_proxy(
        ebay_site=ebay_site,
        monitor_type=monitor_type,
        task_id=task_id,
        sticky_minutes=30
    )

    print(
        f"[*] 🚀 启动 [{monitor_type.upper()} 监控]：关键词 [{keyword}] | 站点 [{ebay_site}] | 位置 [{location_code}] | 代理 [{proxy_url[:80] + '...' if proxy_url else '直连'}]")

    local_cookies = {
        site_config["cookie_key"]: f"bpbf/%23{location_code}^pz/{location_code}^"
    }

    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

    session = requests.Session(
        impersonate="chrome120",  # ← 改回稳定版本（chrome124 会触发 curl 23）
        proxies=proxies,
        cookies=local_cookies
    )

    session.headers.update({
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": f"https://{site_config['domain']}/",
        "Sec-Ch-Ua": '"Chromium";v="120", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    try:
        # ================== Warmup（加 try 保护，不会再炸）==================
        print("[*] 执行 Warmup（强制 US session）...")
        try:
            warmup_url = f"https://{site_config['domain']}/"
            session.get(warmup_url, timeout=15, allow_redirects=True)
            print("[+] Warmup 成功")
        except Exception as w:
            print(f"[⚠️] Warmup 失败（不影响搜索）：{w}")

        # ================== 正式搜索（强制 US 结果）==================
        params = {
            "_nkw": keyword,
            "_pgn": page,
            "_sop": "12",  # Best Match
            "LH_BIN": "1",
            "rt": "nc",
            "LH_PrefLoc": "1",  # 强制美国本地优先
            "_blrs": "1"  # 额外反降级参数
        }
        base_url = f"https://{site_config['domain']}/sch/i.html"
        url = f"{base_url}?{urllib.parse.urlencode(params)}"

        response = session.get(url, timeout=40, allow_redirects=True)

        print(f"[+] 响应状态码: {response.status_code} | 最终 URL: {response.url}")

        if response.status_code != 200:
            print(f"[-] ❌ 请求失败：HTTP {response.status_code}")
            return None

        tree = etree.HTML(response.text)
        items = tree.xpath('//li[contains(@class, "s-item") or contains(@class, "s-card")]')

        all_items = []
        my_item_rank = -1

        for idx, item in enumerate(items, 1):
            title_text = " ".join(item.xpath('.//*[contains(@class,"s-item__title")]//text()'))
            if "sponsored" in title_text.lower() or "Shop on eBay" in title_text:
                continue

            link_list = item.xpath('.//a[contains(@class,"s-item__link") or contains(@class,"s-card__link")]/@href')
            link = link_list[0].split("?")[0] if link_list else ""

            item_id = ""
            if link:
                id_match = re.search(r'/(\d{12,13})(?:/|\?|$)', link)
                item_id = id_match.group(1) if id_match else ""

            if not item_id:
                continue

            price = " ".join(item.xpath(
                './/*[contains(@class,"s-item__price") or contains(@class,"s-card__price")]//text()')).strip()

            if target_item_id and item_id == target_item_id:
                my_item_rank = idx

            all_items.append({"rank": idx, "item_id": item_id, "price": price, "title": title_text})

        print(f"[+] 📊 提取完毕，有效商品 {len(all_items)} 个 | 目标排名: {my_item_rank}")
        return {
            "target_rank": my_item_rank,
            "competitors": all_items,
            "site": ebay_site,
            "location_code": location_code,
            "proxy_used": proxy_url[:80] + "..." if proxy_url else "直连",
        }

    except Exception as e:
        print(f"[-] 💥 致命异常: {e}")
        return None


if __name__ == "__main__":
    data = fetch_ebay_search_rank(
        keyword="iPhone 15 Pro",
        target_item_id="146550002738",  # 改成你自己的 Item ID
        ebay_site="US",
        location_code="90001",
        monitor_type="rank",
        task_id=999
    )
    if data:
        print(f"\n✅ 测试完成！代理状态: {data.get('proxy_used', '未知')}")