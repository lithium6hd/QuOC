from utils import logger
from FoM import FoM
from fewfermions.analysis.function.fidelities import wilson_score

log = logger.get_logger(__name__)


class Fidelity(FoM):

    def __init__(self, target_value: float, conservative=True, accuracy=0.1, confidence=0.95):
        self.target = target_value
        self.acc = accuracy
        self.conf = confidence
        self.n_smpl = 0
        self.n_success = 0
        self.fidelity_record = 0
        self.fidelity = 0
        self.fid_err = 0
        self.cnsv = conservative

    def reset(self):
        self.n_smpl = 0
        self.n_success = 0
        self.fidelity = 0
        self.fid_err = 0

    def update(self, target_value: float) -> bool:
        self.n_smpl += 1
        success = (self.target == target_value)
        if success:
            self.n_success += 1
        fid, err = wilson_score(self.n_smpl, self.n_success, 1 - self.conf)
        self.fidelity = fid - err
        self.fid_err = err
        log.info("%i (%i) - fidelity %.2f%% +/- %.1f%%" % (self.n_smpl - 1, 1 if success else 0, fid * 100,
                                                              err * 100))
        if err <= self.acc:  # accurate enough -> stop
            return True
        if fid + err < self.fidelity_record:  # this is gonna be worse -> stop
            log.info("----> stop early")
            return True
        return False

    def get(self) -> float:
        return self.fidelity - self.fid_err if self.cnsv else self.fidelity  # take lower bound when conservative

    def update_record(self) -> float:
        if self.fidelity > self.fidelity_record:
            self.fidelity_record = self.fidelity  # update record
        return self.fidelity_record


if __name__ == "__main__":
    logger.setup_applevel_logger()
    fid = Fidelity(2)
    at_numbers = [0] + [2 for _ in range(20)]
    for n in at_numbers:
        if fid.update(n):
            print("stop")
            break
    fid.update_record()
    fid.reset()
    at_numbers = [0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for n in at_numbers:
        if fid.update(n):
            print("stop")
            break