import torch
import jax.numpy as jnp
import numpy as np
from jax import jit
from scipy.integrate import solve_ivp, odeint
from torchdiffeq import odeint as torch_odeint
import torch
# import torchode as to
from functools import partial
from jax.experimental.ode import odeint as jax_odeint
from params_and_model import system, system_jax, ODEFunc, initial_conditions, a_initial, tmin, tmax, nt

### Could https://github.com/mathLab/PyDMD be useful?

# Solve the ODE using Scipy
def solve_with_scipy(a=None):
    t = np.linspace(tmin, tmax, nt)
    if a is not None:
        a = a
    else:
        a = a_initial
    # sol = solve_ivp(lambda t, w: system(w, t, a), [tmin, tmax], initial_conditions, t_eval=t, method='RK45')
    # return sol.y.T
    sol = odeint(lambda w, t: system(w, t, a), initial_conditions, t)
    return sol

# Solve the ODE using PyTorch
def solve_with_pytorch(a=None, odefunc:ODEFunc=None, initial_conditions_torch=None):
    if initial_conditions_torch is None:
        initial_conditions_torch = torch.tensor(initial_conditions, requires_grad=True)
    if a is not None:
        a = torch.tensor(a, requires_grad=True)
    else:
        a = torch.tensor(a_initial, requires_grad=True)
    t_torch = torch.linspace(tmin, tmax, nt)
    if odefunc is not None:
        ode_system = odefunc
        odefunc.a.data = a
    else:
        ode_system = ODEFunc(a)
    solution_torch = torch_odeint(ode_system, initial_conditions_torch, t_torch, method='dopri5')
    return solution_torch

# Solve the ODE using JAX
def solve_with_jax(a=None):
    initial_conditions_jax = jnp.array(initial_conditions)#, dtype=jnp.float64)
    if a is not None:
        a_jax = a
    else:
        a_jax = jnp.array(a_initial, dtype=jnp.float64)
    t_jax = jnp.linspace(tmin, tmax, nt)
    system_jit = jit(system_jax)
    # solution_jax = jax_odeint(system_jit, initial_conditions_jax, t_jax, a_jax)
    solution_jax = jax_odeint(partial(system_jit, a=a_jax), initial_conditions_jax, t_jax)
    return solution_jax