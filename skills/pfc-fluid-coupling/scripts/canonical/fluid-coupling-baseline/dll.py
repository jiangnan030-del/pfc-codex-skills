import numpy as np
import pylab as plt
import fipy as fp
import itasca as it
from itasca import ballarray as ba
from itasca import cfdarray as ca
from itasca import element
from functools import reduce

class DarcyFlowSolution(object):
    def __init__(self):
        self.mesh = fp.Grid3D(nx=10, ny=20, nz=10,
                              dx=0.01, dy=0.01, dz=0.01)
        self.pressure = fp.CellVariable(mesh=self.mesh,
                                        name='pressure', value=0.0)
        self.mobility = fp.CellVariable(mesh=self.mesh,
                                        name='mobility', value=0.0)
        self.pressure.equation = (fp.DiffusionTerm(coeff=self.mobility) == 0.0)
        self.mu = 1e-3  # dynamic viscosity
        self.inlet_mask = None
        self.outlet_mask = None
        # create the FiPy grid into the PFC CFD module
        ca.create_mesh(self.mesh.vertexCoords.T, self.mesh._cellVertexIDs.T[:,(0,2,3,1,4,6,7,5)].astype(np.int64))
        if it.ball.count() == 0:
            self.grain_size = 5e-4
        else:
            self.grain_size = 2*ba.radius().mean()

        it.command("""
        model configure cfd
        element cfd attribute density 1e3
        element cfd attribute viscosity {}
        cfd porosity polyhedron
        cfd interval 20
        """.format(self.mu))

    def set_pressure(self, value, where):
        """Dirichlet boundary condition. value is a pressure in Pa and where
        is a mask on the element faces."""
        print ("setting pressure to {} on {} faces".format(value, where.sum()))
        self.pressure.constrain(value, where)

    def set_inflow_rate(self, flow_rate):
        """
        Set inflow rate in m^3/s.  Flow is in the positive y direction and is specfified
        on the mesh faces given by the inlet_mask.
        """
        assert self.inlet_mask.sum()
        assert self.outlet_mask.sum()
        print ("setting inflow on %i faces" % (self.inlet_mask.sum()))
        print ("setting outflow on %i faces" % (self.outlet_mask.sum()))

        self.flow_rate = flow_rate
        self.inlet_area = (self.mesh.scaledFaceAreas*self.inlet_mask).sum()
        self.outlet_area = (self.mesh.scaledFaceAreas*self.outlet_mask).sum()
        self.Uin = flow_rate/self.inlet_area
        inlet_mobility = (self.mobility.faceValue * \
                              self.inlet_mask).sum()/(self.inlet_mask.sum()+0.0)
        self.pressure.faceGrad.constrain(
            ((0,),(-self.Uin/inlet_mobility,),(0,),), self.inlet_mask)

    def solve(self):
        """Solve the pressure equation and find the velocities."""
        self.pressure.equation.solve(var=self.pressure)
        # once we have the solution we write the values into the CFD elements
        ca.set_pressure(self.pressure.value)
        ca.set_pressure_gradient(self.pressure.grad.value.T)
        self.construct_cell_centered_velocity()

    def read_porosity(self):
        """Read the porosity from the PFC cfd elements and calculate a
        permeability."""
        porosity_limit = 0.7
        B = 1.0/180.0
        phi = ca.porosity()
        phi[phi>porosity_limit] = porosity_limit
        K = B*phi**3*self.grain_size**2/(1-phi)**2
        self.mobility.setValue(K/self.mu)
        ca.set_extra(1,self.mobility.value.T)

    def test_inflow_outflow(self):
        """Test continuity."""
        a = self.mobility.faceValue*np.array([np.dot(a,b) for a,b in
                                      zip(self.mesh.faceNormals.T,
                                          self.pressure.faceGrad.value.T)])
        self.inflow = (self.inlet_mask * a * self.mesh.scaledFaceAreas).sum()
        self.outflow = (self.outlet_mask * a * self.mesh.scaledFaceAreas).sum()
        print ("Inflow: {} outflow: {} tolerance: {}".format(
            self.inflow,  self.outflow,  self.inflow +  self.outflow))
        assert abs(self.inflow +  self.outflow) < 1e-6

    def construct_cell_centered_velocity(self):
        """The FiPy solver finds the velocity (fluxes) on the element faces,
        to calculate a drag force PFC needs an estimate of the
        velocity at the element centroids. """

        assert not self.mesh.cellFaceIDs.mask
        efaces = self.mesh.cellFaceIDs.data.T
        fvel = -(self.mesh.faceNormals*\
                 self.mobility.faceValue.value*np.array([np.dot(a,b) \
                 for a,b in zip(self.mesh.faceNormals.T, \
                               self.pressure.faceGrad.value.T)])).T
        def max_mag(a,b):
            if abs(a) > abs(b): return a
            else: return b
        for i, el in enumerate(element.cfd.list()):
            xmax, ymax, zmax = fvel[efaces[i][0]][0], fvel[efaces[i][0]][1],\
                               fvel[efaces[i][0]][2]
            for face in efaces[i]:
                xv,yv,zv = fvel[face]
                xmax = max_mag(xv, xmax)
                ymax = max_mag(yv, ymax)
                zmax = max_mag(zv, zmax)
            el.set_vel((xmax, ymax, zmax))

if __name__ == '__main__':  
    it.command("call 'particles.dat'")
    solver = DarcyFlowSolution()
    fx,fy,fz = solver.mesh.faceCenters
    # set boundary conditions
    solver.inlet_mask = fy == 0
    solver.outlet_mask = reduce(np.logical_and,(fy==0.2, fx<0.06, fx>0.04, fz>0.04, fz<0.06))
    #solver.set_inflow_rate(1e-5)
    solver.set_pressure(0.03, solver.inlet_mask)
    solver.set_pressure(0.0, solver.outlet_mask)

    solver.read_porosity()
    solver.solve()
    solver.test_inflow_outflow()
    it.command("cfd update")

    flow_solve_interval = 100
    def update_flow(*args):
        if it.cycle() % flow_solve_interval == 0:
            solver.read_porosity()
            solver.solve()
            solver.test_inflow_outflow()

    it.set_callback("update_flow",1)

    it.command("""
    model cycle 200
    model save 'end'
    """)