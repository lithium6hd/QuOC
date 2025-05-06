#Imports for M-LOOP

import mloop.interfaces as mli

import mloop.controllers as mlc

import mloop.visualizations as mlv


#Other imports

import numpy as np

import time


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


def execute_optimizer(optimizer):
    optimizer.optimize()


class MloopInterface(mli.Interface):

    def __init__(self, fom: FoM, minimize_fom=True):
        super(MloopInterface, self).__init__()
        self.be = MloopBackendServer(fom)
        self.minimize_fom = minimize_fom

    def get_next_cost_dict(self, params_dict):
        parameters = params_dict['params']


        if not self.be.synced:  # does this thread hold the lock already?
            self.be.sync_lock.acquire()  # it doesn't -> wait for exp cycles to complete
        self.be.parameters = parameters

        self.be.sync_lock.release()
        # wait for exp cycle to start
        while not self.be.sync_lock.locked():
            pass

        # get lock and compute new pulses
        self.be.sync_lock.acquire()
        self.be.synced = True

        if self.minimize_fom:
            cost_function = self.be.fom.get()
        else:
            cost_function = -self.be.fom.get()

        return {'cost': cost_function, 'bad': False}  # , 'uncer': self.be.fom.get_errror()


class MloopInterfaceParametersInCost(mli.Interface):

    def __init__(self, fom: FoM, minimize_fom=True):
        super(MloopInterface, self).__init__()
        self.be = MloopBackendServer(fom)
        self.minimize_fom = minimize_fom

    def get_next_cost_dict(self, params_dict):
        parameters = params_dict['params']


        if not self.be.synced:  # does this thread hold the lock already?
            self.be.sync_lock.acquire()  # it doesn't -> wait for exp cycles to complete
        self.be.parameters = parameters

        self.be.sync_lock.release()
        # wait for exp cycle to start
        while not self.be.sync_lock.locked():
            pass

        # get lock and compute new pulses
        self.be.sync_lock.acquire()
        self.be.synced = True

        if self.minimize_fom:
            cost_function = self.be.fom.get(parameters)
        else:
            cost_function = -self.be.fom.get(parameters)

        return {'cost': cost_function, 'bad': False}  # , 'uncer': self.be.fom.get_errror()


class MloopBackendServer(BackendServer):

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

    def set_optimizer(self, interface, optimizer_dict: dict, start_thread=True):
        num_params = np.size(optimizer_dict["parameters"]["name"])
        min_boundary = optimizer_dict["parameters"]["min_boundary"]
        max_boundary = optimizer_dict["parameters"]["max_boundary"]
        first_params = optimizer_dict["parameters"]["first_params"]
        self.optimizer = mlc.create_controller(interface, num_params=num_params, min_boundary=min_boundary, max_boundary=max_boundary, first_params=first_params, **optimizer_dict)

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
            name = self.opt_dict["parameters"]["name"][i]  #["parameter_name"]
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


from quocslib.utils.inputoutput import readjson

from utils import logger
from FoM.NormalVariable import NormalVariable
from FoM.Fluctuations import Fluctuations
from FoM.PreparationSpeed import SpeedAndAtomNumber

if __name__ == "__main__":
    # logger.setup_applevel_logger()
    #fom = Fidelity(2)
    #fom = NormalVariable()
    fom = Fluctuations(number_of_samples=50)
    interface = MloopInterface(fom, minimize_fom=True)
    opt_dict = readjson(r'OptimizationConfigurations\mloop_sai.json')
    optimizer = interface
    interface.be.set_optimizer(optimizer, opt_dict)
    interface.be.listen()

    mlv.show_all_default_visualizations(interface.be.optimizer)
