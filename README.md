# Autocollision
Script to create collisions in Maya. Uses Maya muscles. Useful for rigs! Written in Python with PySide2 and PyMel.  
Based on Riham Toulan's script. http://www.rihamtoulan.com/blog/2018/3/24/faking-collisions-with-joints-based-setup-8snd2

To use:
1. Place autocollision directory in one of Maya's python script directories.
2. Launch the GUI by running the following:
```
import autocollision.mayadcc
autocollision.mayadcc.show()
```
3. Type in the name of the things you are trying to collide with at the top line edit bar.
4. Select controls to be driven by collision and press "Assign Controls" button.
5. Select geometry to drive collisions and press "Assign Geometry" button.
6. Select parent control (the transform that drives the controls previously selected) and press "Assign Parent Control" button.
7. Press "Create Collisions".

Move geometry around and watch the controls collide with the geometry!
