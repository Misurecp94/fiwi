import numpy as np

from simulator.valueAtRisk import valueAtRisk


def cValueAtRisk(values):
    valueAtRisk = values['valueAtRisk']
    data = values['dataSorted']
    returns = values['returnsSorted']
    valueThreshhold = np.ceil(values['varThreshhold'])
    result = (1 / valueThreshhold) * np.sum(returns[0:int(np.round(valueThreshhold))])
    values.update({'cValueAtRisk': result})
    return values

# Funktioniert!
test = cValueAtRisk(valueAtRisk(0.01642, 1, 10, 20000, 95)) # 95% iges Konfidenzintervall
#print(test['cValueAtRisk'])
#print(test['valueAtRisk'])
#print(test['returnsSorted'])
#print(test['returnsSorted'])
#print(test['returnsSorted'])
#print(test['returnsSorted'][0])
#print(test['returnsSorted'][len(test['returnsSorted'])-1])

# EXPLANATION
# VAR(95) = -2.21% means you have a 5% chance to loose 2.21% of your portfolio
# CVAR(95) = -3.21 means in the worst 5% of returns, the average loss will be 3.21% on average