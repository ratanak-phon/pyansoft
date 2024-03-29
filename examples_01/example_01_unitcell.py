# import library
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
from pyansoft import HFSS

hfss = HFSS(
    project_name="Passive_Metasurface",
    design_name="UnitCell",
    specified_version="2016.2",
)

""" Design Variables ============================= """
""" ============================================== """

hfss["p"] = "3.2 mm"
hfss["pz"] = "10 mm"
hfss["h"] = "0.125 mm"
hfss["rc"] = "1.5 mm"
hfss["w"] = "0.5 mm"
hfss["w1"] = "0.8 mm"
hfss["w2"] = "0.6 mm"
hfss["d"] = "1.3 mm"
hfss["alpha"] = "50 deg"
hfss["beta"] = "20 deg"


""" Create 3D Object ============================= """
""" ============================================== """
pla_color = "(0 128 255)"
kapton_color = "(128 64 64)"
silver_color = "(192 192 192)"
inkject_color = "(128 128 128)"


air_box = hfss.modeler.create_box(
    position=["-p/2", "-p/2", "-pz/2-(h+d)"],
    size=["p", "p", "pz + 2*(h+d)"],
    name="AirBox",
    transparency=1
)

kapton = hfss.modeler.create_box(
    position=["-p/2", "-p/2", "0"],
    size=["p", "p", "h"],
    color=kapton_color,
    name="kapton"
)

# Top PLA
pla_t01 = hfss.modeler.create_box(
    position=["w2/2", "-p/2", "h"],
    size=["w1", "p", "d"],
    color=pla_color,
    name="pla_top_01",
    transparency=0.5
)

pla_t02 = hfss.modeler.create_box(
    position=["-w1-w2/2", "-p/2", "h"],
    size=["w1", "p", "d"],
    color=pla_color,
    name="pla_top_02",
    transparency=0.5
)

# Bottom PLA
pla_b01 = hfss.modeler.create_box(
    position=["-p/2", "w2/2", "-d"],
    size=["p", "w1", "d"],
    color=pla_color,
    name="pla_bottom_01",
    transparency=0.5
)

pla_b02 = hfss.modeler.create_box(
    position=["-p/2", "-w1-w2/2", "-d"],
    size=["p", "w1", "d"],
    color=pla_color,
    name="pla_bottom_02",
    transparency=0.5
)

""" Create 2D Object ============================= """
""" ============================================== """

ring = hfss.modeler.create_circle(
    center=["0", "0", "h"],
    radius="rc", name="ring",
    color=inkject_color
)

ring0 = hfss.modeler.create_circle(
    center=["0", "0", "h"],
    radius="rc-w", name="ring_in"
)

hfss.operator.subtract(blank_parts=ring, tool_parts=ring0)

rect = hfss.modeler.create_rectangle(
    position=["-w/2", "-rc+w/2", "h"],
    size=["w", "2*rc-w"], name="rect"
)

# Create 2D from polyline
l0 = hfss.modeler.create_center_point_arc(
    pl_point=[["p*cos(alpha/2)", "p*sin(alpha/2)", "h"]],
    arc_center=["0", "0", "h"],
    arc_angle="-alpha",
    name="line0"
)

l1 = hfss.modeler.create_line(
    pl_point=[["0", "0", "h"], ["p", "0", "h"]],
    name="line1"
)

l2 = hfss.modeler.create_line(
    pl_point=[["0", "0", "h"], ["p", "0", "h"]],
    name="line2"
)

hfss.operator.rotate(object_name=l1, rotate_angle="alpha/2")
hfss.operator.rotate(object_name=l2, rotate_angle="-alpha/2")
hfss.operator.move(object_name=l0, position=['w/2', 0, 0])
hfss.operator.move(object_name=l1, position=['w/2', 0, 0])
hfss.operator.move(object_name=l2, position=['w/2', 0, 0])

hfss.operator.unite(object_name=[l0, l1, l2])
hfss.operator.cover_line(l0)

l3 = hfss.operator.duplicate_around_axis(
    object_name=l0, rotation_angle="180deg")
hfss.operator.unite(object_name=[l0, l3])

# Make final ring shape
hfss.operator.subtract(blank_parts=ring, tool_parts=l0)
hfss.operator.unite(object_name=[ring, rect])
hfss.operator.rotate(object_name=ring, rotate_angle="beta")

""" Assign materials =================================================================== """
""" ==================================================================================== """

""" Periodic Boundary and Floquet Port ================================================= """
""" ==================================================================================== """

face_id = hfss.operator.get_face_id(air_box)

# Master1
vertex_m1 = hfss.operator.get_vertex_id_from_face(face_id[2])
origin_m1 = hfss.operator.get_vertex_position(vertex_m1[1])
u_pos_m1 = hfss.operator.get_vertex_position(vertex_m1[2])

hfss.boundary.master(
    origin=origin_m1,
    u_pos=u_pos_m1,
    name="Master1",
    reverse_v=True,
    face_id=face_id[2]
)

# Master2
vertex_m2 = hfss.operator.get_vertex_id_from_face(face_id[3])
origin_m2 = hfss.operator.get_vertex_position(vertex_m2[1])
u_pos_m2 = hfss.operator.get_vertex_position(vertex_m2[2])

hfss.boundary.master(
    origin=origin_m2,
    u_pos=u_pos_m2,
    name="Master2",
    reverse_v=True,
    face_id=face_id[3]
)

# Slave1
vertex_s1 = hfss.operator.get_vertex_id_from_face(face_id[4])
origin_s1 = hfss.operator.get_vertex_position(vertex_s1[2])
u_pos_s1 = hfss.operator.get_vertex_position(vertex_s1[1])

hfss.boundary.slave(
    origin=origin_s1,
    u_pos=u_pos_s1,
    name="Slave1",
    master="Master1",
    face_id=face_id[4]
)

# Slave2
vertex_s2 = hfss.operator.get_vertex_id_from_face(face_id[5])
origin_s2 = hfss.operator.get_vertex_position(vertex_s2[2])
u_pos_s2 = hfss.operator.get_vertex_position(vertex_s2[1])

hfss.boundary.slave(
    origin=origin_s2,
    u_pos=u_pos_s2,
    name="Slave2",
    master="Master2",
    face_id=face_id[5]
)

# Floquet Port1
vertex_p1 = hfss.operator.get_vertex_id_from_face(face_id[0])
A_vector = [
    hfss.operator.get_vertex_position(vertex_p1[3]),
    hfss.operator.get_vertex_position(vertex_p1[0])
]
B_vector = [
    hfss.operator.get_vertex_position(vertex_p1[3]),
    hfss.operator.get_vertex_position(vertex_p1[2])
]
hfss.excitation.floquet_port(
    A_vector=A_vector,
    B_vector=B_vector,
    name="FloquetPort1",
    deembed="pz/2",
    face_id=face_id[0]
)

# Floquet Port2
vertex_p1 = hfss.operator.get_vertex_id_from_face(face_id[1])
A_vector = [
    hfss.operator.get_vertex_position(vertex_p1[2]),
    hfss.operator.get_vertex_position(vertex_p1[1])
]
B_vector = [
    hfss.operator.get_vertex_position(vertex_p1[2]),
    hfss.operator.get_vertex_position(vertex_p1[3])
]
hfss.excitation.floquet_port(
    A_vector=A_vector,
    B_vector=B_vector,
    name="FloquetPort2",
    deembed="pz/2",
    face_id=face_id[1]
)

# Setup Analysis
hfss.analysis.solution_setup(
    solution_name="Setup1",
    frequency="10GHz",
    max_passes=10,
)

hfss.analysis.frequency_sweep(
    sweep_name="Sweep",
    freq_range=("5GHz", "15GHz", "0.01GHz"),
    setup_name="Setup1"
)
