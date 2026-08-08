#!/usr/bin/env python3
"""Post-process SSF named histories and append auditable case results."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd


def half_amplitude(x):
    x=np.asarray(x,float)
    return 0.5*(np.nanmax(x)-np.nanmin(x))


def g0_and_damping(loop):
    ds=half_amplitude(loop["deviator_stress"])
    ga=half_amplitude(loop["shear_strain"])
    if ga <= 0: raise ValueError("non-positive shear-strain amplitude")
    g0=ds/ga
    x=loop["shear_strain"].to_numpy(float)
    y=loop["deviator_stress"].to_numpy(float)
    area=abs(np.trapz(y,x))
    stored=0.5*ds*ga
    damping=area/(4*np.pi*stored) if stored > 0 else np.nan
    return g0,damping


def fabric_metrics(normals):
    n=np.asarray(normals,float); n=n/np.linalg.norm(n,axis=1)[:,None]
    rij=np.einsum("ni,nj->ij",n,n)/len(n)
    aij=7.5*(rij-np.eye(3)/3.0)
    ad=np.sqrt(1.5*np.sum(aij*aij))
    return rij,aij,float(ad)


def mechanical_z(contact_counts, nc):
    c=np.asarray(contact_counts,int); n0=np.sum(c==0); n1=np.sum(c==1)
    den=len(c)-n1-n0
    return float((2*nc-n1)/den) if den > 0 else np.nan


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--loop",required=True)
    p.add_argument("--contacts")
    p.add_argument("--out",default="output/summary.json")
    a=p.parse_args()
    loop=pd.read_csv(a.loop)
    g0,damping=g0_and_damping(loop)
    result={"G0_Pa":g0,"damping":damping}
    if a.contacts:
        c=pd.read_csv(a.contacts)
        rij,aij,ad=fabric_metrics(c[["nx","ny","nz"]])
        result.update(Rij=rij.tolist(),aij=aij.tolist(),ad=ad)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
