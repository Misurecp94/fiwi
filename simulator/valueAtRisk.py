from math import ceil

import MonteCarlo.normalDistGenerator as monte


def iteration(dailyVolatility, days, startingPrice):
    result = {0: startingPrice}
    monteCarloNumbers = monte.calcrandomnumbers(0, dailyVolatility, days)
    for i in range(0, days):
        result.update({i + 1: (result[i] * (1 + monteCarloNumbers[i]))})
    return result


def multipleIterations(dailyVolatility, days, startingPrice, numberofIterations):
    iterations = {}
    for i in range(0, numberofIterations):
        iterations.update({i: iteration(dailyVolatility, days, startingPrice)})
    return iterations


def results(dailyVolatility, days, startingPrice, numberofIterations):
    help = multipleIterations(dailyVolatility, days, startingPrice, numberofIterations)
    endresults = []
    for i in range(0, len(help) - 1):
        endresults.append(help[i][len(help[i]) - 1])
    return endresults


def valueAtRisk(dailyVolatility, days, startingPrice, numberofIterations, percentage):
    value = {}
    endresults = results(dailyVolatility, days, startingPrice, numberofIterations)
    endresults.sort()
    returns = []
    for i in range(0, len(endresults)):
        j = ((endresults[i]-startingPrice)/startingPrice)*100
        returns.append(j)
    value.update({'returnsSorted': returns})
    value.update({'numberofIterations': numberofIterations})
    value.update({'dataSorted': endresults})
    value.update({'startingPrice': startingPrice})
    var = (1-(percentage / 100)) * (len(returns)+1)
    value.update({'varThreshhold': var})
    value.update({'valueAtRisk': returns[round(var)]})
    value.update({'percentage': percentage})
    return value

#test = valueAtRisk(0.002, 1, 100, 200, 5)
#print(test)

