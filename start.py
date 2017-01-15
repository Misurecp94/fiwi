# should ultimately display the GUI and calculate everything where the user can change the following aspects:
# number of days to keep the stock, starting price, anual volatility, number of monteCarlo iterations
# should also draw afterwards a chart (results of each iteration, iteration over all days = 1 iteration, so do it x time
# should also calculate mean, median, standard derivation, and the 5%,25% and 95% percentile of the result
# should also calculate the calc. val at risk and val at risk

# val at risk = x% chance y% oder mehr von Portfolio verlieren in einem Tag!
# calc val at risk = in the worst x% of returns the average loss will be y%

# Todo: implement methods to reduce the varianz

from Generator.monteCarlo import MonteCarlo

x = MonteCarlo(0, 1, 10)

print(x.numbers)
