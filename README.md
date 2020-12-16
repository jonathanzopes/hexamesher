# hexamesher
Simple vtk wrapper for the generation of 8-noded hexahedral volume meshes based on binary segmentation masks.

- Input segmentation has to be in nifti format (.nii or .nii.gz).	
- Prior to generation of  hexahedrons the binary segmentation map can be interpolated to increase number of hexahedrons.

- Output mesh of the demo file (demo.py):

<img src="https://github.com/jonathanzopes/hexamesher/blob/main/assets/Sphere.png" width="400" height="366">

- Requirements: vtk, numpy, nibabel, scipy.
