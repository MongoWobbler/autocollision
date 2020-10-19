from PySide2 import QtWidgets, QtCore


class DoubleButton(QtWidgets.QHBoxLayout):
    """
    Convenience class for creating two buttons next to each other
    """
    def __init__(self, left_name, left_function, right_name, right_function):
        super(DoubleButton, self).__init__()
        left_button = QtWidgets.QPushButton(left_name)
        left_button.clicked.connect(left_function)
        self.addWidget(left_button)

        right_button = QtWidgets.QPushButton(right_name)
        right_button.clicked.connect(right_function)
        self.addWidget(right_button)


class GUI(QtWidgets.QDialog):
    """
    GUI for user to input variables for auto collision
    """
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent=parent)
        self.setWindowTitle('Auto Collider')
        self.empty_controls_text = 'Select controls and press "Assign Controls" button.'
        self.empty_geometry_text = 'Select geometry to collide with and press "Assign Geometry" button.'
        self.module_name = None
        self.controls_list = None
        self.parent_control = None
        self.create_offset_checkbox = None
        self.create_blend_checkbox = None
        self.collision_source = None
        self.geometry_list = None
        self.geometry_parent = None
        self.is_geometry_driven_checkbox = None
        self.line_edit_stylesheet = None
        self.list_stylesheet = None
        self.build()

    def build(self):
        """
        Builds the GUI.
        """
        # layouts
        main_layout = QtWidgets.QVBoxLayout(self)
        name_layout = QtWidgets.QHBoxLayout()
        controls_layout = QtWidgets.QVBoxLayout()
        parent_control_text_layout = QtWidgets.QHBoxLayout()
        parent_control_layout = QtWidgets.QVBoxLayout()
        geometry_layout = QtWidgets.QVBoxLayout()
        parent_geometry_text_layout = QtWidgets.QHBoxLayout()
        parent_geometry_layout = QtWidgets.QVBoxLayout()
        source_layout = QtWidgets.QVBoxLayout()
        source_text_layout = QtWidgets.QHBoxLayout()

        # module name line edit
        self.module_name = QtWidgets.QLineEdit()
        self.module_name.setPlaceholderText('The name of the collision module')
        self.line_edit_stylesheet = self.module_name.styleSheet()
        self.module_name.textEdited.connect(self.resetNameStylesheet)
        name_layout.addWidget(self.module_name)

        # reset button
        reset_button = QtWidgets.QPushButton('Reset')
        reset_button.clicked.connect(self.reset)
        name_layout.addWidget(reset_button)

        # controls label
        controls_label = QtWidgets.QLabel('Controls')
        controls_layout.addWidget(controls_label)

        # controls list
        self.controls_list = QtWidgets.QListWidget()
        self.controls_list.addItem(self.empty_controls_text)
        self.list_stylesheet = self.controls_list.styleSheet()
        self.controls_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        controls_layout.addWidget(self.controls_list)

        # assign controls button
        controls_button = QtWidgets.QPushButton('Assign Controls')
        controls_button.clicked.connect(self.assignControls)
        controls_layout.addWidget(controls_button)

        # parent control
        self.parent_control = QtWidgets.QLineEdit()
        self.parent_control.setReadOnly(True)
        self.parent_control.setPlaceholderText('The control or joint that drives the given controls')
        parent_control_text_layout.addWidget(self.parent_control)

        # assign parent control button
        parent_control_button = QtWidgets.QPushButton('Assign Parent Control')
        parent_control_button.clicked.connect(self.assignParentControl)
        parent_control_text_layout.addWidget(parent_control_button)
        parent_control_layout.addLayout(parent_control_text_layout)

        # create offset checkbox
        self.create_offset_checkbox = QtWidgets.QCheckBox('Create Offset')
        self.create_offset_checkbox.setChecked(True)
        parent_control_layout.addWidget(self.create_offset_checkbox)

        # create blend attribute checkbox
        self.create_blend_checkbox = QtWidgets.QCheckBox('Create Blend Attribute')
        self.create_blend_checkbox.setChecked(True)
        parent_control_layout.addWidget(self.create_blend_checkbox)

        # geometry label
        geometry_label = QtWidgets.QLabel('Geometry')
        geometry_layout.addWidget(geometry_label)

        # geometry list
        self.geometry_list = QtWidgets.QListWidget()
        self.geometry_list.addItem(self.empty_geometry_text)
        self.geometry_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        geometry_layout.addWidget(self.geometry_list)

        # geometry button
        geometry_button = QtWidgets.QPushButton('Assign Geometry')
        geometry_button.clicked.connect(self.assignGeometry)
        geometry_layout.addWidget(geometry_button)

        # geometry parent
        self.geometry_parent = QtWidgets.QLineEdit()
        self.geometry_parent.setReadOnly(True)
        self.geometry_parent.setPlaceholderText('(OPTIONAL) The transform that drives the geometry')
        parent_geometry_text_layout.addWidget(self.geometry_parent)

        # geometry parent button
        geometry_parent_button = QtWidgets.QPushButton('Assign Parent Geometry')
        geometry_parent_button.clicked.connect(self.assignParentGeometry)
        parent_geometry_text_layout.addWidget(geometry_parent_button)
        geometry_layout.addLayout(parent_geometry_text_layout)

        # is geometry driven checkbox
        self.is_geometry_driven_checkbox = QtWidgets.QCheckBox('Drive Geometry')
        self.is_geometry_driven_checkbox.setChecked(True)
        geometry_layout.addWidget(self.is_geometry_driven_checkbox)

        # collision source point
        self.collision_source = QtWidgets.QLineEdit()
        self.collision_source.setReadOnly(True)
        self.collision_source.setPlaceholderText('(OPTIONAL): The point where all collisions go away from. Will use parent control as collision source if not specified')
        source_text_layout.addWidget(self.collision_source)

        # source button
        source_button = QtWidgets.QPushButton('Assign Collision Source')
        source_button.clicked.connect(self.assignCollisionSource)
        source_text_layout.addWidget(source_button)
        source_layout.addLayout(source_text_layout)

        # create collisions button
        create_collisions_button = QtWidgets.QPushButton('Create Collisions')
        create_collisions_button.clicked.connect(self.createCollisions)
        source_layout.addWidget(create_collisions_button)

        # controls splitter
        controls_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        controls_top = QtWidgets.QWidget()
        controls_top.setLayout(controls_layout)
        controls_bottom = QtWidgets.QWidget()
        controls_bottom.setLayout(parent_control_layout)
        controls_splitter.addWidget(controls_top)
        controls_splitter.addWidget(controls_bottom)

        # geometry_splitter
        geometry_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        geometry_top = QtWidgets.QWidget()
        geometry_top.setLayout(geometry_layout)
        geometry_bottom = QtWidgets.QWidget()
        geometry_bottom.setLayout(parent_geometry_layout)
        geometry_splitter.addWidget(geometry_top)
        geometry_splitter.addWidget(geometry_bottom)

        # horizontal splitter
        horizontal_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        horizontal_splitter.addWidget(controls_splitter)
        horizontal_splitter.addWidget(geometry_splitter)

        # vertical splitter and finishing layout
        vertical_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        collision_source_widget = QtWidgets.QWidget()
        collision_source_widget.setLayout(source_layout)
        vertical_splitter.addWidget(horizontal_splitter)
        vertical_splitter.addWidget(collision_source_widget)
        main_layout.addLayout(name_layout)
        main_layout.addWidget(vertical_splitter)

    def reset(self):
        """
        Sets all of the variables/widgets back to the default.
        """
        self.module_name.setText('')
        self.resetNameStylesheet()
        self.resetControls(force=True)
        self.parent_control.setText('')
        self.parent_control.setStyleSheet(self.line_edit_stylesheet)
        self.create_offset_checkbox.setChecked(True)
        self.create_blend_checkbox.setChecked(True)
        self.resetGeometry(force=True)
        self.geometry_parent.setText('')
        self.is_geometry_driven_checkbox.setChecked(True)
        self.collision_source.setText('')

    def resetNameStylesheet(self):
        """
        Sets the name stylesheet to default in case it gets turned red by user error.
        """
        self.module_name.setStyleSheet(self.line_edit_stylesheet)

    @staticmethod
    def failed(widget):
        """
        Sets given widget's stylesheet to red and returns False.

        Args:
            widget (QWidget): Widget to set stylesheet of.

        Returns:
            (Boolean): False
        """
        widget.setStyleSheet('color: red')
        return False

    @staticmethod
    def getItems(widget, text=False):
        """
        Convenience method for getting the items of a QListWidget.

        Args:
            widget (QListWidget): List widget to get items from.

            text (boolean): Whether we should get the item as a string instead of a QListWidgetItem.

        Returns:
            (list): List of items in given widget
        """
        if text:
            return [widget.item(i).text() for i in range(widget.count())]
        else:
            return [widget.item(i) for i in range(widget.count())]

    def validate(self):
        """
        Checks whether all required fields have valid variables.

        Returns:
            (boolean): True if everything is valid, false if missing variables.
        """
        name_check = True if self.module_name.text() else self.failed(self.module_name)
        controls_list_check = True if self.getItems(self.controls_list)[0].text() != self.empty_controls_text else self.failed(self.controls_list)
        parent_control_check = True if self.parent_control.text() else self.failed(self.parent_control)
        geometry_list_check = True if self.getItems(self.geometry_list)[0].text() != self.empty_geometry_text else self.failed(self.geometry_list)

        return name_check and controls_list_check and parent_control_check and geometry_list_check

    def resetControls(self, force=False):
        """
        Resets the control list if there is nothing in it or forced.

        Args:
            force (boolean): If True, will reset regardless of items in it.
        """
        if force or self.controls_list.count() == 0:
            self.controls_list.clear()
            self.controls_list.addItem(self.empty_controls_text)
            self.controls_list.setStyleSheet(self.list_stylesheet)

    def resetGeometry(self, force=False):
        """
        Resets the geometry list if there is nothing in it or forced.

        Args:
            force (boolean): If True, will reset regardless of items in it.
        """
        if force or self.geometry_list.count() == 0:
            self.geometry_list.clear()
            self.geometry_list.addItem(self.empty_geometry_text)
            self.geometry_list.setStyleSheet(self.list_stylesheet)

    def assignControls(self):
        """
        App dependent
        """
        self.controls_list.setStyleSheet(self.list_stylesheet)

    def assignParentControl(self):
        """
        App dependent
        """
        self.parent_control.setStyleSheet(self.line_edit_stylesheet)

    def assignGeometry(self):
        """
        App dependent
        """
        self.geometry_list.setStyleSheet(self.list_stylesheet)

    def assignParentGeometry(self):
        """
        App dependent
        """
        pass

    def assignCollisionSource(self):
        """
        App dependent
        """
        pass

    def createCollisions(self):
        """
        Performs a validate and then creates collisions. This function must be overwritten in DCC.
        """
        success = self.validate()

        if not success:
            raise ValueError('Validation failed, please take a look at GUI to see what is missing.')
