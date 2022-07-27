#import what we need
import os
from nilearn import plotting
import matplotlib.pyplot as plt
import nibabel as nib
from nilearn.maskers import NiftiMasker
from nilearn.interfaces.fmriprep import load_confounds
from nilearn import datasets
from nilearn.connectome import ConnectivityMeasure
import numpy as np
from nilearn import plotting
from nilearn.plotting import view_img
from nilearn.image.image import mean_img
from nilearn.plotting import plot_connectome

#create paths
a_path = "/Users/kevinjamey/nilearn_data/"
a_folder = "mtAsdRsfmri"
s13_file_4D = "sub-13_ses-02_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"

fmri_filepath = os.path.join(a_path, a_folder, s13_file_4D)

# path to Nifti file
print(fmri_filepath)

#load subject Nifti file with the nibabel library
fmri_img = nib.load(fmri_filepath)
print(fmri_img)

# get the data array 
fmri_data = fmri_img.get_fdata()
fmri_data.shape

#apply confounds mask
confounds_simple, sample_mask = load_confounds(
    fmri_filepath,
    strategy=["high_pass", "motion", "wm_csf"],
    motion="basic", wm_csf="basic")

print("The shape of the confounds matrix is:", confounds_simple.shape)
print(confounds_simple.columns)

masker = NiftiMasker()
time_series = masker.fit_transform(fmri_filepath,
                                   confounds=confounds_simple,
                                   sample_mask=sample_mask)

time_series.shape

#inverse mask
thresholded_masked_data = time_series * (time_series > time_series.mean())
thresholded_img = masker.inverse_transform(thresholded_masked_data)
plt.imshow(thresholded_img.get_fdata()[:,:,25,0], cmap='gray')

#get msdl atlas
atlas_dataset = datasets.fetch_atlas_msdl()
atlas_filepath = atlas_dataset.maps
labels = atlas_dataset.labels

#apply mask to atlas
from nilearn.maskers import NiftiMapsMasker

atlas_masker = NiftiMapsMasker(maps_img=atlas_filepath, standardize=True)
data_in_atlas = atlas_masker.fit_transform(fmri_filepath, confounds=confounds_simple,
                                   sample_mask=sample_mask)
data_in_atlas.shape

# Plot the correlation matrix
correlation_measure = ConnectivityMeasure(kind='correlation')
correlation_matrix = correlation_measure.fit_transform([data_in_atlas])[0]

# Make a large figure
# Mask the main diagonal for visualization:
np.fill_diagonal(correlation_matrix, 0)
# The matrix is reordered for block-like representation
plotting.plot_matrix(correlation_matrix, figure=(10, 8), labels=labels,
                     vmax=0.8, vmin=-0.8, reorder=True)
plt.savefig("cormat_post.pdf", format="pdf", bbox_inches="tight")

# Since our fmri_img is a 4D NiftiImage, we need to generate a 3D one.
# One way of doing that is averaging our volumes on the time axis 
# with the mean_img function.

fmri_img_mean = mean_img(fmri_img)
view_img(fmri_img_mean)

#create connectome
coords = atlas_dataset.region_coords

# We threshold to keep only the 10% of edges with the highest value
# because the graph is very dense
plotting.plot_connectome(correlation_matrix, coords,
                         edge_threshold="90%", colorbar=True)
plt.savefig("connectome90%_post.pdf", format="pdf", bbox_inches="tight")

view = plotting.view_connectome(correlation_matrix, coords, edge_threshold='90%')

# In a Jupyter notebook, if ``view`` is the output of a cell, it will
# be displayed below the cell
view

#seed-based connectivity

#make seed coordinates
#vis_coords = [(-16, -74, 7)]
pcc_coords = [(0, -52, 18)]

#make seed time series
from nilearn.maskers import NiftiSpheresMasker

seed_masker = NiftiSpheresMasker(
    pcc_coords, radius=10, detrend=True, standardize=True,
    low_pass=0.1, high_pass=0.01, t_r=2,
    memory='nilearn_cache', memory_level=1, verbose=0)

seed_time_series = seed_masker.fit_transform(fmri_filepath,
                                             confounds=confounds_simple,
                                   sample_mask=sample_mask)

#make brain time series
from nilearn.maskers import NiftiMasker

brain_masker = NiftiMasker(
    smoothing_fwhm=6, detrend=True, standardize=True,
    low_pass=0.1, high_pass=0.01, t_r=2,
    memory='nilearn_cache', memory_level=1, verbose=0)

brain_time_series = brain_masker.fit_transform(fmri_filepath,
                                               confounds=confounds_simple,
                                   sample_mask=sample_mask)

print("Seed time series shape: (%s, %s)" % seed_time_series.shape)
print("Brain time series shape: (%s, %s)" % brain_time_series.shape)

#seed to voxel correlation
import numpy as np

seed_to_voxel_correlations = (np.dot(brain_time_series.T, seed_time_series) /
                              seed_time_series.shape[0]
                              )

print("Seed-to-voxel correlation shape: (%s, %s)" %
      seed_to_voxel_correlations.shape)
print("Seed-to-voxel correlation: min = %.3f; max = %.3f" % (
    seed_to_voxel_correlations.min(), seed_to_voxel_correlations.max()))

#plots seed to voxel correlation
from nilearn import plotting

seed_to_voxel_correlations_img = brain_masker.inverse_transform(
    seed_to_voxel_correlations.T)
display = plotting.plot_stat_map(seed_to_voxel_correlations_img,
                                 threshold=0.5, vmax=1,
                                 cut_coords=pcc_coords[0],
                                 title="Seed-to-voxel correlation (PCC seed)"
                                 )
display.add_markers(marker_coords=pcc_coords, marker_color='g',
                    marker_size=300)
plt.savefig("pcc_seed_to_voxel_cor_post.pdf", format="pdf", bbox_inches="tight")

#seed_to_voxel_correlations_fisher_z transform
seed_to_voxel_correlations_fisher_z = np.arctanh(seed_to_voxel_correlations)
print("Seed-to-voxel correlation Fisher-z transformed: min = %.3f; max = %.3f"
      % (seed_to_voxel_correlations_fisher_z.min(),
         seed_to_voxel_correlations_fisher_z.max()
         )
      )

# Finally, we can transform the correlation array back to a Nifti image
# object, that we can save.
seed_to_voxel_correlations_fisher_z_img = brain_masker.inverse_transform(
    seed_to_voxel_correlations_fisher_z.T)
seed_to_voxel_correlations_fisher_z_img.to_filename(
    'pcc_seed_correlation_post_z.nii.gz')