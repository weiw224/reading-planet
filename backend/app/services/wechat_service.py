import httpx
from typing import Optional
from app.config import settings


class WechatService:
    AUTH_URL = "https://api.weixin.qq.com/sns/jscode2session"
    
    @classmethod
    async def code2session(cls, code: str) -> Optional[dict]:
        params = {
            "appid": settings.WECHAT_APP_ID,
            "secret": settings.WECHAT_APP_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(cls.AUTH_URL, params=params, timeout=10.0)
            data = response.json()
        
        if "openid" in data:
            return {
                "openid": data["openid"],
                "session_key": data.get("session_key", "")
            }
        
        print(f"微信登录失败: {data}")
        return None


wechat_service = WechatService()
