import base64
import json
import pytest
import random
import string
from pprint import pprint
from requests_toolbelt import sessions

TEST_TOPIC = "nais.aivia-test"


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
        name, consumer_id = _create_consumer_subscription(session)
        try:
            produce_message(session, message)
            consume_message(session, name, consumer_id, message)
        finally:
            _delete_consumer(session, name, consumer_id)


def produce_message(session, message):
    record = {"value": base64.b64encode(message.encode("utf-8")).decode("utf-8")}
    resp = session.post(f"/topics/{TEST_TOPIC}", json={"records": [record]})
    resp.raise_for_status()
    offset_data = resp.json()["offsets"][0]
    print(f"Produced record {record} for message {message} to topic {TEST_TOPIC}")
    print(f"The record was produced to partition {offset_data['partition']} at offset {offset_data['offset']}")


def consume_message(session, name, consumer_id, message):
    try:
        resp = session.get(f"/consumers/{name}/instances/{consumer_id}/records",
                           headers={"Accept": "application/vnd.kafka.binary.v2+json"})
        resp.raise_for_status()
        records = json.loads(resp.content.decode("utf-8", errors="ignore"))
        print(f"Received {len(records)} records")
        pprint(records)
        values = [base64.b64decode(r["value"].encode("utf-8")).decode("utf-8") for r in records]
        print(f"Values: {values}")
        assert any(v == message for v in values)
    finally:
        resp = session.delete(f"/consumers/{name}/instances/{consumer_id}")
        resp.raise_for_status()


def _create_consumer_subscription(session):
    name = "test_" + "".join(random.choice(string.ascii_lowercase) for _ in range(8))
    resp = session.post(f"/consumers/{name}", json={"name": name, "format": "binary", "auto.offset.reset": "latest"})
    resp.raise_for_status()
    consumer_id = resp.json()["instance_id"]
    resp = session.post(f"/consumers/{name}/instances/{consumer_id}/subscription", json={"topics": TEST_TOPIC})
    resp.raise_for_status()
    return name, consumer_id


def _delete_consumer(session, name, consumer_id):
    session.delete(f"/consumers/{name}/instances/{consumer_id}")
