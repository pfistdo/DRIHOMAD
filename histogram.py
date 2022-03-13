# add the following Python code to the new file:
import matplotlib.pyplot as plt
import numpy as np
rng = np.random.RandomState(10)
a = np.hstack((rng.normal(size=1000)))
plt.hist(a, bins='auto', color='green')
plt.title("Histogram with 'auto' bins")
plt.show()
