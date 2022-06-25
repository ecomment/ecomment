"""
This is a file for testing a simple inline comment.
"""
import statistics


normal_distribution = statistics.NormalDist(mu=0, sigma=1)

for i in range(-100, 100):
    assert normal_distribution.zscore(i) == i  # ecomment: Why do they call it a z-score?

assert normal_distribution.cdf(0) == 0.5
