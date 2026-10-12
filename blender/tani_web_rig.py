# 웹(데스크톱)용 탄이: Sketchfab "Cat v1.0"(rhcreations, CC-BY-4.0) 모델에 뼈대를 새로 심어 GLB로 내보냄
# 원본 모델은 뼈대 위치(빈 노드)만 있고 몸에 연결(스키닝)이 안 되어 있어서, 그 위치로 뼈를 만들고 자동 가중치를 입힘.
# 실행: blender -b -P blender/tani_web_rig.py
import bpy, os, mathutils
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
SRC = os.path.join(WEB, "src", "scene.gltf")
OUT = os.path.join(WEB, "tani.glb")
REND = os.path.join(HERE, "renders")
os.makedirs(REND, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
scene = bpy.context.scene
vl = bpy.context.view_layer

body = next(o for o in bpy.data.objects if o.type == 'MESH' and o.data.materials[0].name == 'Main_Cat_Material')
eyes = next(o for o in bpy.data.objects if o.type == 'MESH' and o is not body)

# 부모(빈 노드)에서 떼어내고 변환을 메시에 적용
for o in (body, eyes):
    mw = o.matrix_world.copy()
    o.parent = None
    o.matrix_world = mw
for o in vl.objects:
    o.select_set(o in (body, eyes))
vl.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.data.objects):
    if o.type == 'EMPTY':
        bpy.data.objects.remove(o)
vl.update()
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
def deselect():
    for o in bpy.data.objects:
        if o.name in bpy.context.view_layer.objects:
            o.select_set(False)


body.name, eyes.name = "TaniBody", "TaniEyes"

# 겹친 정점 합치기(자동 가중치가 잘 붙도록) - 모양은 그대로
bm_me = body.data
import bmesh
bm = bmesh.new()
bm.from_mesh(bm_me)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
bm.to_mesh(bm_me)
bm.free()

# ---------- 뼈대 (원본 뼈 위치 기준, 고양이는 -Y 방향을 봄, Z 위) ----------
arm_data = bpy.data.armatures.new("TaniRig")
arm = bpy.data.objects.new("TaniRig", arm_data)
scene.collection.objects.link(arm)
deselect()
arm.select_set(True)
vl.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones


def bone(name, head, tail, parent=None, connect=False, deform=True):
    b = eb.new(name)
    b.head, b.tail = Vector(head), Vector(tail)
    b.roll = 0
    if parent:
        b.parent = eb[parent]
        b.use_connect = connect
    b.use_deform = deform
    return b


bone("hips", (0, 5.6, 10.4), (0, 1.1, 10.4))
bone("chest", (0, 1.1, 10.4), (0, -2.3, 9.6), "hips", True)
bone("neck", (0, -2.3, 9.6), (0, -4.5, 11.0), "chest", True)
bone("head", (0, -4.5, 11.0), (0, -6.8, 14.6), "neck", True)
bone("jaw", (0, -5.7, 12.4), (0, -7.4, 11.8), "head")
for s, side in ((1, "L"), (-1, "R")):
    bone("upperarm." + side, (s * 1.3, -2.2, 8.6), (s * 1.4, -3.4, 5.8), "chest")
    bone("forearm." + side, (s * 1.4, -3.4, 5.8), (s * 1.2, -4.0, 1.4), "upperarm." + side, True)
    bone("hand." + side, (s * 1.2, -4.0, 1.4), (s * 1.0, -5.6, 0.4), "forearm." + side, True)
    bone("thigh." + side, (s * 1.5, 5.2, 9.6), (s * 1.62, 7.1, 7.4), "hips")
    bone("shin." + side, (s * 1.62, 7.1, 7.4), (s * 1.46, 7.15, 3.0), "thigh." + side, True)
    bone("foot." + side, (s * 1.46, 7.15, 3.0), (s * 1.5, 5.6, 0.4), "shin." + side, True)
tail_pts = [(5.6, 10.5), (8.8, 11.7), (9.7, 14.7), (10.6, 17.2), (11.6, 19.0), (11.4, 22.0)]
prev = "hips"
for i in range(5):
    (y0, z0), (y1, z1) = tail_pts[i], tail_pts[i + 1]
    bone(f"tail{i + 1}", (0, y0, z0), (0, y1, z1), prev, i > 0)
    prev = f"tail{i + 1}"
bpy.ops.object.mode_set(mode='OBJECT')

# ---------- 몸에 뼈 입히기 (자동 가중치) ----------
deselect()
body.select_set(True)
arm.select_set(True)
vl.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
empty_groups = sum(1 for v in body.data.vertices if len(v.groups) == 0)
print("verts without weights:", empty_groups, "/", len(body.data.vertices))
if empty_groups > len(body.data.vertices) * 0.05:
    print("heat weighting failed -> envelope")
    body.modifiers.clear()
    body.vertex_groups.clear()
    body.select_set(True)
    bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')

# 눈은 머리뼈에 붙임 (원점을 두 눈의 가운데로 옮겨서 웹에서 세로로 줄이면 깜빡임)
deselect()
eyes.select_set(True)
vl.objects.active = eyes
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
mw = eyes.matrix_world.copy()
eyes.parent = arm
eyes.parent_type = 'BONE'
eyes.parent_bone = "head"
vl.update()
eyes.matrix_world = mw

# ---------- 형태 확인: 몇 가지 포즈로 렌더 ----------
sc = scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.color_type = 'TEXTURE'
sc.render.resolution_x, sc.render.resolution_y = 700, 600


def cam(n, loc, tgt, scale=30):
    cd = bpy.data.cameras.new(n)
    cd.type = 'ORTHO'
    cd.ortho_scale = scale
    ob = bpy.data.objects.new(n, cd)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


side = cam("side", (40, 3, 10), (0, 3, 10))
pb = arm.pose.bones
import math


def pose(name, rots):
    for b in pb:
        b.rotation_mode = 'XYZ'
        b.rotation_euler = (0, 0, 0)
    for k, v in rots.items():
        pb[k].rotation_euler = v
    vl.update()
    sc.camera = side
    sc.render.filepath = os.path.join(REND, f"rig_{name}.png")
    bpy.ops.render.render(write_still=True)


pose("rest", {})
pose("test", {"head": (0.5, 0, 0), "tail2": (0.6, 0, 0), "tail3": (0.5, 0, 0),
              "upperarm.L": (-0.7, 0, 0), "thigh.R": (0.6, 0, 0), "jaw": (0.4, 0, 0)})
for b in pb:
    b.rotation_euler = (0, 0, 0)

# ---------- 눈 색: 초록 -> 탄이 호박색 ----------
img = next((i for i in bpy.data.images if 'Eye' in i.name), None)
if img:
    px = list(img.pixels)
    for i in range(0, len(px), 4):
        r, g, b = px[i:i + 3]
        if g > r * 1.15 and g > b * 1.15:  # 초록 계열만
            v = g
            px[i], px[i + 1], px[i + 2] = min(1, v * 1.05), v * 0.62, v * 0.08
    img.pixels = px
    img.update()
    img.pack()

# ---------- 내보내기 ----------
for o in vl.objects:
    o.select_set(o in (body, eyes, arm))
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True,
                          export_skins=True, export_animations=False, export_yup=True,
                          export_image_format='JPEG', export_jpeg_quality=88)
print("exported", OUT, os.path.getsize(OUT))
