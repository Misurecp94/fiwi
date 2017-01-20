# Conditional Value-at-Risk in the Normal and Student t Linear VaR Model
# (c) 2016 Pawel Lachowicz, QuantAtRisk.com

import numpy as np
import math
from scipy.stats import skew, kurtosis, kurtosistest
import matplotlib.pyplot as plt
from scipy.stats import norm, t
import pandas_datareader.data as web

# Fetching Yahoo! Finance for IBM stock data
data = web.DataReader("AAPL", data_source='yahoo',
                      start='2010-12-01', end='2016-12-01')['Adj Close']
cp = np.array(data.values)  # daily adj-close prices
ret = cp[1:] / cp[:-1] - 1  # compute daily returns

# N(x; mu, sig) best fit (finding: mu, stdev)
mu_norm, sig_norm = norm.fit(ret)
dx = 0.0001  # resolution
x = np.arange(-0.1, 0.1, dx)
pdf = norm.pdf(x, mu_norm, sig_norm)
print("Sample mean  = %.5f" % mu_norm)
print("Sample stdev = %.5f" % sig_norm)
print()

# Student t best fit (finding: nu)
parm = t.fit(ret)
nu, mu_t, sig_t = parm
nu = np.round(nu)
pdf2 = t.pdf(x, nu, mu_t, sig_t)
print("nu = %.2f" % nu)
print()

# Compute VaRs and CVaRs

h = 3
alpha = 0.01  # significance level
lev = 100 * (1 - alpha)
xanu = t.ppf(alpha, nu)

CVaR_n = alpha ** -1 * norm.pdf(norm.ppf(alpha)) * sig_norm - mu_norm
VaR_n = norm.ppf(1 - alpha) * sig_norm - mu_norm

VaR_t = np.sqrt((nu - 2) / nu) * t.ppf(1 - alpha, nu) * sig_norm - h * mu_norm
CVaR_t = -1 / alpha * (1 - nu) ** (-1) * (nu - 2 + xanu ** 2) * \
         t.pdf(xanu, nu) * sig_norm - h * mu_norm

print("%g%% %g-day Normal VaR     = %.2f%%" % (lev, h, VaR_n * 100))
print("%g%% %g-day Normal t CVaR  = %.2f%%" % (lev, h, CVaR_n * 100))
print("%g%% %g-day Student t VaR  = %.2f%%" % (lev, h, VaR_t * 100))
print("%g%% %g-day Student t CVaR = %.2f%%" % (lev, h, CVaR_t * 100))

plt.figure(num=1, figsize=(11, 6))
grey = .77, .77, .77
# main figure
plt.hist(ret, bins=50, normed=True, color=grey, edgecolor='none')
plt.hold(True)
plt.axis("tight")
plt.plot(x, pdf, 'b', label="Normal PDF fit")
plt.hold(True)
plt.axis("tight")
plt.plot(x, pdf2, 'g', label="Student t PDF fit")
plt.xlim([-0.2, 0.1])
plt.ylim([0, 50])
plt.legend(loc="best")
plt.xlabel("Daily Returns of IBM")
plt.ylabel("Normalised Return Distribution")
# inset
a = plt.axes([.22, .35, .3, .4])
plt.hist(ret, bins=50, normed=True, color=grey, edgecolor='none')
plt.hold(True)
plt.plot(x, pdf, 'b')
plt.hold(True)
plt.plot(x, pdf2, 'g')
plt.hold(True)
# Student VaR line
plt.plot([-CVaR_t, -CVaR_t], [0, 3], c='r')
# Normal VaR line
plt.plot([-CVaR_n, -CVaR_n], [0, 4], c='b')
plt.text(-CVaR_n - 0.015, 4.1, "Norm CVaR", color='b')
plt.text(-CVaR_t - 0.0171, 3.1, "Student t CVaR", color='r')
plt.xlim([-0.09, -0.02])
plt.ylim([0, 5])
plt.show()