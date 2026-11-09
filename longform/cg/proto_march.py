"""CG試作：行進するローマ軍団（3秒）。usage: python proto_march.py --out DIR [--still]"""
import math
import os
import random
import sys
import time

import bpy

OUT = sys.argv[sys.argv.index("--out") + 1]
STILL = "--still" in sys.argv
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 72


def mat(name, rgb, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


RED = mat("red", (0.22, 0.012, 0.01), 0.5)
GOLD = mat("gold", (0.8, 0.55, 0.15), 0.35, 1.0)
STEEL = mat("steel", (0.55, 0.55, 0.58), 0.28, 1.0)
ARMOR = mat("armor", (0.32, 0.32, 0.34), 0.35, 1.0)
SKIN = mat("skin", (0.3, 0.17, 0.11))
TUNIC = mat("tunic", (0.3, 0.03, 0.02))
WOOD = mat("wood", (0.2, 0.12, 0.05))
GRASS = mat("grass", (0.05, 0.08, 0.02), 0.95)
_n = GRASS.node_tree.nodes
_noise = _n.new("ShaderNodeTexNoise")
_noise.inputs["Scale"].default_value = 0.35
_ramp = _n.new("ShaderNodeValToRGB")
_ramp.color_ramp.elements[0].color = (0.03, 0.05, 0.012, 1)
_ramp.color_ramp.elements[1].color = (0.11, 0.1, 0.035, 1)
GRASS.node_tree.links.new(_noise.outputs[0], _ramp.inputs[0])
GRASS.node_tree.links.new(_ramp.outputs[0], _n["Principled BSDF"].inputs["Base Color"])


def prim(fn, m, **kw):
    fn(**kw)
    o = bpy.context.active_object
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def curved_shield(m, w_ang=0.62, r=0.55, h=1.05, cx=-0.05, cy=-0.24, cz=0.98, t=0.03):
    """湾曲した長方形の盾（スクトゥム）を頂点から作る"""
    import bmesh
    me = bpy.data.meshes.new("shield")
    bm = bmesh.new()
    n = 12
    rows = []
    for k, rr in enumerate((r, r - t)):
        ring = []
        for i in range(n + 1):
            a = -w_ang / 2 + w_ang * i / n
            x, y = math.sin(a) * rr, -math.cos(a) * rr + r
            ring.append((bm.verts.new((cx + x, cy + y, cz - h / 2)), bm.verts.new((cx + x, cy + y, cz + h / 2))))
        rows.append(ring)
    for ring in rows:
        for i in range(n):
            bm.faces.new((ring[i][0], ring[i + 1][0], ring[i + 1][1], ring[i][1]))
    o_, i_ = rows
    for i in range(n):
        bm.faces.new((o_[i][1], o_[i + 1][1], i_[i + 1][1], i_[i][1]))
        bm.faces.new((o_[i][0], i_[i][0], i_[i + 1][0], o_[i + 1][0]))
    for j in (0, n):
        bm.faces.new((o_[j][0], o_[j][1], i_[j][1], i_[j][0]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("shield", me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m)
    return o


def join(objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    return bpy.context.active_object


def make_soldier_template():
    """胴体（盾・兜・槍込み）と脚を作り、隠しておいて複製元にする"""
    body = [
        prim(bpy.ops.mesh.primitive_cube_add, TUNIC, size=1, location=(0, 0, 0.82), scale=(0.23, 0.15, 0.2)),
        prim(bpy.ops.mesh.primitive_cylinder_add, ARMOR, vertices=16, radius=0.2, depth=0.42, location=(0, 0, 1.15),
             scale=(1.1, 0.8, 1)),
        prim(bpy.ops.mesh.primitive_uv_sphere_add, SKIN, segments=16, ring_count=10, radius=0.12, location=(0, 0, 1.5)),
        prim(bpy.ops.mesh.primitive_uv_sphere_add, STEEL, segments=16, ring_count=10, radius=0.145,
             location=(0, 0.01, 1.56), scale=(1, 1, 0.78)),
        prim(bpy.ops.mesh.primitive_cube_add, RED, size=1, location=(0, 0.02, 1.7), scale=(0.025, 0.16, 0.05)),
        prim(bpy.ops.mesh.primitive_cylinder_add, WOOD, vertices=6, radius=0.015, depth=2.0, location=(0.27, 0.05, 1.2)),
        prim(bpy.ops.mesh.primitive_cone_add, STEEL, vertices=6, radius1=0.03, depth=0.18, location=(0.27, 0.05, 2.28)),
    ]
    sh = curved_shield(RED)
    boss = prim(bpy.ops.mesh.primitive_uv_sphere_add, GOLD, segments=12, ring_count=8, radius=0.07,
                location=(-0.05, -0.23, 0.98))
    b = join(body + [sh, boss])
    legs = []
    for dx in (-0.09, 0.09):
        lg = prim(bpy.ops.mesh.primitive_cylinder_add, SKIN, vertices=10, radius=0.065, depth=0.72,
                  location=(dx, 0, 0.36))
        bpy.context.scene.cursor.location = (dx, 0, 0.72)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        legs.append(lg)
    for o in [b] + legs:
        o.hide_render = True
        o.hide_set(True)
    return b, legs


BODY, LEGS = make_soldier_template()
army = bpy.data.objects.new("army", None)
sc.collection.objects.link(army)
random.seed(4)
for r in range(6):
    for c in range(12):
        x, y = c * 0.85 + random.uniform(-0.05, 0.05), r * 1.0 + random.uniform(-0.05, 0.05)
        ph = random.uniform(-0.25, 0.25)
        root = bpy.data.objects.new("s", None)
        sc.collection.objects.link(root)
        root.parent = army
        root.location = (x, y, 0)
        d = root.driver_add("location", 2).driver
        d.expression = f"abs(sin(frame*0.26+{ph:.2f}))*0.05"
        bo = BODY.copy()
        bo.hide_render = False
        sc.collection.objects.link(bo)
        bo.parent = root
        bo.location = (0, 0, 0)
        for i, L in enumerate(LEGS):
            lo = L.copy()
            lo.hide_render = False
            sc.collection.objects.link(lo)
            lo.parent = root
            lo.location = L.location.copy()
            dd = lo.driver_add("rotation_euler", 0).driver
            dd.expression = f"sin(frame*0.26+{ph:.2f}+{i * 3.14159:.3f})*0.45"
army.rotation_euler = (0, 0, math.radians(90))  # 隊列が +x 方向へ進む
army.location = (0, -2.5, 0)
army.keyframe_insert("location", frame=1)
army.location = (3.6, -2.5, 0)
army.keyframe_insert("location", frame=72)
for fc in (army.animation_data.action.fcurves if hasattr(army.animation_data.action, "fcurves") else []):
    for k in fc.keyframe_points:
        k.interpolation = "LINEAR"

# 地面
bpy.ops.mesh.primitive_plane_add(size=300)
g = bpy.context.active_object
g.data.materials.append(GRASS)
sub = g.modifiers.new("sub", "SUBSURF")
sub.subdivision_type = "SIMPLE"
sub.levels = sub.render_levels = 7
tex = bpy.data.textures.new("n", "CLOUDS")
tex.noise_scale = 25
dsp = g.modifiers.new("d", "DISPLACE")
dsp.texture = tex
dsp.strength = 3.0
dsp.mid_level = 0.6
bpy.ops.object.shade_smooth()

# 鷲の旗（隊列の先頭）
for o, loc in [(prim(bpy.ops.mesh.primitive_cylinder_add, WOOD, vertices=8, radius=0.03, depth=3.2), (4.7, -1.0, 1.6)),
               (prim(bpy.ops.mesh.primitive_cube_add, RED, size=1, scale=(0.4, 0.02, 0.5)), (4.7, -1.0, 2.75)),
               (prim(bpy.ops.mesh.primitive_uv_sphere_add, GOLD, radius=0.18), (4.7, -1.0, 3.35))]:
    o.parent = army
    o.location = loc

sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 3.0
sun.angle = math.radians(2)
so = bpy.data.objects.new("sun", sun)
so.rotation_euler = (math.radians(74), 0, math.radians(-120))
sc.collection.objects.link(so)
w = bpy.data.worlds.new("w")
sc.world = w
nt = w.node_tree
sky = nt.nodes.new("ShaderNodeTexSky")
sky.sky_type = "MULTIPLE_SCATTERING"
sky.sun_elevation = math.radians(16)
sky.sun_rotation = math.radians(210)
nt.links.new(sky.outputs[0], nt.nodes["Background"].inputs[0])
nt.nodes["Background"].inputs[1].default_value = 0.3

cam = bpy.data.cameras.new("cam")
cam.lens = 35
co = bpy.data.objects.new("cam", cam)
sc.collection.objects.link(co)
sc.camera = co
co.rotation_euler = (math.radians(82), 0, math.radians(-18))
co.location = (-3.0, -11.5, 2.2)
co.keyframe_insert("location", frame=1)
co.location = (0.5, -11.0, 2.4)
co.keyframe_insert("location", frame=72)

sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = 50
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 16
sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
sc.view_settings.exposure = -0.5
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = os.path.join(OUT, "f_")
t = time.time()
if STILL:
    sc.frame_set(36)
    sc.render.filepath = os.path.join(OUT, "still.png")
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("RENDER_SECONDS", round(time.time() - t, 1))
