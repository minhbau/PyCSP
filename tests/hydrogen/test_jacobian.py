# -*- coding: utf-8 -*-
"""
@author: Riccardo Malpica Galassi, Sapienza University, Roma, Italy
"""
import cantera as ct
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.insert(0,'../..')
import src.cspFunctions as csp

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

evals_an = []
evals = []

sim.set_initial_time(0.0)
while sim.time < 1000:
    sim.step()
    states.append(r.thermo.state, t=sim.time)
    print('%10.3e %10.3f %10.3f %14.6e' % (sim.time, r.T, r.thermo.P, r.thermo.u))
    lam,R,L,f = gas.get_kernel(jacobian='numeric')
    gas.update_kernel(jacobian='analytic')
    lam_an,R_an,L_an,f_an = gas.get_kernel(jacobian='analytic')
    evals.append(lam)
    evals_an.append(lam_an)

evals_an = np.array(evals_an)    
evals = np.array(evals)



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
logevals_an = np.clip(np.log10(np.abs(evals_an)),0,100)*np.sign(evals_an.real)
print('plotting eigenvalues...')
fig, ax = plt.subplots(figsize=(6,4))
for idx in range(evals.shape[1]):
    ax.plot(states.t, logevals[:,idx], color='black', marker='.', markersize = 3,linestyle = 'None')
    ax.plot(states.t, logevals_an[:,idx], color='red', marker='.', markersize = 2,linestyle = 'None')
ax.set_xlabel('time (s)')
ax.set_ylabel('evals')
ax.set_ylim([-9, 6])
ax.set_xlim([0., 0.001])
ax.grid(False)
plt.legend(['Numeric', 'Analytic'])
plt.show()
#plt.savefig('figures/prediction_combined.png', dpi=500, transparent=False)