from curl_cffi import requests
from lxml import etree
import urllib.parse
import re


def fetch_ebay_search_rank(
        keyword: str,
        target_item_id: str = None,
        page: int = 1,
        proxy_url: str = None,
        target_zipcode: str = "90001"  # 默认注入美国加州邮编
):
    """
    【V1.5 引擎组件】eBay 搜索排名与竞品盘点
    底层驱动：curl_cffi (完美模拟 Chrome 120 指纹)
    核心亮点：强行注入 Zip Code，获取无痕本地化真实排名
    """
    print(f"[*] 🚀 启动 [排名监控]：关键词 [{keyword}] | 目标邮编 [{target_zipcode}]")

    # 1. 核心：构造带有 Zip Code 的本地化 Cookie
    # eBay 通过 dp1 cookie 中的 pz 参数来识别买家邮编
    local_cookies = {
        "dp1": f"bpbf/%23{target_zipcode}^pz/{target_zipcode}^"
    }

    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

    # 2. 初始化 curl_cffi 客户端 (原生级浏览器伪装)
    session = requests.Session(
        impersonate="chrome120",  # 一键完美伪装，不用再手写一大堆 headers
        proxies=proxies,
        cookies=local_cookies
    )

    # 只需要补充一点业务 Header，底层的 TLS/HTTP2 特征 curl_cffi 会自动处理
    session.headers.update({
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.ebay.com/"
    })

    try:
        params = {"_nkw": keyword, "_pgn": page}
        url = f"https://www.ebay.com/sch/i.html?{urllib.parse.urlencode(params)}"

        # 发起请求
        response = session.get(url, timeout=30, allow_redirects=False)

        if response.status_code != 200:
            print(f"[-] ❌ 请求失败或被拦截：HTTP {response.status_code}")
            return None

        # ================= 以下保留你优秀的 XPath 解析逻辑 =================
        tree = etree.HTML(response.text)
        items = tree.xpath('//li[contains(@class, "s-item") or contains(@class, "s-card")]')

        all_items = []
        my_item_rank = -1  # 记录我们自己 Item 的排名

        for idx, item in enumerate(items, 1):
            # 过滤广告 (Sponsored) - 计算真实自然排名必须跳过广告
            title_text = " ".join(item.xpath('.//*[contains(@class,"s-item__title")]//text()'))
            if "sponsored" in title_text.lower() or "Shop on eBay" in title_text:
                continue

            link_list = item.xpath('.//a[contains(@class,"s-item__link") or contains(@class,"s-card__link")]/@href')
            link = link_list[0].split("?")[0] if link_list else ""

            # 提取 ID
            item_id = ""
            if link:
                id_match = re.search(r'/(\d{12,13})(?:/|\?|$)', link)
                item_id = id_match.group(1) if id_match else ""

            if not item_id:
                continue

            price = " ".join(item.xpath(
                './/*[contains(@class,"s-item__price") or contains(@class,"s-card__price")]//text()')).strip()

            # 如果传了 target_item_id，发现匹配就记录排名
            if target_item_id and item_id == target_item_id:
                my_item_rank = idx
                print(f"[🚨 发现目标] 你的商品 {target_item_id} 目前排在第 {idx} 名！价格: {price}")

            all_items.append({
                "rank": idx,
                "item_id": item_id,
                "price": price,
                "title": title_text
            })

        print(f"[+] 📊 提取完毕，有效自然商品 {len(all_items)} 个。")
        return {
            "target_rank": my_item_rank,
            "competitors": all_items
        }

    except Exception as e:
        print(f"[-] 💥 致命异常: {e}")
        return None


if __name__ == "__main__":
    # 测试一下重构后的引擎
    # 假设你卖的是 "nike air max"，你的 Item ID 是 123456789012
    data = fetch_ebay_search_rank(
        keyword="nike air max",
        target_item_id="123456789012",
        proxy_url=None,  # 测试时先直连
        target_zipcode="90001"  # 洛杉矶
    )

    if data:
        print(f"\n[监控结果] 你的排名: {data['target_rank']}")