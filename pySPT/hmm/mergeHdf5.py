"""
@author: Johanna Rahm
Research group Heilemann
Institute for Physical and Theoretical Chemistry, Goethe University Frankfurt a.M.

Merge information from archive files (from ermine) with matching *.h5 files (from SPTAnalyser trackAnalysis
or TrackStatistics) containing the *.trc information the ermine analysis is based on.
"""

import h5py
import numpy as np
from shutil import copyfile


class MergeHdf5():
    def __init__(self, hdf5_path, archive_path, save_path):
        self.archive_file = h5py.File(archive_path, "r")
        new_hdf5_file = copyfile(hdf5_path, save_path)
        self.hdf5_file = h5py.File(new_hdf5_file, "r+")
    
    def create_missing_groups(self):
        self.hdf5_file.create_group("judi")
        self.hdf5_file.create_group("physicalModel")
        self.hdf5_file.create_group("hmm")
        
    def trc_placeholder_to_state(self):
        hdf5_trc_group = self.hdf5_file["trc"]
        hdf5_trc_dataset = hdf5_trc_group["trcHmm"]
        archive_data_group = self.archive_file["data"]
        archive_molecules_dataset = archive_data_group["molecules"]
        shape = len(hdf5_trc_dataset)
        trc_new_values = []
        # old trcFile values are saved, except for placeholder column which is replaced by the state from archive file
        for i in range(len(hdf5_trc_dataset[0])):
            trc_new_values.append([])
            for j in range(len(hdf5_trc_dataset)):
                if i != 4:
                    trc_new_values[i].append(hdf5_trc_dataset[j][i])
                else:
                    trc_new_values[i].append(archive_molecules_dataset[j][i])
        del hdf5_trc_group["trcHmm"]
        dset = hdf5_trc_group.create_dataset("trcHmm", (shape,), dtype=np.dtype([("track id", int),
                                                                                 ("frame", int),
                                                                                 ("x position [\u03BCm]", float),
                                                                                 ("y position [\u03BCm]", float),
                                                                                 ("state", int),
                                                                                 ("intensity [photon]", float)]))
        dset["track id"] = trc_new_values[0]
        dset["frame"] = trc_new_values[1]
        dset["x position [\u03BCm]"] = trc_new_values[2]
        dset["y position [\u03BCm]"] = trc_new_values[3]
        dset["state"] = trc_new_values[4]
        dset["intensity [photon]"] = trc_new_values[5]
        
    def add_roi_dataset_to_settings(self):
        archive_settings_group = self.archive_file["settings"]
        archive_roi_dataset = archive_settings_group["roi"]
        roi_values = []
        shape = len(archive_roi_dataset)
        for i in range(len(archive_roi_dataset[0])):
            roi_values.append(archive_roi_dataset[0][i])
            if i < 4:
                roi_values[i] /= 1000
        
        hdf5_settings_group = self.hdf5_file["settings"]
        dset = hdf5_settings_group.create_dataset("roi", (shape,), dtype=np.dtype([("minX [\u03BCm]", float),
                                                                                   ("maxX [\u03BCm]", float),
                                                                                   ("minY [\u03BCm]", float),
                                                                                   ("maxY [\u03BCm]", float),
                                                                                   ("minT [frames]", float),
                                                                                   ("maxT [frames]", float),
                                                                                   ("minI [a.u.]", float),
                                                                                   ("maxI [a.u.]", float)]))
        dset["minX [\u03BCm]"] = roi_values[0]
        dset["maxX [\u03BCm]"] = roi_values[1]
        dset["minY [\u03BCm]"] = roi_values[2]
        dset["maxY [\u03BCm]"] = roi_values[3]
        dset["minT [frames]"] = roi_values[4]
        dset["maxT [frames]"] = roi_values[5]
        dset["minI [a.u.]"] = roi_values[6]
        dset["maxI [a.u.]"] = roi_values[7]
        
    def add_judi(self):
        archive_data_group = self.archive_file["data"]
        archive_judi_dataset = archive_data_group["judi"]
        judi_values = []
        shape = len(archive_judi_dataset)
        for i in range(len(archive_judi_dataset[0])):
            judi_values.append([])
            for j in range(len(archive_judi_dataset)):
                if i != 1:
                    judi_values[i].append(archive_judi_dataset[j][i])
                else:
                    judi_values[i].append(archive_judi_dataset[j][i]/1000)  # nm -> ym
        hdf5_judi_group = self.hdf5_file["judi"]
        
        dset = hdf5_judi_group.create_dataset("judiFile", (shape,), dtype=np.dtype([("trajectory id", int),
                                                                                    ("distance [\u03BCm]", float),
                                                                                    ("state", int)]))
        dset["trajectory id"] = judi_values[0]
        dset["distance [\u03BCm]"] = judi_values[1]
        dset["state"] = judi_values[2]
        
    def add_diffusion_coeff(self):
        archive_physical_model_group = self.archive_file["physical model"]
        archive_diffusion_dataset = archive_physical_model_group["diffusion coefficient"]        
        hdf5_physical_model_group = self.hdf5_file["physicalModel"]
        diffusion_values = []
        shape = np.shape(archive_diffusion_dataset)
        for i in range(len(archive_diffusion_dataset[0])):
            diffusion_values.append([])
            for j in range(len(archive_diffusion_dataset)):
                if i != 1:
                    diffusion_values[i].append(archive_diffusion_dataset[j][i]/1000000)  # -> nm^2 in ym^2
                else:
                    diffusion_values[i].append(archive_diffusion_dataset[j][i])
        
        dset = hdf5_physical_model_group.create_dataset("diffusionCoefficient", (shape,),
                                                        dtype=np.dtype([("D [\u03BCm\u00b2/s]", float),
                                                                        ("fix", float),
                                                                        ("min D [\u03BCm\u00b2/s]", float),
                                                                        ("max D [\u03BCm\u00b2/s]", float)]))
        dset["D [\u03BCm\u00b2/s]"] = diffusion_values[0]
        dset["fix"] = diffusion_values[1]
        dset["min D [\u03BCm\u00b2/s]"] = diffusion_values[2]
        dset["max D [\u03BCm\u00b2/s]"] = diffusion_values[3]
            
    def add_weight_coeff(self):
        archive_physical_model_group = self.archive_file["physical model"]
        archive_weight_dataset = archive_physical_model_group["weight coefficient"]
        self.hdf5_file.create_dataset("/physicalModel/weightCoefficient", data=archive_weight_dataset)
            
    def add_equilibrium_matrix(self):
        archive_hmm_group = self.archive_file["hmm"]
        archive_eq_matrix_dataset = archive_hmm_group["equilibrium matrix"]
        self.hdf5_file.create_dataset("/hmm/equilibriumMatrix", data=archive_eq_matrix_dataset)
        
    def add_statistics(self):
        archive_hmm_group = self.archive_file["hmm"]
        archive_statistics_dataset = archive_hmm_group["statistics"]
        self.hdf5_file.create_dataset("/hmm/statistics", data=archive_statistics_dataset)
        
    def add_obervation_alphabet(self):
        archive_hmm_group = self.archive_file["hmm"]
        archive_observation_alphabet_dataset = archive_hmm_group["observation alphabet"]
        self.hdf5_file.create_dataset("/hmm/observationAlphabet", data=archive_observation_alphabet_dataset)
        
    def add_observation_matrix(self):
        archive_hmm_group = self.archive_file["hmm"]
        archive_observation_matrix_dataset = archive_hmm_group["observation matrix"]
        self.hdf5_file.create_dataset("/hmm/observationMatrix", data=archive_observation_matrix_dataset)
        
    def add_transition_matrix(self):
        archive_hmm_group = self.archive_file["hmm"]
        archive_transition_matrix_dataset = archive_hmm_group["transition matrix"]
        self.hdf5_file.create_dataset("/hmm/transitionMatrix", data=archive_transition_matrix_dataset)
        
    def close(self):
        self.archive_file.close()
        self.hdf5_file.close()
        
    def run(self):
        self.create_missing_groups()
        self.trc_placeholder_to_state()
        self.add_roi_dataset_to_settings()
        self.add_judi()
        self.add_diffusion_coeff()
        self.add_weight_coeff()
        self.add_equilibrium_matrix()
        self.add_statistics()
        self.add_obervation_alphabet()
        self.add_observation_matrix()
        self.add_transition_matrix()
        self.close()
