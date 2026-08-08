"""PFC + FiPy one-way (fluid -> solid) Darcy seepage coupling.

PFC's built-in CFD module computes porosity on polyhedral elements. FiPy solves the steady pressure
diffusion equation on the same grid, permeability/mobility are derived from porosity, and pressure,
pressure gradient and cell-centred velocity are written back to the PFC elements.

    div(lambda * grad p) = 0,      lambda = K / mu
    K = B * phi**3 * d**2 / (1 - phi)**2        (Kozeny-Carman type, B = 1/180)
    U_in = Q / A_in,               dp/dn|_in = -U_in / lambda_in

Case-specific assets: `particles.p3dat`, the 10x20x10 grid, inlet/outlet masks, grain size and flow
rate. Requires numpy and fipy. Verify command syntax for your PFC version.
"""

from functools import reduce      # Python 3: reduce is not a builtin

import numpy as np
import pylab as plt               # noqa: F401  (kept for interactive plotting)
import fipy as fp
import itasca as it
from itasca import ballarray as ba
from itasca import cfdarray as ca
from itasca.element import cfd


class DarcyFlowSolution(object):
    def __init__(self):
        self.mesh = fp.Grid3D(nx=10, ny=20, nz=10,
                              dx=0.01, dy=0.01, dz=0.01)
        self.pressure = fp.CellVariable(mesh=self.mesh, name='pressure', value=0.0)
        self.mobility = fp.CellVariable(mesh=self.mesh, name='mobility', value=0.0)
        # steady pressure diffusion: div(mobility * grad p) = 0
        self.pressure.equation = (fp.DiffusionTerm(coeff=self.mobility) == 0.0)
        self.mu = 1e-3
        self.inlet_mask = None
        self.outlet_mask = None
        # hand the FiPy mesh to PFC CFD; vertices are reordered to PFC element convention
        ca.create_mesh(self.mesh.vertexCoords.T,
                       self.mesh._cellVertexIDs.T[:, (0, 2, 3, 1, 4, 6, 7, 5)].astype(np.int64))
        if it.ball.count() == 0:
            self.grain_size = 5e-4
        else:
            self.grain_size = 2 * ba.radius().mean()
        it.command("""
        configure cfd
        element cfd attribute density 1e3
        element cfd attribute viscosity {}
        cfd porosity polyhedron
        cfd interval 20
        """.format(self.mu))

    def set_pressure(self, value, where):
        print("setting pressure to {} on {} faces".format(value, where.sum()))
        self.pressure.constrain(value, where)

    def set_inflow_rate(self, flow_rate):
        assert self.inlet_mask.sum()
        assert self.outlet_mask.sum()
        print("setting inflow on %i faces" % (self.inlet_mask.sum()))
        print("setting outflow on %i faces" % (self.outlet_mask.sum()))
        self.flow_rate = flow_rate
        self.inlet_area = (self.mesh.scaledFaceAreas * self.inlet_mask).sum()
        self.outlet_area = (self.mesh.scaledFaceAreas * self.outlet_mask).sum()
        self.Uin = flow_rate / self.inlet_area
        inlet_mobility = (self.mobility.getFaceValue() * self.inlet_mask).sum() \
            / (self.inlet_mask.sum() + 0.0)
        self.pressure.faceGrad.constrain(
            ((0,), (-self.Uin / inlet_mobility,), (0,),), self.inlet_mask)

    def solve(self):
        self.pressure.equation.solve(var=self.pressure)
        ca.set_pressure(self.pressure.value)
        ca.set_pressure_gradient(self.pressure.grad.value.T)
        self.construct_cell_centered_velocity()

    def read_porosity(self):
        porosity_limit = 0.7
        B = 1.0 / 180.0
        phi = ca.porosity()
        phi[phi > porosity_limit] = porosity_limit
        K = B * phi**3 * self.grain_size**2 / (1 - phi)**2
        self.mobility.setValue(K / self.mu)
        ca.set_extra(1, self.mobility.value.T)

    def test_inflow_outflow(self):
        a = self.mobility.getFaceValue() * np.array([np.dot(u, v) for u, v in
            zip(self.mesh._faceNormals.T, self.pressure.getFaceGrad().value.T)])
        self.inflow = (self.inlet_mask * a * self.mesh.scaledFaceAreas).sum()
        self.outflow = (self.outlet_mask * a * self.mesh.scaledFaceAreas).sum()
        print("Inflow: {} outflow: {} tolerance: {}".format(
            self.inflow, self.outflow, self.inflow + self.outflow))
        assert abs(self.inflow + self.outflow) < 1e-6

    def construct_cell_centered_velocity(self):
        assert not self.mesh.cellFaceIDs.mask
        efaces = self.mesh.cellFaceIDs.data.T
        fvel = -(self.mesh._faceNormals * self.mobility.faceValue.value
                 * np.array([np.dot(u, v)
                             for u, v in zip(self.mesh._faceNormals.T,
                                             self.pressure.faceGrad.value.T)]))

        def max_mag(a, b):
            if abs(a) > abs(b):
                return a
            return b

        for i, element in enumerate(cfd.list()):
            xmax, ymax, zmax = fvel[efaces[i][0]]
            for face in efaces[i]:
                xv, yv, zv = fvel[face]
                xmax = max_mag(xv, xmax)
                ymax = max_mag(yv, ymax)
                zmax = max_mag(zv, zmax)
            element.set_vel((xmax, ymax, zmax))


if __name__ == '__main__':
    it.command("call particles.p3dat")
    solver = DarcyFlowSolution()
    fx, fy, fz = solver.mesh.getFaceCenters()
    solver.inlet_mask = fy == 0
    solver.outlet_mask = reduce(np.logical_and,
                                (fy == 0.2, fx < 0.06, fx > 0.04, fz > 0.04, fz < 0.06))
    solver.set_inflow_rate(1e-5)
    solver.set_pressure(0.0, solver.outlet_mask)
    solver.read_porosity()
    solver.solve()
    solver.test_inflow_outflow()
    it.command("cfd update")

    flow_solve_interval = 100

    def update_flow(*args):
        """Re-solve the flow field every `flow_solve_interval` mechanical cycles."""
        if it.cycle() % flow_solve_interval == 0:
            solver.read_porosity()
            solver.solve()
            solver.test_inflow_outflow()

    it.set_callback("update_flow", 1)
    it.command("""
    cycle 20000
    save end
    """)
