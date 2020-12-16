import os
import vtk

import numpy as np
import nibabel as nib

from scipy.ndimage import zoom

""" Hexamesher Version 0.1

	Simple vtk wrapper for the generation of 8-noded hexahedral volume meshes based on binary segmentation masks.
	Input segmentation has to be in nifti format (.nii or .nii.gz).	
	Prior to generation of  hexahedrons the binary segmentation map can be interpolated to increase number of hexahedrons.

	12/2020, JZ

"""

class hexamesher():
	
	def __init__(self, input_path, output_path, zoom=1):
		# Initialize input and output path, load nii meta information and extract binary map.
		
		self.input_path  = input_path
		self.output_path = output_path
		
		self.nii_handle  = nib.load(input_path)
		self.header      = self.nii_handle.header 

		self.scale		 = [self.header['pixdim'][1], self.header['pixdim'][2], self.header['pixdim'][3]]
		self.offset 	 = [self.header['qoffset_x'], self.header['qoffset_y'], self.header['qoffset_z']]

		self.binmap      = np.array(self.nii_handle.dataobj).astype('int8')
		
		self.dvec        = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]]
		
		self.zoom        = zoom

	
	def mesh(self):
		
		if not self.zoom == 1:
			self.binmap = zoom(self.binmap, self.zoom, order=0)

		# Generate 8-noded hexahedral mesh.
		output = vtk.vtkUnstructuredGrid()		
		x_temp, y_temp, z_temp = self.binmap.nonzero()

		x = x_temp*self.scale[0] + self.offset[0]
		y = y_temp*self.scale[1] + self.offset[1]
		z = z_temp*self.scale[2] + self.offset[2]

		N = x.shape[0]
		
		I = 0 
		points = vtk.vtkPoints()		

		NodeLength = vtk.vtkDoubleArray()
		NodeLength.SetName('NodeLength')
		
		# Generate points and hexahedral elements.
		for i in range(0, N):
			for k in range(len(self.dvec)):
				points.InsertNextPoint(x[i]+self.dvec[k][0]/1, y[i]+self.dvec[k][1]/1, z[i]+self.dvec[k][2]/1)

			hex_ = vtk.vtkHexahedron()	
			
			for j in range(0, len(self.dvec)):
				hex_.GetPointIds().SetId(j, 8*I+j)
			
			NodeLength.InsertNextValue(1.0)
			output.InsertNextCell(hex_.GetCellType(), hex_.GetPointIds())
			I = I+1
		
		output.SetPoints(points)
		output.Scalars = NodeLength
		
		# Write output to file.
		writer = vtk.vtkXMLUnstructuredGridWriter()
		writer.SetFileName(self.output_path)
		writer.SetInputData(output)
		writer.Write()
