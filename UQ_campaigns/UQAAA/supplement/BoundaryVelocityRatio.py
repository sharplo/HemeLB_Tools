import matplotlib.pyplot as plt
import numpy as np

from scipy.special import jv

plt.rc('font', family='serif')

dx = 1.0e-4
h = 1.775e-3 #m, wall thickness
PR = 0.5 #Poisson Ratio
rho = 1050 #kg/m3 fluid density
rhoS = rho #kg/m3 wall density


x=np.linspace(0,0.1)

for r in [13, 20, 27]: #sites per radius
    for a in [10.1, 12.3]: #womersley number
        R=r*dx
        Lambda = (1j**1.5)*a #Wommersley

        g = 2*jv(1,Lambda)/(Lambda*jv(0,Lambda))

        A = (g-1)*(PR**2-1)
        B = (rhoS*h*(g-1))/(rho*R) + (2*PR-0.5)*g - 2
        C = 2*rhoS*h/(rho*R) + g

        roots = np.roots([A,B,C])
        nu = max(roots[0],roots[1])

        M = (2+nu*(2*PR-1))/(nu*(2*PR-g))

        print("M = ", M)

        plt.figure(1)
        f1 = []
        for i in x:
            f1.append((1-M)/(1-M*jv(0,Lambda*(1-i))/jv(0,Lambda)))
        plt.plot(100*x,f1,label='Wo=%s, r=%s dx' %(a,r))
        print('f1', min(f1))

plt.legend()
plt.xlabel('Extension (%)')
plt.ylabel('F')
plt.grid()
plt.minorticks_on()
plt.savefig("lineF.png")


plt.figure(2)
R = 20*dx #m, Average Wall position
Extend = np.arange(0.00,0.10,0.0025)
Wom = np.arange(10.1,12.3,0.2) # Wommersley
f = np.zeros(len(Extend)*len(Wom))
i=0
for e in Extend:
    for a in Wom:
        Lambda = (1j**1.5)*a

        g = 2*jv(1,Lambda)/(Lambda*jv(0,Lambda))

				# Solve for nu in a quadratic equation
        A = (g-1)*(PR**2-1)
        B = (rhoS*h*(g-1))/(rho*R) + (2*PR-0.5)*g - 2
        C = 2*rhoS*h/(rho*R) + g

        roots = np.roots([A,B,C])
        nu = max(roots[0],roots[1])

        M = (2+nu*(2*PR-1))/(nu*(2*PR-g))

        f[i] = ((1-M)/(1-M*jv(0,Lambda*(1-e))/jv(0,Lambda)))
        i=i+1

print('mean', np.average(f))
print('median', np.median(f))
print('min', np.min(f))

plt.imshow(f.reshape(len(Extend),len(Wom)), aspect="auto", extent=[10.1,12.3,0,10], origin='lower')
plt.colorbar(label='F') 
plt.xlabel("Womersley Number")
plt.ylabel("Extension (%)")
plt.savefig("mapF.png")
