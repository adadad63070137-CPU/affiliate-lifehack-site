"""CG試作：ローマ軍団の隊列（Blender / bpy）"""
import math
import random
import sys
import time

import bpy

OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "/tmp/legion.png"
ENGINE = sys.argv[sys.argv.index("--engine") + 1] if "--engine" in sys.argv else "CYCLES"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(name, rgb, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


RED = mat("red", (0.45, 0.04, 0.03))
GOLD = mat("gold", (0.8, 0.55, 0.15), 0.35, 1.0)
STEEL = mat("steel", (0.6, 0.6, 0.62), 0.3, 1.0)
SKIN = mat("skin", (0.55, 0.35, 0.25))
TUNIC = mat("tunic", (0.5, 0.08, 0.06))
WOOD = mat("wood", (0.25, 0.15, 0.07))
GRASS = mat("grass", (0.06, 0.09, 0.025), 0.95)
ARMOR = mat("armor", (0.35, 0.35, 0.37), 0.35, 1.0)
ROCK = mat("rock", (0.16, 0.14, 0.11), 0.9)
# 草地に色むら（ノイズ）
_n = GRASS.node_tree.nodes
_noise = _n.new("ShaderNodeTexNoise"); _noise.inputs["Scale"].default_value = 0.6
_ramp = _n.new("ShaderNodeValToRGB")
_ramp.color_ramp.elements[0].color = (0.035, 0.06, 0.015, 1); _ramp.color_ramp.elements[1].color = (0.13, 0.13, 0.04, 1)
GRASS.node_tree.links.new(_noise.outputs[0], _ramp.inputs[0])
GRASS.node_tree.links.new(_ramp.outputs["Color"], _n["Principled BSDF"].inputs["Base Color"])


def add(obj_fn, m, **kw):
    obj_fn(**kw)
    o = bpy.context.active_object
    o.data.materials.append(m)
    return o


def soldier(x, y):
    parts = []
    parts.append(add(bpy.ops.mesh.primitive_cube_add, TUNIC, size=1, location=(x, y, 0.8), scale=(0.23, 0.15, 0.2)))
    parts.append(add(bpy.ops.mesh.primitive_cylinder_add, ARMOR, vertices=12, radius=0.2, depth=0.42,
                     location=(x, y, 1.15), scale=(1.1, 0.8, 1)))
    parts.append(add(bpy.ops.mesh.primitive_cylinder_add, SKIN, vertices=10, radius=0.07, depth=0.7,
                     location=(x - 0.09, y, 0.35)))
    parts.append(add(bpy.ops.mesh.primitive_cylinder_add, SKIN, vertices=10, radius=0.07, depth=0.7,
                     location=(x + 0.09, y, 0.35)))
    parts.append(add(bpy.ops.mesh.primitive_uv_sphere_add, SKIN, segments=12, ring_count=8, radius=0.13,
                     location=(x, y, 1.5)))
    parts.append(add(bpy.ops.mesh.primitive_uv_sphere_add, STEEL, segments=12, ring_count=8, radius=0.15,
                     location=(x, y, 1.56), scale=(1, 1, 0.75)))
    parts.append(add(bpy.ops.mesh.primitive_cube_add, RED, size=1, location=(x, y - 0.06, 1.62), scale=(0.03, 0.2, 0.06)))
    sh = add(bpy.ops.mesh.primitive_cylinder_add, RED, vertices=24, radius=0.5, depth=1.1, end_fill_type="NOTHING",
             location=(x - 0.05, y + 0.18, 0.95), scale=(0.7, 1, 1))
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.object.mode_set(mode="OBJECT")
    for v in sh.data.vertices:
        if v.co.y > -0.38:
            v.co.y = -0.38 - (v.co.y + 0.38) * 0.0
    sh.modifiers.new("s", "SOLIDIFY").thickness = 0.03
    parts.append(sh)
    parts.append(add(bpy.ops.mesh.primitive_uv_sphere_add, GOLD, segments=10, ring_count=6, radius=0.06,
                     location=(x - 0.05, y - 0.3, 0.95)))
    parts.append(add(bpy.ops.mesh.primitive_cylinder_add, WOOD, vertices=6, radius=0.015, depth=2.0,
                     location=(x + 0.25, y - 0.1, 1.2)))
    return parts


random.seed(2)
for r in range(6):
    for c in range(14):
        soldier(c * 0.8 + random.uniform(-0.05, 0.05), r * 1.0 + random.uniform(-0.05, 0.05))

# 地面（起伏）
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
g = bpy.context.active_object
g.data.materials.append(GRASS)
bpy.ops.object.modifier_add(type="SUBSURF")
g.modifiers[0].subdivision_type = "SIMPLE"
g.modifiers[0].levels = 6
g.modifiers[0].render_levels = 6
tex = bpy.data.textures.new("n", "CLOUDS")
tex.noise_scale = 18
bpy.ops.object.modifier_add(type="DISPLACE")
g.modifiers[1].texture = tex
g.modifiers[1].strength = 2.5

# 鷲の旗（アクイラ）
add(bpy.ops.mesh.primitive_cylinder_add, WOOD, vertices=8, radius=0.03, depth=3.2, location=(5.6, -1.2, 1.6))
add(bpy.ops.mesh.primitive_cube_add, RED, size=1, location=(5.6, -1.2, 2.8), scale=(0.35, 0.02, 0.45))
add(bpy.ops.mesh.primitive_uv_sphere_add, GOLD, radius=0.18, location=(5.6, -1.2, 3.35))

# 光と空
sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 3.2
sun.angle = math.radians(3)
so = bpy.data.objects.new("sun", sun)
so.rotation_euler = (math.radians(72), 0, math.radians(-60))
sc.collection.objects.link(so)
w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
nt = w.node_tree
sky = nt.nodes.new("ShaderNodeTexSky")
sky.sky_type = "MULTIPLE_SCATTERING"
sky.sun_elevation = math.radians(14)
sky.sun_rotation = math.radians(150)
nt.links.new(sky.outputs[0], nt.nodes["Background"].inputs[0])
nt.nodes["Background"].inputs[1].default_value = 0.35

cam = bpy.data.cameras.new("cam")
cam.lens = 32
co = bpy.data.objects.new("cam", cam)
sc.collection.objects.link(co)
sc.camera = co
co.location = (-4.5, -9.0, 2.6)
co.rotation_euler = (math.radians(80), 0, math.radians(-28))

sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = 50
if ENGINE == "CYCLES":
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
else:
    sc.render.engine = ENGINE
sc.view_settings.view_transform = "AgX"
try:
    sc.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass
sc.view_settings.exposure = -0.6
sc.render.filepath = OUT
t = time.time()
bpy.ops.render.render(write_still=True)
print("RENDER_SECONDS", round(time.time() - t, 1))
