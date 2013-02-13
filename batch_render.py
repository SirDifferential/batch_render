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

# Pair<int,int> type since there isn't one by default 
class IntPair(bpy.types.PropertyGroup):
    value1 = bpy.props.IntProperty(name="First value of a pair", default=0)
    value2 = bpy.props.IntProperty(name="Second value of a pair", default=0)
    markedForDeletion = bpy.props.BoolProperty(name="Toggled on if this must be deleted", default=False)

# Container that records what frame ranges are to be rendered
class BatchRenderData(bpy.types.PropertyGroup):
    frame_ranges = bpy.props.CollectionProperty(name="Container for frame ranges defined for rendering", type=IntPair)
    active_range = bpy.props.IntProperty(name="Index for currently processed range", default=0)

class RenderButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

# A panel in the render section of properties space
class BatchRenderPanel(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Batch Render"

    def draw(self, context):
        layout = self.layout
        batcher = bpy.context.scene.batch_render
        layout.operator("batch_render.render", text="Launch rendering")
        layout.operator("batch_render.add_new", text="Add new set")
        layout.operator('batch_render.remove', text="Delete selected", icon='CANCEL')
        layout.row()
        count = 0
        # Print a control knob for every item currently defined
        for it in batcher.frame_ranges:
            count += 1
            layout.label(text="Batch " + str(count))
            layout.prop(it, 'value1', text="Start frame")
            layout.prop(it, 'value2', text="End frame")
            layout.prop(it, 'markedForDeletion', text="Delete")
            layout.row()

# Operator that starts the rendering
class OBJECT_OT_BatchRenderButton(bpy.types.Operator):
    bl_idname = "batch_render.render"
    bl_label = "Batch Render"
    
    def execute(self, context):
        batcher = bpy.context.scene.batch_render
        sce = bpy.context.scene
        for it in batcher.frame_ranges:
            if (it.value2 <= it.value1):
                print("Skipped batch " + str(it.value1) + " - " + str(it.value2) + ": Start frame greater than end frame")
                continue
            print("Rendering frames: " + str(it.value1) + " - " + str(it.value2))
            sce.frame_start = it.value1
            sce.frame_end = it.value2
            bpy.ops.render.render(animation=True)
        sum = 0
        for it in batcher.frame_ranges:
            sum += (it.value2 - it.value1)
        print("Rendered " + str(len(batcher.frame_ranges)) + " batches containing " + str(sum) + " frames")
        return {'FINISHED'}

# Operator that adds a new frame range to be rendered
class OBJECT_OT_BatchRenderAddNew(bpy.types.Operator):
    bl_idname = "batch_render.add_new"
    bl_label = "Add new set"
    
    def execute(self, context):
        batcher = bpy.context.scene.batch_render
        batcher.frame_ranges.add()
        last_item = len(batcher.frame_ranges)-1
        batcher.frame_ranges[last_item].value1 = 1
        batcher.frame_ranges[last_item].value2 = 2
        
        return {'FINISHED'}

class OBJECT_OT_BatchRenderRemove(bpy.types.Operator):
    bl_idname = "batch_render.remove"
    bl_label = "Remove selected sets"
    
    def execute(self, context):
        batcher = bpy.context.scene.batch_render
        i = 0
        for it in batcher.frame_ranges:
            if (it.markedForDeletion == True):
                batcher.frame_ranges.remove(i)
            i += 1
        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.batch_render = PointerProperty(type=BatchRenderData, name='Batch Render', description='Settings used for batch rendering')

def unregister():
    bpy.utils.unregister(__name__)

if __name__ == "__main__":
    register()


