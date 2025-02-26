import numpy as np

import bpy
from bpy.props import FloatProperty, EnumProperty, BoolProperty, IntProperty, FloatVectorProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, zip_long_repeat, ensure_nesting_level, get_data_nesting_level
from sverchok.utils.field.scalar import SvScalarField
from sverchok.utils.dummy_nodes import add_dummy
from sverchok_extra.dependencies import sdf
from sverchok_extra.utils.sdf import *

if sdf is None:
    add_dummy('SvExSdfExtrudeNode', "SDF Extrude", 'sdf')

class SvExSdfExtrudeNode(bpy.types.Node, SverchCustomTreeNode):
    """
    Triggers: SDF Extrude
    Tooltip: SDF Extrude
    """
    bl_idname = 'SvExSdfExtrudeNode'
    bl_label = 'SDF Extrude'
    bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_EXTRUDE_REGION'

    height : FloatProperty(
            name = "Height",
            default = 1.0,
            update = updateNode)

    def sv_init(self, context):
        self.inputs.new('SvScalarFieldSocket', "SDF")
        self.inputs.new('SvStringsSocket', "Height").prop_name = 'height'
        self.outputs.new('SvScalarFieldSocket', "SDF")

    def process(self):
        if not any(socket.is_linked for socket in self.outputs):
            return

        sdf_s = self.inputs['SDF'].sv_get()
        height_s = self.inputs['Height'].sv_get()

        input_level = get_data_nesting_level(sdf1_s, data_types=(SvScalarField,))
        flat_output = input_level == 1
        sdf_s = ensure_nesting_level(sdf_s, 2, data_types=(SvScalarField,))
        height_s = ensure_nesting_level(height_s, 2)

        sdf_out = []
        for params in zip_long_repeat(sdf_s, height_s):
            new_sdf = []
            for sdf, height in zip_long_repeat(*params):
                sdf_2d = scalar_field_to_sdf_2d(sdf, 0)
                sdf = sdf_2d.extrude(height)
                field = SvExSdfScalarField(sdf)
                new_sdf.append(field)
            if flat_output:
                sdf_out.extend(new_sdf)
            else:
                sdf_out.append(new_sdf)

        self.outputs['SDF'].sv_set(sdf_out)

def register():
    if sdf is not None:
        bpy.utils.register_class(SvExSdfExtrudeNode)

def unregister():
    if sdf is not None:
        bpy.utils.unregister_class(SvExSdfExtrudeNode)

