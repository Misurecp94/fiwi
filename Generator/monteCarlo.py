# Generates Random numbers from the normal distribution, with the help of the numpy bib

import numpy as np


def calcrandomnumbers(erwartungswert, varianz, anzahl):
    return np.random.normal(erwartungswert, varianz, anzahl)


class MonteCarlo:
    def __init__(self, erwartungswert, varianz, anzahl):
        self.anzahl = anzahl
        self.erwartungswert = erwartungswert
        self.varianz = varianz
        self.numbers = calcrandomnumbers(self.erwartungswert, self.varianz, self.anzahl)


