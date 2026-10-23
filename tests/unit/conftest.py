"""Fixtures for the async client tests: a local aiohttp server with queued replies."""

from typing import Any, Dict, List, Optional, Tuple

import pytest
import pytest_asyncio
from aiohttp import web

from wattnet.client import AsyncWattnetRawClient

from ..conftest import TOKEN

DROP = object()  # queue marker: close the connection without answering


class FakeServer:
    """Serves queued responses, recording every request it receives."""

    def __init__(self) -> None:
        self.queues: Dict[Tuple[str, str], List[Any]] = {}
        self.requests: List[web.BaseRequest] = []
        self.base_url = ""
        self.token_url = ""

    def add(
        self,
        method: str,
        path: str,
        json: Any = None,
        status: int = 200,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.queues.setdefault((method, path), []).append(
            (status, json, text, headers or {})
        )

    def drop(self, method: str, path: str) -> None:
        self.queues.setdefault((method, path), []).append(DROP)

    def calls(self, method: str, path: str) -> List[web.BaseRequest]:
        return [r for r in self.requests if (r.method, r.path) == (method, path)]

    async def handle(self, request: web.Request) -> web.StreamResponse:
        await request.read()  # keep the body readable once the handler is done
        self.requests.append(request)
        queue = self.queues.get((request.method, request.path))
        if not queue:
            return web.json_response({"detail": "unexpected request"}, status=599)
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if item is DROP:
            request.transport.close()
            raise ConnectionResetError
        status, payload, text, headers = item
        if text is not None:
            return web.Response(text=text, status=status, headers=headers)
        return web.json_response(payload, status=status, headers=headers)


@pytest_asyncio.fixture
async def server():
    fake = FakeServer()
    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", fake.handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    fake.base_url = f"http://127.0.0.1:{port}/v1"
    fake.token_url = f"http://127.0.0.1:{port}/token"
    yield fake
    await runner.cleanup()


@pytest.fixture
def make_client(server):
    def factory(**kwargs):
        kwargs.setdefault("base_url", server.base_url)
        kwargs.setdefault("token_url", server.token_url)
        kwargs.setdefault("retry_delay", 0)
        if not any(k in kwargs for k in ("token", "client_id")):
            kwargs["token"] = TOKEN
        return AsyncWattnetRawClient(**kwargs)

    return factory
