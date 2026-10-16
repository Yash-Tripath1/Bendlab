"""Phototropic simulator + proprioception + clock (Bastien + Atamian).

Model:
  k_eff(t) = k0 * (1 + a*cos(2*pi*(ZT - phase)/24))   # clock, a=0 -> k0
  stimulus = k_eff * sin(phi - theta) - gamma*theta
  tau*dr/dt = stimulus - r
  r_clipped = clip(r, -max_rate, +max_rate)
  dtheta/dt = r_clipped

Params: k0, tau, max_rate, phi0, gamma, a, phase, ZT_start
- gamma=0, a=0 -> original 4-dial exactly (backward compatible)
- B = k0 / gamma  (Bending Number, Bastien, L=1)
- ZT = ZT_start + t  (absolute ZT, e.g. 9 for ZT9)

Tested: ZT9-1 RMSE 6.76 -> 3.20 (a=0.90 phase7.6 tau0.10), all 6 ZT9 improve 13-70%.
"""
from __future__ import annotations
import numpy as np

DEFAULT_DT = 1.0/60.0

def simulate(k0: float, tau: float, max_rate: float, phi_fn, t_end: float,
             dt: float = DEFAULT_DT, gamma: float = 0.0,
             a: float = 0.0, phase: float = 0.0, ZT_start: float = 0.0):
    n=int(round(t_end/dt)); times=np.linspace(0,n*dt,n+1)
    thetas=np.empty(n+1); theta,r=0.0,0.0; thetas[0]=theta
    for i in range(n):
        t=i*dt
        ZT=ZT_start + t
        k_eff=k0*(1 + a*np.cos(2*np.pi*(ZT - phase)/24))
        if k_eff<0.01: k_eff=0.01
        stimulus=k_eff*np.sin(np.deg2rad(phi_fn(t)-theta)) - gamma*theta
        r+=(stimulus - r)*(dt/tau)
        if r>max_rate: r=max_rate
        elif r< -max_rate: r=-max_rate
        theta+=r*dt
        thetas[i+1]=theta
    return times,thetas

def batch_simulate(k0, tau, max_rate, phi0, light_fn=None, t_end=24.0,
                   dt=DEFAULT_DT, record_dt=None, theta0=None, r0=None,
                   gamma=0.0, a=0.0, phase=0.0, ZT_start=0.0):
    k0=np.asarray(k0,float); tau=np.asarray(tau,float); max_rate=np.asarray(max_rate,float)
    phi0=np.asarray(phi0,float); gamma=np.asarray(gamma,float)
    a=np.asarray(a,float); phase=np.asarray(phase,float); ZT_start=np.asarray(ZT_start,float)
    # broadcast scalars
    n=len(k0)
    if gamma.size==1: gamma=np.full(n,float(gamma))
    if a.size==1: a=np.full(n,float(a))
    if phase.size==1: phase=np.full(n,float(phase))
    if ZT_start.size==1: ZT_start=np.full(n,float(ZT_start))
    if light_fn is None: light_fn=lambda t,p0: p0
    steps=int(round(t_end/dt)); rec=max(1,int(round(record_dt/dt))) if record_dt else 1
    thetas=np.empty((steps//rec+1, n))
    theta=np.zeros(n) if theta0 is None else np.array(theta0,float).copy()
    r=np.zeros(n) if r0 is None else np.array(r0,float).copy()
    thetas[0]=theta; j=1
    for i in range(steps):
        t=i*dt
        ZT=ZT_start + t
        k_eff=k0*(1 + a*np.cos(2*np.pi*(ZT - phase)/24))
        k_eff=np.maximum(k_eff,0.01)
        phi_rad=np.deg2rad(light_fn(t,phi0))
        theta_rad=np.deg2rad(theta)
        stimulus=k_eff*(np.sin(phi_rad)*np.cos(theta_rad)-np.cos(phi_rad)*np.sin(theta_rad)) - gamma*theta
        r+=(stimulus - r)*(dt/tau)
        np.clip(r,-max_rate,max_rate,out=r)
        theta+=r*dt
        if (i+1)%rec==0:
            thetas[j]=theta; j+=1
    times=np.arange(thetas.shape[0])*(dt*rec)
    return times,thetas

def batch_simulate_static(k0,tau,max_rate,phi0,t_end,dt=DEFAULT_DT,record_dt=None,gamma=0.0,a=0.0,phase=0.0,ZT_start=0.0):
    return batch_simulate(k0,tau,max_rate,phi0,None,t_end,dt,record_dt,gamma=gamma,a=a,phase=phase,ZT_start=ZT_start)

# helpers
def static_light(phi0): return lambda t: phi0
