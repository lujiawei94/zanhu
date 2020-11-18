from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from zanhu.messager.consumers import MessagesConsumer
from channels.auth import AuthMiddlewareStack  # 中间件认证
# 直接读取到django 中setttings里allowhost允许的访问源站 或者引入OriginValidator（需要手动添加允许访问的源站）【防止websocket csrf攻击】
from channels.security.websocket import AllowedHostsOriginValidator

# 可通过self.scope['type'] 获取协议类型

# channels routing是scope级别的，一个连接只能由一个consumer接收处理
application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path('wa/<str:username>/', MessagesConsumer),
                # 可以通过self.scope['url_route']['kwargs']['username'] 获取url中的关键字参数
            ])
        )
    ),
  # 'http': views相关,  # 普通http协议默认会加载
})


# AuthMiddlewareStack 用于WebSocket认证，继承了CookieMiddleware, SessionMiddleware, AuthMidleware 兼容django认证系统
