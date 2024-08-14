import json
import socket
from copy import deepcopy
import numpy as np
from utils import logger

log = logger.get_logger(__name__)


class BackendServer:

    def __init__(self, port=65432):
        self.port = port
        self.index = 0
        self.payload_template = {"Index": 0, "Optimized Variables": [], "Pulse 1": {"Time": [], "Value": []},
                                 "Pulse 2": {"Time": [], "Value": []}, "Pulse 3": {"Time": [], "Value": []}}

    def get_params(self) -> dict:
        payload = deepcopy(self.payload_template)
        payload["Index"] = self.index
        return payload

    def update_target(self, target_variable: str, target_value: float):
        pass

    def reset(self):
        pass

    def listen(self):
        self.reset()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', self.port))
            s.listen()
            self.index = 0
            while True:
                conn, addr = s.accept()
                with conn:
                    log.info(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        req = data[0]
                        if req == 48:  # b'0', request for new parameters
                            payload = self.get_params()
                            payload = json.dumps(payload)
                            length = len(payload)
                            head = length.to_bytes(4, byteorder='big', signed=False)
                            conn.sendall(head)
                            conn.sendall(payload.encode())
                        elif req == 49:  # b'1, update target variable
                            msg = json.loads(data[1:].decode())
                            self.update_target(msg["Variable"], msg["Value"])
                            conn.sendall("OK".encode())
                            self.index += 1


class DummyOptimizerBackend(BackendServer):

    def __init__(self, port=65432):
        BackendServer.__init__(self, port=port)
        self.last_t = -1

    def get_params(self) -> dict:
        payload = BackendServer.get_params(self)
        payload["Optimized Variables"].append({"n": "testvar", "v": self.last_t})
        t = np.linspace(0, 100, 400)
        v = np.sin(t * ((self.last_t * 10) % np.pi) * 2 * np.pi / 100)
        payload["Pulse 1"]["Time"] = t.tolist()
        payload["Pulse 1"]["Value"] = v.tolist()
        print(payload)
        return payload

    def update_target(self, target_variable: str, target_value: float):
        print("Target '%s': %.3f" % (target_variable, target_value))
        self.last_t = target_value


if __name__ == "__main__":
    be = DummyOptimizerBackend()
    be.listen()
