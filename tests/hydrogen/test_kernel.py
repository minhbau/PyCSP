# -*- coding: utf-8 -*-
import cantera as ct
import numpy as np
import matplotlib.pyplot as plt
import cspFunctions as csp
import sys

#create gas from original mechanism file gri30.cti
gas = csp.CanteraCSP('hydrogen.cti')
#reorder the gas to match pyJac (N2 in last place)
n2_ind = gas.species_index('N2')
specs = gas.species()[:]
gas = csp.CanteraCSP(thermo='IdealGas', kinetics='GasKinetics',
        species=specs[:n2_ind] + specs[n2_ind + 1:] + [specs[n2_ind]],
        reactions=gas.reactions())

#set the gas state
T = 1000
P = ct.one_atm
#gas.TPX = T, P, "H2:2.0, O2:1, N2:3.76"
gas.TP = T, P
gas.set_equivalence_ratio(1.0, 'H2', 'O2:1, N2:3.76')

#equilibrium
#gas.equilibrate('HP')


#integrate ODE
r = ct.IdealGasConstPressureReactor(gas)
sim = ct.ReactorNet([r])
time = 0.0
states = ct.SolutionArray(gas, extra=['t'])


evals = []
Revec = []
Levec = []
fvec = []
sim.set_initial_time(0.0)
while sim.time < 1000.0:
    sim.step()
    states.append(r.thermo.state, t=sim.time)
    print('%10.3e %10.3f %10.3f %14.6e' % (sim.time, r.T, r.thermo.P, r.thermo.u))
    lam,R,L,f = gas.get_kernel()
    evals.append(lam)
    Revec.append(R)
    Levec.append(L)
    fvec.append(f)
    
evals = np.array(evals)
Revec = np.array(Revec)
Levec = np.array(Levec)
fvec = np.array(fvec)


#plot solution
print('plotting ODE solution...')
plt.clf()
plt.subplot(2, 2, 1)
plt.plot(states.t, states.T)
plt.xlabel('Time (s)')
plt.ylabel('Temperature (K)')
plt.xlim(0., 0.002)
plt.subplot(2, 2, 2)
plt.plot(states.t, states.X[:,gas.species_index('OH')])
plt.xlabel('Time (s)')
plt.ylabel('OH Mole Fraction')
plt.xlim(0., 0.002)
plt.subplot(2, 2, 3)
plt.plot(states.t, states.X[:,gas.species_index('H')])
plt.xlabel('Time (s)')
plt.ylabel('H Mole Fraction')
plt.xlim(0., 0.002)
plt.subplot(2, 2, 4)
plt.plot(states.t, states.X[:,gas.species_index('H2')])
plt.xlabel('Time (s)')
plt.ylabel('H2 Mole Fraction')
plt.xlim(0., 0.002)
plt.tight_layout()
plt.show()

#plot eigenvalues
logevals = np.clip(np.log10(np.abs(evals)),0,100)*np.sign(evals.real)
print('plotting eigenvalues...')
fig, ax = plt.subplots(figsize=(6,4))
for idx in range(evals.shape[1]):
    #color = next(ax._get_lines.prop_cycler)['color']
    ax.plot(states.t, logevals[:,idx], color='black', marker='.', markersize = 2,linestyle = 'None')
ax.set_xlabel('time (s)')
ax.set_ylabel('evals')
ax.set_ylim([-9, 6])
ax.set_xlim([0., 0.001])
ax.grid(False)
plt.show()
#plt.savefig('figures/prediction_combined.png', dpi=500, transparent=False)