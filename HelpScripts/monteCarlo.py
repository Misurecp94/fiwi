

from HelpScripts.normalDistGenerator import calcrandomnumbers

# Hold one the one hand, all settings used by the user, on the other hand the calculated random normal distribution
# numbers


class MonteCarlo:
    def __init__(self, erwartungswert, varianz, anzahl):
        self.anzahl = anzahl
        self.erwartungswert = erwartungswert
        self.varianz = varianz
        self.numbers = calcrandomnumbers(self.erwartungswert, self.varianz, self.anzahl)
