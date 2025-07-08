import numpy as np
import matplotlib.pyplot as plt

c = 3e8
pi = np.pi
n_water = 1.33
e1 = n_water**2
gamma = 4.353e12

wss = np.linspace(1820e-9, 1870e-9, 1000)
omega = 2*pi*c/ wss

eps = 1 - (wp**2) / (omega**2 + 1j * gamma * omega)
alpha = (4*pi*(100e-9)**3) * (eps - e1)/(eps + 2 * e1)
alpha2 = (4*pi*(100e-9)**3) * (eps - e2)/(eps + 2 * e2)



plt.plot(wss * 1e9, np.abs(alpha), 'k')
plt.plot(wss*1e9, np.abs(alpha2), 'b')
plt.xlabel('Wavelength (nm)')
plt.ylabel('a')
plt.show()
e2 = 1.34**2
wp = 2.18e15
