import math

from simulator.cValueAtRisk import cValueAtRisk
from simulator.valueAtRisk import valueAtRisk


def klassen(value):
    min = value['returnsSorted'][0]
    max = value['returnsSorted'][len(value['returnsSorted']) - 1]
    numberOfClasses = math.sqrt(value['numberofIterations'])
    if(numberOfClasses<20):
        numberOfClasses=20
    result = {}
    result.update({'min': min})
    result.update({'max': max})
    result.update({'numberOfClasses': numberOfClasses})
    classWidth = (max-min)/numberOfClasses
    result.update({'klassenbreite': classWidth})
    return result

# For Testing purposes!
# test = cValueAtRisk(valueAtRisk(0.01642, 100, 10, 5, 95)) # 95% iges Konfidenzintervall
# print(test['valueAtRisk'])
# print(klassen(test))
