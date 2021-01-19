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
		# Initialize all container elements for vtk.
		output = vtk.vtkUnstructuredGrid()
		points = vtk.vtkPoints()
		length = vtk.vtkDoubleArray()
		length.SetName('NodeLength')
		# Find all locations that need a mesh element.
		xs, ys, zs = self.binmap.nonzero()

		N = xs.shape[0]

		pos_id_dict = {}
		# Generate all required points and stored their pos_id in hashmap.
		for i in range(N):
			for k in range(len(self.dvec)):
				xi = xs[i]+self.dvec[k][0]
				yi = ys[i]+self.dvec[k][1]
				zi = zs[i]+self.dvec[k][2]

				if not (xi, yi, zi) in pos_id_dict:
					points.InsertNextPoint(xi, yi, zi)
					pos_id_dict[(xi, yi, zi)] = len(pos_id_dict)

		# Add all hexahedrons into the unstructured grid, by using points.
		num_ids = len(pos_id_dict)
		print(num_ids)
		for i in range(N):
			hex_ = vtk.vtkHexahedron()
			for j in range(len(self.dvec)):
				# Retrieve the correct id for the point.
				xi = xs[i]+self.dvec[j][0]
				yi = ys[i]+self.dvec[j][1]
				zi = zs[i]+self.dvec[j][2]
				curr_id = pos_id_dict[(xi, yi, zi)]
				# Set the id into the hexahedral element.
				hex_.GetPointIds().SetId(j, curr_id)
		
			length.InsertNextValue(1.0)
			output.InsertNextCell(hex_.GetCellType(), hex_.GetPointIds())

		# Write final output containers.
		output.SetPoints(points)
		output.Scalars = length

		# Write output.
		writer = vtk.vtkXMLUnstructuredGridWriter()
		writer.SetFileName(self.output_path)
		writer.SetInputData(output)
		writer.Write()
