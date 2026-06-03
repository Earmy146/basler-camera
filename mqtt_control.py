import json
import os
import ssl
import threading
import time
import uuid


class MqttViewerSync:
    def __init__(self, pattern_names):
        self.pattern_names = pattern_names
        self.host = os.environ.get("DEFLECTO_MQTT_HOST", "").strip()
        self.port = int(os.environ.get("DEFLECTO_MQTT_PORT", "8883"))
        self.username = os.environ.get("DEFLECTO_MQTT_USERNAME", "").strip()
        self.password = os.environ.get("DEFLECTO_MQTT_PASSWORD", "")
        self.session = os.environ.get("DEFLECTO_MQTT_SESSION", "default").strip() or "default"
        self.topic_prefix = os.environ.get(
            "DEFLECTO_MQTT_TOPIC_PREFIX",
            f"deflectometry/{self.session}",
        ).strip().strip("/")
        self.retain = os.environ.get("DEFLECTO_MQTT_RETAIN", "1") != "0"
        self.expected_acks = int(os.environ.get("DEFLECTO_MQTT_EXPECTED_VIEWERS", "0"))
        self.ack_timeout = float(os.environ.get("DEFLECTO_MQTT_ACK_TIMEOUT_SEC", "2.0"))
        self.pattern_t = os.environ.get("DEFLECTO_PATTERN_T", "").strip()
        self.client = None
        self.connected = threading.Event()
        self.acks = {}
        self.acks_lock = threading.Lock()
        self.version = int(time.time() * 1000)

    @property
    def cmd_topic(self):
        return f"{self.topic_prefix}/cmd"

    @property
    def ack_topic(self):
        return f"{self.topic_prefix}/ack"

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        is_failure = getattr(reason_code, "is_failure", False)
        try:
            rc = int(reason_code)
        except Exception:
            rc = 1 if is_failure else 0

        if rc == 0 and not is_failure:
            self.connected.set()
            client.subscribe(self.ack_topic, qos=1)
        else:
            print(f"  [MQTT] connect failed rc={reason_code}")

    def _on_disconnect(self, client, userdata, *args):
        self.connected.clear()

    def _on_message(self, client, userdata, msg):
        if msg.topic != self.ack_topic:
            return
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            return

        version = payload.get("version")
        viewer_id = payload.get("viewerId") or payload.get("viewer_id")
        if version is None or not viewer_id or payload.get("ready") is False:
            return

        with self.acks_lock:
            viewers = self.acks.setdefault(int(version), set())
            viewers.add(str(viewer_id))

    def connect(self):
        if self.client is not None:
            return True
        if not self.host:
            print("  [MQTT] DEFLECTO_MQTT_HOST chua duoc cau hinh.")
            return False

        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            print("  [MQTT] Thieu thu vien paho-mqtt. Cai bang: pip install paho-mqtt")
            return False

        client_id = f"deflecto-capture-{uuid.uuid4().hex[:8]}"
        try:
            client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=client_id,
                clean_session=True,
            )
        except (AttributeError, TypeError):
            client = mqtt.Client(client_id=client_id, clean_session=True)
        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message
        if self.username or self.password:
            client.username_pw_set(self.username, self.password)
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

        try:
            client.connect(self.host, self.port, keepalive=30)
        except Exception as exc:
            print(f"  [MQTT] Khong ket noi duoc broker {self.host}:{self.port}: {exc}")
            return False

        client.loop_start()
        self.client = client
        if not self.connected.wait(timeout=5):
            print("  [MQTT] Timeout khi ket noi broker.")
            return False

        print(f"  [MQTT] connected {self.host}:{self.port}, topic={self.cmd_topic}")
        return True

    def sync(self, idx):
        if not self.connect():
            return

        idx = max(0, min(len(self.pattern_names) - 1, int(idx)))
        self.version += 1
        payload = {
            "idx": idx,
            "name": self.pattern_names[idx],
            "version": self.version,
            "ts": time.time(),
        }
        if self.pattern_t:
            payload["T"] = int(float(self.pattern_t))

        info = self.client.publish(
            self.cmd_topic,
            json.dumps(payload, separators=(",", ":")),
            qos=1,
            retain=self.retain,
        )
        info.wait_for_publish(timeout=2)
        print(f"  [MQTT] viewer -> {self.pattern_names[idx]} v{self.version}")

        if self.expected_acks <= 0:
            return

        deadline = time.monotonic() + self.ack_timeout
        while time.monotonic() < deadline:
            with self.acks_lock:
                ack_count = len(self.acks.get(self.version, set()))
            if ack_count >= self.expected_acks:
                print(f"  [MQTT] ack {ack_count}/{self.expected_acks}")
                return
            time.sleep(0.02)

        with self.acks_lock:
            ack_count = len(self.acks.get(self.version, set()))
        print(f"  [MQTT] WARN ack {ack_count}/{self.expected_acks} before timeout")

    def close(self):
        if self.client is None:
            return
        self.client.loop_stop()
        self.client.disconnect()
        self.client = None
