import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationsConsumer(AsyncWebsocketConsumer):
    """处理通知应用中的websocket请求"""

    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add('notifications', self.channel_name)
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """后端views层将消息发给consumer receive接收, 然后再发给前端（websocket只可能由后端发给前端）"""
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        await self.channel_layer.group_discard('notifications', self.channel_name)
