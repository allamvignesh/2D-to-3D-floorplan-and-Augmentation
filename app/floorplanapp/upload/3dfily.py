import os, bpy, json, numpy as np

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

bpy.ops.outliner.orphans_purge()
bpy.ops.outliner.orphans_purge()
bpy.ops.outliner.orphans_purge()

def init_object(name):
    # Create new blender object and return references to mesh and object
    mymesh = bpy.data.meshes.new(name)
    myobject = bpy.data.objects.new(name, mymesh)
    bpy.context.collection.objects.link(myobject)
    return myobject, mymesh


def average(lst):
    return sum(lst) / len(lst)


def get_mesh_center(verts):
    # Calculate center location of a mesh from verts
    x = []
    y = []
    z = []

    for vert in verts:
        x.append(vert[0])
        y.append(vert[1])
        z.append(vert[2])

    return [average(x), average(y), average(z)]


def subtract_center_verts(verts1, verts2):
    # Remove verts1 from all verts in verts2, return result, verts1 & verts2 must have same shape!
    for i in range(0, len(verts2)):
        verts2[i][0] -= verts1[0]
        verts2[i][1] -= verts1[1]
        verts2[i][2] -= verts1[2]
    return verts2

def create_custom_mesh(objname, verts, faces, mat=None, cen=None):
    # Create mesh and object
    myobject, mymesh = init_object(objname)

    # Rearrange verts to put pivot point in center of mesh
    # Find center of verts
    center = get_mesh_center(verts)
    # Subtract center from verts before creation
    proper_verts = subtract_center_verts(center, verts)

    # Generate mesh data
    mymesh.from_pydata(proper_verts, [], faces)
    # Calculate the edges
    mymesh.update(calc_edges=True)

    parent_center = [int(cen[0] / 2), int(cen[1] / 2), int(cen[2])]

    # Move object to input verts location
    myobject.location.x = center[0] - parent_center[0]
    myobject.location.y = center[1] - parent_center[1]
    myobject.location.z = center[2] - parent_center[2]

    # add material
    if mat is None:  # add random color
        myobject.data.materials.append(
            create_mat(np.random.randint(0, 40, size=4))
        )  # add the material to the object
    else:
        myobject.data.materials.append(mat)  # add the material to the object
    return myobject

def create_mat(rgb_color):
    mat = bpy.data.materials.new(name="MaterialName")  # set new material to variable
    mat.diffuse_color = rgb_color  # change to random color
    return mat


parent, _ = init_object("Floorplan")

with open("..\\floorplanapp\\scans\\wall_horizontal_verts.txt", 'r') as f:
    verts = json.loads(f.read())
with open("..\\floorplanapp\\scans\\wall_horizontal_faces.txt", 'r') as f:
    faces = json.loads(f.read())

boxcount = 0
wallcount = 0
wall_parent, _ = init_object("Walls")

for i in range(0, len(verts)):
    roomname = "VertWalls" + str(i)
    obj = create_custom_mesh(
        roomname,
        verts[i],
        faces[i],
        cen=np.array([0, 0, 0]),
        mat=create_mat((0.5, 0.5, 0.5, 1)),
    )

bpy.ops.object.select_all(action='DESELECT')
        
for obj in bpy.data.objects:
    if "VertWalls" in obj.name:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
try:
    bpy.ops.object.mode_set(mode='EDIT')        
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 1), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "use_duplicated_keyframes":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)

    bpy.ops.object.mode_set(mode='OBJECT')

    num = 1
    while os.path.exists(os.path.join(f"..\\floorplanapp\\models\\model{num}.glb")):
        num += 1

    bpy.ops.export_scene.gltf(filepath=f"..\\floorplanapp\\models\\model{num}.gltf")
    bpy.ops.wm.quit_blender()
except:
    pass