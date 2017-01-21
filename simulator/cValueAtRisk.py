import numpy as np

from simulator.valueAtRisk import valueAtRisk


def cValueAtRisk(values):
    valueAtRisk = values['valueAtRisk']
    data = values['dataSorted']
    returns = values['returnsSorted']
    valueThreshhold = np.ceil(values['varThreshhold'])
    # Stimmt vlt nicht.
    result = (1 / valueThreshhold) * np.sum(returns[0:int(np.round(valueThreshhold))])
    values.update({'cValueAtRisk': result})
    return values

# Funktioniert!
test = cValueAtRisk(valueAtRisk(0.002, 100, 100, 20, 99)) # 95% iges Konfidenzintervall
print(test['cValueAtRisk'])
print(test['valueAtRisk'])
print(test['returnsSorted'])


# EXPLANATION
# VAR(95) = -2.21% means you have a 5% chance to loose 2.21% of your portfolio on a single day
# CVAR(95) = -3.21 means in the worst 5% of returns, the average loss will be 3.21% on average