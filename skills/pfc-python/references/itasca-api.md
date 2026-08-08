# itasca module reference (Python inside PFC)

`import itasca` establishes the Python <-> PFC channel. There are two interaction layers:

1. **Submodule functions**: `itasca.ball.*`, `itasca.contact.*`, `itasca.clump.*` (e.g. `count`, `list`, `find`, `near`, `create`).
2. **Object methods**: methods on the returned objects (e.g. `ball.radius()`, `contact.prop()`).

Full member lists live in the PFC documentation files `itasca.ball.rst` and `itasca.ball.Ball.rst`.

## 1. Sending commands and querying

```py
import itasca

itasca.command("""
new
domain extent -5e-2 6e-2 -6e-2 5e-2 -5e-2 5e-2
cmat default model linear property kn 1e1 dp_nratio 0.2
ball generate cubic box -0.02375 0.02375 rad 1.25e-3
ball attr dens 2600
""")

itasca.ball.count()            # 8000
ball = itasca.ball.find(1)
ball.radius()                  # 0.00125

radius_sum = 0.0
for b in itasca.ball.list():
    radius_sum += b.radius()
print(radius_sum)              # 10.0 = 0.00125 * 8000
```

## 2. Accessing contacts

```py
itasca.command("cycle 1")          # cycle once so contacts exist
b = itasca.ball.near((0, 0, 0))
b.pos()                            # vec3((1.25e-03, 1.25e-03, 1.25e-03))
len(b.contacts())                  # 6 for cubic packing

c = b.contacts()[0]
c.force_global()                   # contact force in global axes
c.props()                          # {'kn': 10.0, 'fric': 0.0, 'emod': 5092.96, ...}
c.prop('fric')
c.set_prop('fric', 0.5)
c.end1(), c.end2()                 # the two contacting bodies

neighbors = [c.end1() if c.end2() == b else c.end2() for c in b.contacts()]
```

## 3. Type system: active vs virtual (inactive) contacts

`itasca.contact.list()` returns **active** contacts only; `itasca.contact.list(all=True)` also returns
virtual (inactive) contacts. Contact classes differ by type:

- ball-ball -> `itasca.BallBallContact`
- ball-wall facet -> `itasca.BallFacetContact` (a `facet` is a wall triangle element)

```py
c1, c2, c3, c4 = tuple(itasca.contact.list(all=True))
type(c1) is itasca.BallBallContact     # True
type(c3) is itasca.BallFacetContact    # True
```

## 4. Callbacks inside the solve loop

```py
i = 0
def my_callback(*args):
    global i
    i += 1

itasca.set_callback("my_callback", -1)
itasca.command("cycle 5")     # callback fires 5 times
itasca.remove_callback("my_callback", -1)
itasca.command("cycle 5")     # callback no longer fires
```

`order` selects the insertion point within the solve cycle (e.g. `-1`, `1`). This is the mechanism used
by the Darcy example to re-solve the flow field every N steps.

## 5. Bulk array exchange

```py
from itasca import ballarray as ba      # radius(), pos(), vel(), ...
from itasca import cfdarray as ca       # create_mesh(), porosity(), set_pressure(), set_extra(), ...
from itasca.element import cfd          # per-element access: element.set_vel(...)
```

Use these numpy-backed arrays for hundreds of thousands of particles; per-object Python loops are far slower.

## 6. Python language essentials used by the examples

- Types: `float`, `int`, `str` (single, double or triple quotes for multi-line).
- Collections: `list` (mutable, `[]`, `append`, slicing, negative indices), `tuple` (immutable),
  `dict` (key -> value, `del`).
- Functions: `def name(a, b): return a + b`.
- Control flow: `for` (like FISH `loop foreach`), `if / elif / else`, `while` with `break` / `continue`.
- Comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`.
- `import` for standard library and third-party packages (`pip install <name>`); adding the PFC install
  directory to PATH lets you practice Python from a plain command prompt without opening PFC.
