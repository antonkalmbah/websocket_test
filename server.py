import os

from aiohttp import web

async def wshandler(request: web.Request):
    resp = web.WebSocketResponse()  # создаём объект HTTP-ответа
    available = resp.can_prepare(request)  # проверка, можем ли мы ответить сразу
    if not available:
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)  # открывает соединение через webscocket

    await resp.send_str("Welcome!!!")  # шлём сообщение

    try:
        print("Someone joined.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone joined")  # отправляем всем, что у нас новый пользователь
        request.app["sockets"].append(resp)
        
        # здесь функция перебирает по одному все сообщения пользователя через итератор for. Если сообщение нет, то они
        # передаются в EventLoop, который отслеживает их новое появление
        async for msg in resp:
            if msg.type == web.WSMsgType.TEXT:
                for ws in request.app["sockets"]:
                    if ws is not resp:
                        await ws.send_str(msg.data)
            else:
                return resp
        return resp

    finally:
        request.app["sockets"].remove(resp)  # убирает соединение из списка
        print("Someone disconnected.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone disconnected.")  # рассылаем сообщение, что соединения разорвано 


# создаём функцию, чтобы кооректно закрыть работу сервера
async def on_shutdown (app: web.Application):
    for ws in app["sockets"]:
        await ws.close()

def init():
    app = web.Application()
    app ["sockets"] = []  # здесь мы храним все соединения
    app.router.add_get("/", wshandler)  # тут обработчик для get-запросов, которые поступают по пути "/"
    # в нём мы будем опредлелять куда идёт этот get-запрос (на сервер или в websocket)
    app.on_shutdown.append(on_shutdown)
    return app

web.run_app(init())  # здесь выполняется вес event loop

