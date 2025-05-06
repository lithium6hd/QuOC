import numpy as np
from scipy.stats import beta, norm


def confidence_binomial(n_sample, n_success, alpha=0.05):
    assert n_sample > 0
    assert n_success >= 0
    n = n_sample
    k = n_success
    p_l, p_u = beta.ppf([alpha / 2, 1 - alpha / 2], [k, k + 1], [n - k + 1, n - k])
    if n_sample == n_success:
        p_u = 1
    elif n_success == 0:
        p_l = 0
    return n_success / n_sample, p_l, p_u


def wilson_score(n_sample, n_success, alpha=0.05):
    assert n_sample > 0
    assert n_success >= 0
    z = norm.ppf(1 - alpha / 2)
    est = (n_success + 0.5 * z ** 2) / (n_sample + z ** 2)
    err = z / (n_sample + z ** 2) * np.sqrt(n_success * (n_sample - n_success) / n_sample + 0.25 * z ** 2)
    return est, err


if __name__ == "__main__":
    print(confidence_binomial(100, 97))
    print(wilson_score(100, 100))
