import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MessagesConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope['user'].is_anonymous:  # 是否匿名用户
            await self.close()
        else:
            # 加入聊天组的监听频道
            await self.channel_layer.group_add(self.scope['user'].username, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.scope['user'].username, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        await self.send(text_data=json.dumps(text_data))

# form channels.db import database_sync_to_async
# user = await database_sync_to_async(User.objects.get(username=username))
