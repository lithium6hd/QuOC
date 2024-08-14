from quocslib.Optimizer import Optimizer
from quocslib.utils.inputoutput import readjson

from utils import logger
from OptimizerBackend import OptimizerBackend
from FoM import Fidelity
from FoM.NormalVariable import NormalVariable


if __name__ == "__main__":
    logger.setup_applevel_logger()
    #fom = Fidelity(2)
    fom = NormalVariable()
    be = OptimizerBackend(fom, pulse_offset=4.65)
    opt_dict = readjson("parameter_search_settings.json")
    #opt_dict = readjson("dcrab_setting.json")
    optimizer = Optimizer(opt_dict, be)
    be.set_optimizer(optimizer, opt_dict)
    be.listen()