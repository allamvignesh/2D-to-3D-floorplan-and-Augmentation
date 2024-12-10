import bpy
import bmesh
import json
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
    
bpy.ops.outliner.orphans_purge()
bpy.ops.outliner.orphans_purge()
bpy.ops.outliner.orphans_purge()

obj_name = "house_plan"

mesh_data = bpy.data.meshes.new(f"{obj_name}_data")

mesh_obj = bpy.data.objects.new(obj_name, mesh_data)

bpy.context.scene.collection.objects.link(mesh_obj)

bm = bmesh.new()

ifile = open("D:\Downloads\project\myfile.json",)
json_data = json.load(ifile)
ifile.close()

scale = 0.01
hor = 0

for wall in json_data["data"]["walls"]:
    a, b = wall["position"]
    try:
        theta = math.degrees(math.atan((b[1]-a[1])/(b[0]-a[0])))
    except ZeroDivisionError:
        theta = 90
    if theta > 45:
        hor = 0
    else:
        hor = 1  # horizontal
    
    a11 = bm.verts.new([a[0]*scale-0.1, a[1]*scale-(0.1*hor), 0])
    a12 = bm.verts.new([a[0]*scale+0.1*(not hor)-0.1*(hor), a[1]*scale+(0.1 * hor), 0])
    b11 = bm.verts.new([b[0]*scale-0.1*(not hor)+0.1*(hor), b[1]*scale-(0.1*hor), 0])
    b12 = bm.verts.new([b[0]*scale+0.1*(not hor)+0.1*(hor), b[1]*scale+(0.1 * hor), 0])
    
    a21 = bm.verts.new([a[0]*scale-0.1, a[1]*scale-(0.1*hor), 1])
    a22 = bm.verts.new([a[0]*scale+0.1*(not hor)-0.1*(hor), a[1]*scale+(0.1 * hor), 1])
    b21 = bm.verts.new([b[0]*scale-0.1*(not hor)+0.1*(hor), b[1]*scale-(0.1*hor), 1])
    b22 = bm.verts.new([b[0]*scale+0.1*(not hor)+0.1*(hor), b[1]*scale+(0.1 * hor), 1])
    
    
    if hor:
        bm.faces.new([a11, a12, b12, b11])  #bottom
        bm.faces.new([b21, b22, a22, a21])  #top
        bm.faces.new([a21, a22, a12, a11])  #left
        bm.faces.new([b11, b12, b22, b21])  #right
        bm.faces.new([b11, b21, a21, a11])  #front
        bm.faces.new([a12, a22, b22, b12])  #back
    else:
        bm.faces.new([b11, b12, a12, a11])  #bottom
        bm.faces.new([a21, a22, b22, b21])  #top
        bm.faces.new([a11, a12, a22, a21])  #front
        bm.faces.new([b21, b22, b12, b11])  #back
        bm.faces.new([a11, a21, b21, b11])  #left
        bm.faces.new([b12, b22, a22, a12])  #right

bm.to_mesh(mesh_data)
mesh_data.update()

bpy.data.objects[obj_name].select_set(True)
bpy.ops.export_scene.gltf(filepath="D:\Downloads\hello.gltf")