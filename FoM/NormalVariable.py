import numpy as np
import scipy.stats as stats

from utils import logger
from FoM import FoM

log = logger.get_logger(__name__)


class NormalVariable(FoM):
    """
    Estimator for normal distributed variable. Stops when accuracy is reached or when unlikely to beat record.
    """

    def __init__(self, accuracy=0.1, confidence=0.95):
        self.acc = accuracy
        self.conf = confidence
        self.samples = []
        self.estimate = 0
        self.est_err = 0
        self.record = 0

    def reset(self):
        self.estimate = 0
        self.est_err = 0
        self.samples = []

    def update(self, target_value: float) -> bool:
        self.samples.append(target_value)
        self.estimate = float(np.mean(self.samples))
        if len(self.samples) > 1:
            s = stats.sem(self.samples, ddof=1)
            c = stats.t(len(self.samples) - 1).ppf(1 / 2 + self.conf / 2)
            print(c)
            err = c * s
        else:
            err = np.nan
        self.est_err = err
        log.info("%i (%.1e) - variable %.2e +/- %.2e (%.1f%%)" % (len(self.samples) - 1, target_value, self.estimate,
                                                                  err, abs(err / self.estimate) * 100))
        if abs(err / self.estimate) <= self.acc:  # accurate enough -> stop
            return True
        if self.estimate + err < self.record:  # this is gonna be worse -> stop
            log.info("----> stop early")
            return True
        return False

    def get(self) -> float:
        return self.estimate

    def update_record(self) -> float:
        if self.estimate > self.record:
            self.record = self.estimate  # update record
        return self.record


if __name__ == "__main__":
    logger.setup_applevel_logger()
    fom = NormalVariable()
    meas = [30, 55, 67, 41, 81, 65, 38, 50, 52, 54, 52, 52, 52, 52, 52, 52, 52, 52, 52, 100, 100]
    for m in meas:
        if fom.update(m):
            break
    fom.update_record()
    fom.reset()
    meas = [10, 4.5, 6.7, 11.1, 8, 6, 3.8, 5, 4, 7]
    for m in meas:
        if fom.update(m):
            break