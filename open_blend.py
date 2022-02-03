from sys import path
import bpy
import math
import time
import configparser
import os
path_ini = "conf.ini"
config = configparser.ConfigParser()
config.read(path_ini)
ifc_path = ''
try:
    ifc_path = config.get("BIM", "path_out_ifc")
except Exception:
    print('No output path in BIM')
else:
    ifc2obj = ifc_path.rsplit('/', 1)
    print(ifc2obj)
    temp_path = os.path.basename(ifc_path)
    temp_path = temp_path.rsplit('.', 1)
    ifc2obj[0] += '/' + temp_path[0] + '.obj'
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Camera'].select_set(True)
    bpy.data.objects['Light'].select_set(True)
    bpy.data.objects['Cube'].select_set(True)
    bpy.ops.object.delete()
    bpy.ops.import_scene.obj(filepath=ifc2obj[0])
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_all(action='SELECT')
    ov=bpy.context.copy()
    ov['area']=[a for a in bpy.context.screen.areas if a.type=="VIEW_3D"][0]
    bpy.ops.transform.rotate(ov,value=math.radians(90), orient_axis='X', orient_type='GLOBAL')