import threading
from threading import Lock

import numpy as np
from quocslib.Optimizer import Optimizer
from quocslib.utils.AbstractFoM import AbstractFoM

from utils import logger
import FoM
from BackendServer import BackendServer

log = logger.get_logger(__name__)

lock = Lock()


def execute_optimizer(optimizer: Optimizer):
    optimizer.execute()


class OptimizerBackend(BackendServer, AbstractFoM):

    def __init__(self, fom: FoM, pulse_offset=0.0, port=65432):
        BackendServer.__init__(self, port=port)
        self.fom = fom
        self.synced = False
        self.pulses = [np.array([]), np.array([]), np.array([])]
        self.timings = [np.array([]), np.array([]), np.array([])]
        self.parameters = []
        self.sync_lock = Lock()
        self.pulse_offset = pulse_offset
        self.optimizer = None

    def set_optimizer(self, optimizer: Optimizer, optimizer_dict: dict, start_thread=True):
        self.optimizer = optimizer
        self.opt_dict = optimizer_dict
        if start_thread:
            self.start_optimizer()

    def start_optimizer(self):
        self.opt_thread = threading.Thread(target=execute_optimizer, args=(self.optimizer,))
        self.opt_thread.start()

    def get_params(self) -> dict:
        payload = BackendServer.get_params(self)
        if not self.sync_lock.locked():
            self.sync_lock.acquire()  # cycle starts, lock for next exp cycles (until fid measured)
            # reset for next FoM measurement
            self.fom.reset()
        for i, p in enumerate(self.parameters):
            name = self.opt_dict["parameters"][i]["parameter_name"]
            payload["Optimized Variables"].append({"n": name, "v": p})
            pass
        for i in range(min(len(self.pulses), 3)):
            payload["Pulse %d" % (i + 1)]["Time"] = self.timings[i].tolist()
            payload["Pulse %d" % (i + 1)]["Value"] = (self.pulses[i] + self.pulse_offset).tolist()
        return payload

    def update_target(self, target_variable: str, target_value: float):
        log.info("Target '%s': %.3f" % (target_variable, target_value))
        stop = self.fom.update(target_value)
        if self.sync_lock.locked() and stop:
            self.fom.update_record()
            self.sync_lock.release()  # cycle ended, release lock

    def reset(self):
        self.synced = False

    def get_FoM(self, pulses: list = [],
                parameters: list = [],
                timegrids: list = []) -> dict:
        "this is called asynchroneously"
        if not self.synced:  # does this thread hold the lock already?
            self.sync_lock.acquire()  # it doesn't -> wait for exp cycles to complete
        self.pulses = pulses
        self.parameters = parameters
        self.timings = timegrids
        self.sync_lock.release()
        # wait for exp cycle to start
        while not self.sync_lock.locked():
            pass

        # get lock and compute new pulses
        self.sync_lock.acquire()
        self.synced = True
        return {"FoM": self.fom.get()}
