import numpy as np
from scipy.stats import t
from typing import Tuple


def corrected_resampled_t_statistic(x: np.array, n: int, n1: int, n2: int, alpha: float = 0.05) -> Tuple[float, Tuple]:
    """
    Nadeau and Bengio (2003), Bouckaert and Frank (2004)
    Corrected resampled t-statistic
    :param x: vector of differences (between two recommenders) of size n
    :param n: number of resamples
    :param n1: number of training instances
    :param n2: number of testing instances
    :param alpha: level of significance for CI
    :return: p-value, confidence interval
    """
    sample_mean = np.mean(x)
    sample_variance = np.var(x)
    corrected_std_error = np.sqrt((1/n + n2/n1) * sample_variance)
    corrected_t_statistic = sample_mean / corrected_std_error

    t_area = t.sf(np.abs(corrected_t_statistic), n - 1)
    p_value = t_area * 2
    t_value = t.isf(alpha/2, n - 1)
    confidence_interval = (sample_mean - t_value * corrected_std_error, sample_mean + t_value * corrected_std_error)
    return p_value, confidence_interval
