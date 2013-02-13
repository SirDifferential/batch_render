# batch_render.py Copyright (C) 2013, Jesse Kaukonen
#
# Allows setting up a queue of renders to be executed in sequence
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Batch Render",
    "author": "Jesse Kaukonen",
    "version": (1,0),
    "blender": (2, 6, 5),
    "location": "Render > Render",
    "description": "Set up multiple render tasks to be executed in sequence",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Render"}

"""
Usage:


Launch from "Render > Render > Batch render"


Additional links:
    Author Site: www.jessekaukonen.net
    e-mail: jesse dot kaukonen at gmail dot com
"""

import bpy
from bpy.props import PointerProperty, StringProperty, BoolProperty, EnumProperty, IntProperty, CollectionProperty

class IntPair(bpy.types.PropertyGroup):
    value1 = bpy.props.IntProperty(name="First value of a pair", default=0)
    value2 = bpy.props.IntProperty(name="Second value of a pair", default=0)

class BatchRenderData(bpy.types.PropertyGroup):
    frame_ranges = bpy.props.CollectionProperty(name="Container for frame ranges defined for rendering", type=IntPair)
    number = bpy.props.IntProperty(name="Number of sequences to render", default=1)

#
# A panel in the render section of properties space
#
class BatchRenderPanel(bpy.types.Panel):
    bl_label = "Batch Render"
    bl_space_type= "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        batcher = bpy.context.scene.batch_render
        self.layout.operator("batch_render.render", text="Batch render")
        self.layout.operator("batch_render.add_new", text="Add new range")

import sys

class OBJECT_OT_BatchRenderButton(bpy.types.Operator):
    bl_idname = "batch_render.render"
    bl_label = "Batch Render"
    
    def execute(self, context):
        print("oioi")
        sys.stdout.flush()
        return {'FINISHED'}

class OBJECT_OT_BatchRenderAddNew(bpy.types.Operator):
    bl_idname = "batch_render.add_new"
    bl_label = "Add new range"
    
    def execute(self, context):
        print("aiai")
        sys.stdout.flush()
        batcher = bpy.context.scene.batch_render
        batcher.frame_ranges.add()
        batcher.frame_ranges[last_item].value1 = 1
        batcher.frame_ranges[last_item].value2 = 2
        
        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.batch_render = PointerProperty(type=BatchRenderData, name='Batch Render', description='Settings used for batch rendering')

def unregister():
    bpy.utils.unregister(__name__)

if __name__ == "__main__":
    register()


