
import json
import random
import string

import pytest
from requests_toolbelt import sessions

TEST_TOPIC = "aura.aivia-test"


class TestKarapace():
    @pytest.fixture(scope="module")
    def session(self):
        return sessions.BaseUrlSession(base_url="http://localhost:8080")

    @pytest.fixture(scope="module")
    def message(self):
        message = list(string.ascii_letters)
        random.shuffle(message)
        return "".join(message)

    def test_karapace(self, session, message):
        self.produce_message(session, message)
        self.consume_message(session, message)

    def produce_message(self, session, message):
        session.post(f"/topics/{TEST_TOPIC}", json={"records": [{"value": message}]})

    def consume_message(self, session, message):
        name = "test" + random.choice(string.ascii_lowercase)
        resp = session.post(f"/consumers/{name}", json={"name": name, "format": "binary", "auto.offset.reset": "earliest"})
        resp.raise_for_status()
        consumer_id = resp.json()["instance_id"]
        try:
            resp = session.post(f"/consumers/{name}/instances/{consumer_id}/subscription", json={"topics": TEST_TOPIC})
            resp.raise_for_status()
            resp = session.get(f"/consumers/{name}/instances/{consumer_id}/records", headers={"Accept": "application/vnd.kafka.binary.v2+json"})
            resp.raise_for_status()
            records = json.loads(resp.content.decode("utf-8", errors="ignore"))
            assert any(r["value"] == message for r in records)
        finally:
            session.delete(f"/consumers/{name}/instances/{consumer_id}")
