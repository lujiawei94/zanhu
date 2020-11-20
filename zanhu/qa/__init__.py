"""
第一步：websocket是否连接成功，请求头、响应头、状态码（101）
1.前端websocket api使用错误，未正确发送连接，常见的：连接地址写错，JS语法错误，为正确的引用reconnecting-websocket.js
2.Consumers.py 中接收websocket连接的代码错误，检查connect方法，或者routing.py中的路由

第二部：前端js能否接收到websocket消息，在chrome f12 选中ws：frames data是否有数据(需要用另一个浏览器的另一个用户给该用户触发消息通知)
1.模型类或者视图中调用get_channel_layers的时候，payload有没有传递给consumers.py中对应的方法（WebSocket对应的Consumer类）
2.consumers.py中self.send()方法，数据发送给前端时出错
3.前端websocket api中的onmessage方法，没有正确解析event.data， 可以使用console.log测试

第三部：Frames中data有websocket消息，但是没有消息通知提示
1.js对html标签的操作是否有误，对于点赞数和评论数的更新，看下update_social_activity函数

"""
