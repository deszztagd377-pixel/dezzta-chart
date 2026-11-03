import threading
import types

from app.databento_sources import DatabentoLiveSource


def test_live_source_requests_gateway_send_timestamps(monkeypatch):
    closed = threading.Event()
    clients = []

    class FakeLive:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.subscriptions = []
            self.callback = None
            self.started = False
            self.stopped = False
            clients.append(self)

        def subscribe(self, **kwargs):
            self.subscriptions.append(kwargs)

        def add_callback(self, callback):
            self.callback = callback

        def start(self):
            self.started = True

        def block_for_close(self):
            return None

        def stop(self):
            self.stopped = True

    monkeypatch.setitem(__import__("sys").modules, "databento", types.SimpleNamespace(Live=FakeLive))
    source = DatabentoLiveSource("test-key", "GLBX.MDP3", ("ESZ6",))

    source.start(lambda record: None, lambda error: closed.set())

    assert closed.wait(timeout=1)
    client = clients[0]
    assert client.kwargs == {"key": "test-key", "ts_out": True}
    assert client.subscriptions == [{
        "dataset": "GLBX.MDP3",
        "schema": "ohlcv-1s",
        "symbols": ["ESZ6"],
        "stype_in": "raw_symbol",
    }]
    assert client.started is True

    source.stop()
    assert client.stopped is True
