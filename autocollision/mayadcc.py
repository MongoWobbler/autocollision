from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets
import pymel.core as pm
import agnostic


# check to see if Maya Muscle is loaded
required_plugin = 'MayaMuscle.mll'
pm.loadPlugin(required_plugin, quiet=True)
if not pm.pluginInfo(required_plugin, loaded=True, q=True):
    pm.error(required_plugin + ' is not loaded! Please load it.')


def create(name, controls, parent_control, collision_geometry, geometry_parent=None, collision_source=None, create_offset=True, create_blender=True, is_geometry_driven=True):
    """
    Creates the collision nodes at the given control's position, with given parent control driving them and given collision geometry colliding with them.

    Args:
        name (string): Name to add to groups to differentiate.

        controls (list): Controls that will be driven by collision.

        parent_control (string): Name of the transform that will drive all our of collisions so they stay in the right space.

        collision_geometry (list): All the transforms of the meshes that will collide with our given controls.

        geometry_parent (string): OPTIONAL. The name of the transform that will drive the given collision geometry so they stay in the right space.

        collision_source (string): OPTIONAL. The name of the transform for the point in space to figure out collision direction. If none given, will use parent_control as collision source.

        create_offset (bool): If True, will create an offset transform group above each control to be driven by the collision and drive the control.

        create_blender (bool): If True, will create a blender node and attribute for each control to blend between using collision or not.

        is_geometry_driven (bool): If True, will set up constraints for the given collision geometry.

    Returns:
        (list): Nodes created.
    """
    # error checking
    if not controls:
        pm.error('Please specify controls')

    if not collision_geometry:
        pm.error('Please specify collision geometry')

    if not parent_control:
        pm.error('Please specify parent control')

    # created holds all nodes created, clear selection just in case
    # find the position of our collision source and turn it into a vector for vector math
    created = []
    pm.select(cl=True)
    collision_node = collision_source if collision_source else parent_control
    collision_source_translation = pm.xform(collision_node, q=True, worldSpace=True, translation=True)
    collision_source_translation = pm.datatypes.Vector(collision_source_translation)

    # muscles group will hold all our nodes, this would usually go in the extras category of a rig
    muscles_group = pm.group(n=name + '_muscles_master_grp', em=True)
    scale_constraint = pm.scaleConstraint(parent_control, muscles_group, mo=False)
    created.append(scale_constraint)
    created.append(muscles_group)
    
    # makes collision geometry a muscle
    for geometry in collision_geometry:
        pm.select(geometry)
        pm.mel.eval('cMuscle_makeMuscle(0);')

    # iterate over all the controls and make collisions for each
    for control in controls:

        # create a group and locator at our control's location
        # group is the one that is going to be driven by collision
        # locator will drive our controls
        control = pm.PyNode(control)
        control_name = control.nodeName()
        control_translation = pm.xform(control, q=True, worldSpace=True, translation=True)
        control_translation = pm.datatypes.Vector(control_translation)
        control_rotation = pm.xform(control, q=True, worldSpace=True, rotation=True)
        group = pm.group(em=True, n=control_name + '_muscle_grp')
        locator = pm.spaceLocator(n=control_name + '_muscle_locator')
        created.append(group)
        created.append(locator)

        # set location of group to our control
        group.t.set(control_translation)
        group.r.set(control_rotation)

        # parent locator to group, and group to master muscles group
        pm.parent(locator, group)
        pm.parent(group, muscles_group)

        # setting locator to local 0 will move it to the control's location
        locator.t.set(0, 0, 0)
        locator.r.set(0, 0, 0)

        # must have nodes selected for that mel command
        pm.select(group)
        muscle_nodes = pm.mel.eval('cMuscle_rigKeepOutSel();')
        muscle_node = pm.PyNode(muscle_nodes[1])
        created += muscle_nodes

        # get the direction the muscles should move when they collide with the collision geometry
        direction = pm.datatypes.Vector(control_translation - collision_source_translation)
        direction.normalize()

        # setting that direction
        muscle_node.inDirectionX.set(direction.x)
        muscle_node.inDirectionY.set(direction.y)
        muscle_node.inDirectionZ.set(direction.z)

        # making the connection between the muscles and the collision geometry
        pm.select(group)
        pm.select(collision_geometry, add=True)
        pm.mel.eval('cMuscle_keepOutAddRemMuscle(1);')

        if create_offset:
            # if create offset, make a group that will be driven by the muscle collision
            # that will then drive the given controls
            offset = pm.group(n=control_name + '_collision_offset', em=True)
            offset.t.set(control_translation)
            pm.parent(offset, control.getParent())
            pm.parent(control, offset)
            point_constraint = pm.pointConstraint(locator, offset, mo=False)
            created.append(offset)
            created.append(point_constraint)

            if create_blender:
                # create attribute to connect to blender node
                pm.addAttr(control, ln='autoCollisionWeight', min=0, max=1, dv=1, hidden=False, keyable=True)

                # creates a blender attribute to blend between muscle collision and regular control position
                blend_node = pm.shadingNode('blendColors', n=offset + '_Blend_T_Collision', au=True)
                blend_node.color1.set((0, 0, 0))
                blend_node.color2.set((0, 0, 0))
                created.append(blend_node)

                # connect control attribute to blender
                control.autoCollisionWeight >> blend_node.blender
                point_constraint.constraintTranslate >> blend_node.color1

                # make sure to disconnect the point constraint from the offset
                # before hooking up the values from the blender
                offset.tx.disconnect()
                offset.ty.disconnect()
                offset.tz.disconnect()
                blend_node.output >> offset.t

        else:
            # if not creating a blender, drive the controls with a good ol' parent constraint
            parent_constraint = pm.parentConstraint(locator, control)
            created.append(parent_constraint)

    if is_geometry_driven:

        # if no geometry parent is driven, the parent control will drive our geometry then
        if not geometry_parent:
            geometry_parent = parent_control

        # create a group for all our collision geometry
        master_collision_group = pm.group(n=name + '_collision_grp', em=True)
        scale_constraint = pm.scaleConstraint(geometry_parent, master_collision_group, mo=False)
        created.append(master_collision_group)
        created.append(scale_constraint)

        for geometry in collision_geometry:
            # making an offset group so that we don't mess with the geometry's transform
            # parent constraining each geometry's offset group
            geometry = pm.PyNode(geometry)
            collision_group = pm.group(n=name + '_' + geometry.nodeName() + '_grp', em=True)
            collision_parent = pm.parentConstraint(geometry_parent, collision_group, mo=False)
            pm.parent(collision_group, master_collision_group)
            pm.parent(geometry, collision_group)
            created.append(collision_group)
            created.append(collision_parent)

    return created


class GUI(MayaQWidgetDockableMixin, agnostic.GUI):

    def __init__(self, parent=None):
        super(GUI, self).__init__(parent=parent)

    def assignControls(self):
        """
        Assigns the controls that will be driven by the collisions.
        """
        super(GUI, self).assignControls()
        self.controls_list.clear()
        [self.controls_list.addItem(QtWidgets.QListWidgetItem(node.nodeName())) for node in pm.selected()]
        self.resetControls()

    def assignParentControl(self):
        """
        Assigns the parent control that will drive all the collision nodes,
        """
        super(GUI, self).assignParentControl()
        selected = pm.selected()

        if not selected:
            self.parent_control.setText('')
            return

        parent_control = selected[-1].nodeName()
        if len(selected) > 1:
            pm.warning('More than one object selected, assigning ' + parent_control + ' as parent control')

        self.parent_control.setText(parent_control)

    def assignGeometry(self):
        """
        Assigns the geometries that will collide with our controls
        """
        super(GUI, self).assignGeometry()
        self.geometry_list.clear()
        [self.geometry_list.addItem(QtWidgets.QListWidgetItem(node.nodeName())) for node in pm.selected()]
        self.resetGeometry()

    def assignParentGeometry(self):
        """
        Assigns the transform in charge of driving our geometries
        """
        super(GUI, self).assignParentGeometry()
        selected = pm.selected()

        if not selected:
            self.geometry_parent.setText('')
            return

        geometry_parent = selected[-1].nodeName()
        if len(selected) > 1:
            pm.warning('More than one object selected, assigning ' + geometry_parent + ' as geometry parent')

        self.geometry_parent.setText(geometry_parent)

    def assignCollisionSource(self):
        """
        Assigns the transform from which the collision direction is derived from.
        """
        super(GUI, self).assignCollisionSource()
        selected = pm.selected()

        if not selected:
            self.collision_source.setText('')
            return

        collision_source = selected[-1].nodeName()
        if len(selected) > 1:
            pm.warning('More than one object selected, assigning ' + collision_source + ' as collision source')

        self.collision_source.setText(collision_source)

    def createCollisions(self):
        """
        Creates the auto collisions in Maya.

        Returns:
            (list): Nodes created.
        """
        super(GUI, self).createCollisions()

        nodes = create(
                       self.module_name.text(),
                       self.getItems(self.controls_list, text=True),
                       self.parent_control.text(),
                       self.getItems(self.geometry_list, text=True),
                       self.geometry_parent.text(),
                       self.collision_source.text(),
                       self.create_offset_checkbox.isChecked(),
                       self.create_blend_checkbox.isChecked(),
                       self.is_geometry_driven_checkbox.isChecked()
                       )

        return nodes


def show():
    """
    Convenience method for showing maya's auto collision GUI.
    """
    auto_collision_gui = GUI()
    auto_collision_gui.show(dockable=True)
    return auto_collision_gui
