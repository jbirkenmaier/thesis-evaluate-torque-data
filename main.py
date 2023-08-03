import function_library as fl
import numpy as np


print(isinstance('4',int))


fl.read_torque_csv(10, 'ref_30mm_16_05_23.csv', 10, 25,'results_max_reduction.csv','results_intervalled_reduction.csv')

