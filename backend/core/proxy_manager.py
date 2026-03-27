# backend/core/proxy_manager.py
# Decodo 专用代理管理器 - 已支持全部 19 个国家
from typing import Dict, Optional
import random
import os
from datetime import datetime, timedelta

class ProxyManager:
    """Decodo 智能代理管理器（支持 Rotating + Sticky）"""

    # Decodo base proxy（你在 dashboard 生成的「轮换」代理）
    PROXY_BASE: Dict[str, list] = {
        "US": os.getenv("PROXY_BASE_US", "").split(",") if os.getenv("PROXY_BASE_US") else [],
        "UK": os.getenv("PROXY_BASE_UK", "").split(",") if os.getenv("PROXY_BASE_UK") else [],
        "DE": os.getenv("PROXY_BASE_DE", "").split(",") if os.getenv("PROXY_BASE_DE") else [],
        "FR": os.getenv("PROXY_BASE_FR", "").split(",") if os.getenv("PROXY_BASE_FR") else [],
        "CA": os.getenv("PROXY_BASE_CA", "").split(",") if os.getenv("PROXY_BASE_CA") else [],
        "AU": os.getenv("PROXY_BASE_AU", "").split(",") if os.getenv("PROXY_BASE_AU") else [],
        "IT": os.getenv("PROXY_BASE_IT", "").split(",") if os.getenv("PROXY_BASE_IT") else [],
        "ES": os.getenv("PROXY_BASE_ES", "").split(",") if os.getenv("PROXY_BASE_ES") else [],
        "NL": os.getenv("PROXY_BASE_NL", "").split(",") if os.getenv("PROXY_BASE_NL") else [],
        "AT": os.getenv("PROXY_BASE_AT", "").split(",") if os.getenv("PROXY_BASE_AT") else [],
        "CH": os.getenv("PROXY_BASE_CH", "").split(",") if os.getenv("PROXY_BASE_CH") else [],
        "IE": os.getenv("PROXY_BASE_IE", "").split(",") if os.getenv("PROXY_BASE_IE") else [],
        "MX": os.getenv("PROXY_BASE_MX", "").split(",") if os.getenv("PROXY_BASE_MX") else [],
        "IN": os.getenv("PROXY_BASE_IN", "").split(",") if os.getenv("PROXY_BASE_IN") else [],
        "HK": os.getenv("PROXY_BASE_HK", "").split(",") if os.getenv("PROXY_BASE_HK") else [],
        "BE": os.getenv("PROXY_BASE_BE", "").split(",") if os.getenv("PROXY_BASE_BE") else [],
        "KR": os.getenv("PROXY_BASE_KR", "").split(",") if os.getenv("PROXY_BASE_KR") else [],
        "JP": os.getenv("PROXY_BASE_JP", "").split(",") if os.getenv("PROXY_BASE_JP") else [],
        "RU": os.getenv("PROXY_BASE_RU", "").split(",") if os.getenv("PROXY_BASE_RU") else [],
    }

    _sticky_cache: Dict[int, dict] = {}

    @staticmethod
    def _get_base_proxy(ebay_site: str) -> Optional[str]:
        site = ebay_site.upper()
        proxies = ProxyManager.PROXY_BASE.get(site, [])
        if not proxies or not proxies[0].strip():
            print(f"[⚠️] 未配置 {site} proxy，使用直连（建议尽快添加 Decodo 住宅代理）")
            return None
        return random.choice([p.strip() for p in proxies if p.strip()])

    @staticmethod
    def _make_sticky_proxy(base_proxy: str, task_id: int, sticky_minutes: int = 30) -> str:
        if not base_proxy or "://" not in base_proxy:
            return base_proxy

        now = datetime.utcnow()
        ProxyManager._sticky_cache = {tid: data for tid, data in ProxyManager._sticky_cache.items() if data["expire"] > now}

        if task_id in ProxyManager._sticky_cache:
            session_id = ProxyManager._sticky_cache[task_id]["session_id"]
        else:
            session_id = f"task{task_id}_{int(now.timestamp())}"
            ProxyManager._sticky_cache[task_id] = {"session_id": session_id, "expire": now + timedelta(minutes=sticky_minutes)}

        if "@" in base_proxy:
            protocol, rest = base_proxy.split("://", 1)
            auth, host = rest.split("@", 1)
            user_pass = auth.split(":", 1)
            if len(user_pass) == 2:
                user, pwd = user_pass
                new_user = f"{user}-session-{session_id}"
                new_proxy = f"{protocol}://{new_user}:{pwd}@{host}"
                print(f"[🔒] Sticky Session 已启用 → Task {task_id} | Session: {session_id[:12]}... | 持续 {sticky_minutes} 分钟")
                return new_proxy
        return base_proxy

    @staticmethod
    def get_proxy(
        ebay_site: str,
        monitor_type: str = "rank",
        task_id: Optional[int] = None,
        sticky_minutes: int = 30
    ) -> Optional[str]:
        base = ProxyManager._get_base_proxy(ebay_site)
        if not base:
            return None

        if monitor_type.lower() in ["price", "pricedefense", "price_defense"]:
            if task_id is None:
                print("[⚠️] 价格防卫任务必须传入 task_id")
                return base
            return ProxyManager._make_sticky_proxy(base, task_id, sticky_minutes)
        else:
            print(f"[🔄] Rotating 模式 → Task {task_id or 'N/A'} | 站点 {ebay_site}")
            return base

    @staticmethod
    def get_all_config():
        """调试用：查看所有已配置代理"""
        return {site: len(proxies) for site, proxies in ProxyManager.PROXY_BASE.items() if proxies and proxies[0]}