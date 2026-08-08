"""itasca module basics: commands, ball/contact iteration, contact types, callbacks.

Reference example only. Verify command syntax for your PFC version before use.
Python 3 syntax (PFC 6.0+). On PFC 5.0 (Python 2.7) adapt print statements.
"""

import itasca


def build_cubic_packing():
    """Create a cubic packing of 8000 balls and report the radius sum."""
    itasca.command("""
    new
    domain extent -5e-2 6e-2 -6e-2 5e-2 -5e-2 5e-2
    cmat default model linear property kn 1e1 dp_nratio 0.2
    ball generate cubic box -0.02375 0.02375 rad 1.25e-3
    ball attr dens 2600
    """)
    print("ball count:", itasca.ball.count())

    ball = itasca.ball.find(1)
    print("ball 1 radius:", ball.radius())

    radius_sum = 0.0
    for b in itasca.ball.list():
        radius_sum += b.radius()
    print("radius sum:", radius_sum)
    return radius_sum


def inspect_contacts():
    """Cycle once so contacts exist, then inspect one ball's contacts."""
    itasca.command("cycle 1")
    b = itasca.ball.near((0, 0, 0))
    print("position:", b.pos(), "contacts:", len(b.contacts()))

    for c in b.contacts():
        print("contact with id: {} at {}".format(c.id(), c.pos()))

    c = b.contacts()[0]
    print("global force:", c.force_global())
    print("props:", c.props())
    print("fric:", c.prop('fric'))
    c.set_prop('fric', 0.5)

    neighbors = [c.end1() if c.end2() == b else c.end2() for c in b.contacts()]
    for i, neighbor in enumerate(neighbors):
        print("neighbor ball {} id: {}, position: {}".format(i, neighbor.id(), neighbor.pos()))
    return neighbors


def active_vs_virtual_contacts():
    """Three balls plus one wall: active vs virtual (inactive) contacts and their types."""
    from vec import vec

    itasca.command("""
    new
    domain extent -1 1 -1 1 -1 1
    cmat default model linear property kn 1e1 dp_nratio 0.2
    """)

    origin = vec((0.0, 0.0, 0.0))
    rad = 0.1
    eps = 0.001
    itasca.ball.create(rad, origin)
    itasca.ball.create(rad, origin + (rad - eps, 0, 0))
    # far enough away to produce a virtual (inactive) contact only
    itasca.ball.create(rad, origin + (rad * 3 + eps, 0, 0))

    itasca.command("""
    ball prop dens 1200
    wall create vertices ...
        -{rad} -{rad} -{rad} ...
         {rad} -{rad} -{rad} ...
         {rad}  {rad} -{rad}
    cycle 1
    """.format(rad=rad))

    print("active contacts:")
    for c in itasca.contact.list():
        print(" ", c)

    print("all contacts (including virtual):")
    for c in itasca.contact.list(all=True):
        print(" ", c, type(c))


def callback_demo():
    """Register a Python callback inside the solve loop, then unregister it."""
    state = {"count": 0}

    def my_callback(*args):
        state["count"] += 1

    itasca.set_callback("my_callback", -1)
    itasca.command("cycle 5")
    print("callback called {} times".format(state["count"]))

    itasca.remove_callback("my_callback", -1)
    state["count"] = 0
    itasca.command("cycle 5")
    print("callback called {} times after removal".format(state["count"]))


if __name__ == "__main__":
    build_cubic_packing()
    inspect_contacts()
    callback_demo()
