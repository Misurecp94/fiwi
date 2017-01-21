import numpy as np

from simulator.valueAtRisk import valueAtRisk


def cValueAtRisk(values):
    valueAtRisk = values['valueAtRisk']
    data = values['dataSorted']
    valueThreshhold = np.ceil(values['varThreshhold'])
    result = (1/valueAtRisk)*np.sum(data[0:int(valueThreshhold)])
    values.update({'cValueAtRisk': result})
    return values

# Funktioniert!
test = cValueAtRisk(valueAtRisk(0.002, 1, 100, 200, 5))
print(test['cValueAtRisk'])
print(test['valueAtRisk'])
