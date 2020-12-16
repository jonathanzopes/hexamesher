import numpy as np
import nibabel as nib

from hexamesher import *

def sphere(shape, radius, position):
    # Implementation from https://stackoverflow.com/questions/46626267
    semisizes = (radius, ) * 3
    
    grid = [slice(-x0, dim - x0) for x0, dim in zip(position, shape)]
    position = np.ogrid[grid]
    
    arr = np.zeros(shape, dtype=float)
    
    for x_i, semisize in zip(position, semisizes):
        arr += (x_i/semisize)**2
        
    arr = (arr<=1.0).astype('int8')
    
    #arr = np.array(arr).astype('int8')    
    
    return arr
    
if __name__ == '__main__':
    
    infile_name  = 'sphere.nii.gz'
    outfile_name = 'out.vtu'
    
    # Generate example hexahedron mesh of sphere.
    
    print('Generating example sphere... ')
    
    shape    = (128, 128, 128)
    radius   = 40
    position = (64, 64, 64)
    
    data = sphere(shape, radius, position)
    
    nii_file = nib.Nifti1Image(data, affine=np.eye(4))
    
    nib.save(nii_file, infile_name)
    
    # Use hexamesher.
    
    print('Running mesher...')
    
    hm =  hexamesher(infile_name, outfile_name, zoom=1)
    
    hm.mesh()
    
