#!/usr/bin/env python3
"""Plot equal-area orientation density from SSF major-axis/contact vectors."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

p=argparse.ArgumentParser()
p.add_argument("csv")
p.add_argument("--columns",nargs=3,default=["nx","ny","nz"])
p.add_argument("--out",default="output/figures/orientation.png")
p.add_argument("--bins",type=int,default=36)
a=p.parse_args()
v=pd.read_csv(a.csv)[a.columns].to_numpy(float)
v=v/np.linalg.norm(v,axis=1)[:,None]
v[v[:,2]<0]*=-1
az=np.arctan2(v[:,1],v[:,0])
r=np.sqrt(2.0)*np.sin(0.5*np.arccos(np.clip(v[:,2],-1,1)))
x=r*np.cos(az); y=r*np.sin(az)
fig,ax=plt.subplots(figsize=(5,5))
h=ax.hist2d(x,y,bins=a.bins,cmap="viridis")
ax.set_aspect("equal"); ax.set_xlabel("equal-area x"); ax.set_ylabel("equal-area y")
fig.colorbar(h[3],ax=ax,label="count")
Path(a.out).parent.mkdir(parents=True,exist_ok=True)
fig.tight_layout(); fig.savefig(a.out,dpi=300)
