import numpy as np

from simulator.valueAtRisk import valueAtRisk


def cValueAtRisk(values):
    valueAtRisk = values['valueAtRisk']
    data = values['dataSorted']
    valueThreshhold = np.ceil(values['varThreshhold'])
    # Stimmt vlt nicht.
    result = (1/(values['startingPrice']-values['valueAtRisk']))*np.sum(data[0:int(np.ceil(valueThreshhold))])
    values.update({'cValueAtRisk': result})
    return values

# Funktioniert!
test = cValueAtRisk(valueAtRisk(0.02, 100, 1000, 200, 5))
print(test['cValueAtRisk'])
print(test['startingPrice'] - test['valueAtRisk'])
print(1-test['valueAtRisk']/test['startingPrice'])
