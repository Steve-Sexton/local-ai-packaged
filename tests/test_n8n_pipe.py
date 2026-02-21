import unittest
from unittest.mock import patch, Mock

import sys
import types

if "pydantic" not in sys.modules:
    pydantic_stub = types.ModuleType("pydantic")

    class _BaseModel:
        pass

    def _field(*, default=None, description=None):
        return default

    pydantic_stub.BaseModel = _BaseModel
    pydantic_stub.Field = _field
    sys.modules["pydantic"] = pydantic_stub

if "requests" not in sys.modules:
    requests_stub = types.ModuleType("requests")

    def _post(*args, **kwargs):
        raise RuntimeError("requests.post stub should be mocked in tests")

    requests_stub.post = _post
    sys.modules["requests"] = requests_stub

from n8n_pipe import Pipe


class TestPipe(unittest.IsolatedAsyncioTestCase):
    async def test_pipe_with_empty_messages_returns_none_and_appends_assistant_message(self):
        pipe = Pipe()
        body = {"messages": []}
        emitted_events = []

        async def emitter(event):
            emitted_events.append(event)

        result = await pipe.pipe(body, __event_emitter__=emitter)

        self.assertIsNone(result)
        self.assertEqual(body["messages"][-1]["role"], "assistant")
        self.assertIn("No messages found", body["messages"][-1]["content"])
        self.assertTrue(any(e["data"]["level"] == "error" for e in emitted_events))


    async def test_pipe_with_missing_messages_key_does_not_crash(self):
        pipe = Pipe()
        body = {}
        emitted_events = []

        async def emitter(event):
            emitted_events.append(event)

        result = await pipe.pipe(body, __event_emitter__=emitter)

        self.assertIsNone(result)
        self.assertIn("messages", body)
        self.assertEqual(body["messages"][-1]["role"], "assistant")
        self.assertIn("No messages found", body["messages"][-1]["content"])
        self.assertTrue(any(e["data"]["level"] == "error" for e in emitted_events))

    async def test_pipe_with_malformed_message_returns_controlled_error(self):
        pipe = Pipe()
        pipe.valves.n8n_url = "https://example.test/webhook"
        body = {"messages": [{"role": "user"}]}

        result = await pipe.pipe(body)

        self.assertIn("error", result)
        self.assertIn("content", result["error"])

    async def test_pipe_success_appends_response_and_returns_response_field(self):
        pipe = Pipe()
        pipe.valves.n8n_url = "https://example.test/webhook"
        pipe.valves.n8n_bearer_token = "token"
        pipe.valves.response_field = "output"
        body = {"messages": [{"role": "user", "content": "hello"}]}

        with patch("n8n_pipe.requests.post") as mock_post:
            response = Mock(status_code=200)
            response.json.return_value = {"output": "workflow reply"}
            mock_post.return_value = response

            result = await pipe.pipe(body)

        self.assertEqual(result, "workflow reply")
        self.assertEqual(body["messages"][-1], {"role": "assistant", "content": "workflow reply"})

    async def test_pipe_non_200_response_returns_error_object(self):
        pipe = Pipe()
        pipe.valves.n8n_url = "https://example.test/webhook"
        body = {"messages": [{"role": "user", "content": "hello"}]}

        with patch("n8n_pipe.requests.post") as mock_post:
            response = Mock(status_code=500, text="server error")
            mock_post.return_value = response

            result = await pipe.pipe(body)

        self.assertIn("error", result)
        self.assertIn("500", result["error"])

    async def test_emit_status_throttles_by_interval(self):
        pipe = Pipe()
        pipe.valves.emit_interval = 100
        emitted_events = []

        async def emitter(event):
            emitted_events.append(event)

        await pipe.emit_status(emitter, "info", "first", False)
        await pipe.emit_status(emitter, "info", "second", False)
        await pipe.emit_status(emitter, "info", "done", True)

        self.assertEqual(len(emitted_events), 2)
        self.assertEqual(emitted_events[0]["data"]["description"], "first")
        self.assertEqual(emitted_events[1]["data"]["description"], "done")


if __name__ == "__main__":
    unittest.main()
