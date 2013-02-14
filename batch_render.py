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
    "version": (1,1),
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

# Container that keeps track of the settings used for this render batch
class BatchSettings(bpy.types.PropertyGroup):
    start_frame = bpy.props.IntProperty(name="Starting frame of this batch", default=0)
    end_frame = bpy.props.IntProperty(name="Ending frame of this batch", default=1)
    reso_x = bpy.props.IntProperty(name="X resolution", description="resoution of this batch", default=1920, min=1, max=10000, soft_min=1, soft_max=10000)
    reso_y = bpy.props.IntProperty(name="Y resoliution", description="resolution of this batch", default=1080, min=1, max=10000, soft_min=1, soft_max=10000)
    samples = IntProperty(name='Samples', description='Number of samples that is used (Cycles only)', min=1, max=1000000, soft_min=1, soft_max=100000, default=100)
    camera = StringProperty(name="Camera", description="Camera to be used for rendering this patch", default="")
    markedForDeletion = bpy.props.BoolProperty(name="Toggled on if this must be deleted", default=False)

# Container that records what frame ranges are to be rendered
class BatchRenderData(bpy.types.PropertyGroup):
    frame_ranges = bpy.props.CollectionProperty(name="Container for frame ranges defined for rendering", type=BatchSettings)
    active_range = bpy.props.IntProperty(name="Index for currently processed range", default=0)

class RenderButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

# Updates a list of objects used by a drop down menu
def updateObjectList():
    cameras = []
    for index, obj in enumerate(bpy.context.scene.objects):
        if (obj.type == 'CAMERA'):
            cameras.append((str(index), obj.name, str(index)))
    bpy.types.Scene.camera_list = EnumProperty(name="Cameras", description="asd", items=cameras, default='0')

# Box for selecting objects in a drop down menu
# Thanks to Peter Roelants
class CUSTOM_OT_SelectObjectButton(bpy.types.Operator):
    bl_idname = "batch_render.select_object"
    bl_label = "Select"
    bl_description = "Select the chosen object"

    def invoke(self, context, event):
        updateObjectList()
        obj = bpy.context.scene.objects[int(bpy.context.scene.camera_list)]
        for o in bpy.data.objects:
            print(o.name)
        #obj.selected = True
        bpy.context.scene.objects.active = obj
        return {'FINISHED'}

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
            layout.prop(it, 'start_frame', text="Start frame")
            layout.prop(it, 'end_frame', text="End frame")
            layout.prop(it, 'reso_x', text="Resolution X")
            layout.prop(it, 'reso_y', text="Resolution Y")
            layout.prop(it, 'samples', text="Samples (if using Cycles)")
            layout.prop(it, 'camera', text="Camera")
            layout.prop(bpy.context.scene, "camera_list", text="Objects")
            layout.operator("batch_render.select_object", "objects")
            layout.prop(it, 'markedForDeletion', text="Delete")
            layout.row()

# Operator that starts the rendering
class OBJECT_OT_BatchRenderButton(bpy.types.Operator):
    bl_idname = "batch_render.render"
    bl_label = "Batch Render"
    
    def execute(self, context):
        batcher = bpy.context.scene.batch_render
        sce = bpy.context.scene
        rd = sce.render
        for it in batcher.frame_ranges:
            if (it.end_frame <= it.start_frame):
                print("Skipped batch " + str(it.start_frame) + " - " + str(it.end_frame) + ": Start frame greater than end frame")
                continue
            if (rd.engine == 'CYCLES'):
                print("Rendering frames: " + str(it.start_frame) + " - " + str(it.end_frame) + " at resolution " + str(it.reso_x) + "x" + str(it.reso_y) + " with " + str(it.samples) + " samples")
            else:
                print("Rendering frames: " + str(it.start_frame) + " - " + str(it.end_frame) + " at resolution " + str(it.reso_x) + "x" + str(it.reso_y))
            sce.frame_start = it.start_frame
            sce.frame_end = it.end_frame
            rd.resolution_x = it.reso_x
            rd.resolution_y = it.reso_y

            # if a camera was specified
            if (it.camera != None):
                print("Camera was specified " + str(type(it.camera)))
                sce.camera = it.camera
            if (rd.engine == 'CYCLES'):
                sce.cycles.samples = it.samples
            bpy.ops.render.render(animation=True)
        sum = 0
        for it in batcher.frame_ranges:
            if (it.end_frame >= it.start_frame):
                sum += (it.end_frame - it.start_frame)
        print("Rendered " + str(len(batcher.frame_ranges)) + " batches containing " + str(sum) + " frames")
        return {'FINISHED'}

# Operator that adds a new frame range to be rendered
class OBJECT_OT_BatchRenderAddNew(bpy.types.Operator):
    bl_idname = "batch_render.add_new"
    bl_label = "Add new set"
    
    def execute(self, context):
        batcher = bpy.context.scene.batch_render
        rd = bpy.context.scene.render
        batcher.frame_ranges.add()
        last_item = len(batcher.frame_ranges)-1
        batcher.frame_ranges[last_item].start_frame = 1
        batcher.frame_ranges[last_item].end_frame = 2
        batcher.frame_ranges[last_item].samples = bpy.context.scene.cycles.samples
        batcher.frame_ranges[last_item].reso_x = rd.resolution_x
        batcher.frame_ranges[last_item].reso_y = rd.resolution_y
        
        return {'FINISHED'}

# Removes items that have been marked for deletion
class OBJECT_OT_BatchRenderRemove(bpy.types.Operator):
    bl_idname = "batch_render.remove"
    bl_label = "Remove selected sets"
    
    def execute(self, context):
        batcher = bpy.context.scene.batch_render

        done = False
        # Ugh, ugly O(n^2) operation here since it's hard to edit these collectionProperties...
        # Difficult to remove marked entries from lists when you can't delete while iterating,
        # and you can't make copies of the objects. Unless it's possible somehow. copy.deepcopy
        # does not work
        while (done == False):
            count = 0
            if (len(batcher.frame_ranges) < 1):
                break
            for it in batcher.frame_ranges:
                if (it.markedForDeletion == True):
                    batcher.frame_ranges.remove(count)
                    break
                count += 1
                if (count >= (len(batcher.frame_ranges)-1)):
                    done = True
        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.batch_render = PointerProperty(type=BatchRenderData, name='Batch Render', description='Settings used for batch rendering')
    updateObjectList()

def unregister():
    bpy.utils.unregister(__name__)

if __name__ == "__main__":
    register()


