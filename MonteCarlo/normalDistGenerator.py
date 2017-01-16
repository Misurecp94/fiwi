# NUMPY THE LITTLE ELEPHANT
import numpy as np

# Calculates "anzahl" random numbers from the normal distribution N(erwartungswert,varianz)
#

def calcrandomnumbers(erwartungswert, varianz, anzahl):
    return np.random.normal(erwartungswert, varianz, anzahl)
