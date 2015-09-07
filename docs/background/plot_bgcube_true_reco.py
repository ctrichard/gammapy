"""
Script to produce plots comparing 2 background cube models.

Details in stringdoc of the plot_bg_cube_model_comparison function.

Inspired on the Gammapy examples/plot_bg_cube_model_comparison.py script.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from astropy.units import Quantity
from astropy.coordinates import Angle
from astropy.table import Table
from astropy.io import ascii
from gammapy.background import CubeBackgroundModel
from gammapy import datasets

E_REF = Quantity(1., 'TeV') # reference energy
NORM = 1
INDEX = 1.5


def power_law(energy, E_0, norm, index):
    return norm*(energy/E_0)**-index


def int_power_law(energy_band, E_0, norm, index):
    return norm/(1 - index)/E_0**-index*(energy_band[1]**(1 - index) - energy_band[0]**(1 - index))


def plot_bg_cube_model_comparison(input_file1, name1,
                                  input_file2, name2):
    """
    Plot background cube model comparison.

    Produce a figure for comparing 2 bg cube models (1 and 2).

    Plot strategy in each figure:

    * Images:
        * rows: similar energy bin
        * cols: same bg cube model set
    * Spectra:
        * rows: similar det bin
        * cols: compare both bg cube model sets

    Parameters
    ----------
    input_file1, input_file2 : str
        File where the corresponding bg cube model is stored.
    name1, name2 : str
        Name to use for plot labels/legends.
    """
    # get cubes
    filename1 = input_file1
    filename2 = input_file2
    print('filename1', filename1)
    print('filename2', filename2)
    bg_cube_model1 = CubeBackgroundModel.read(filename1,
                                              format='table').background_cube
    bg_cube_model2 = CubeBackgroundModel.read(filename2,
                                              format='table').background_cube

    # normalize 1 w.r.t. 2 (i.e. true w.r.t. reco)
    # normalize w.r.t. cube integral
    integral1 = bg_cube_model1.integral
    integral2 = bg_cube_model2.integral
    bg_cube_model1.data *= integral2/integral1

    # make sure that both cubes use the same units for the plots
    bg_cube_model2.data = bg_cube_model2.data.to(bg_cube_model1.data.unit)

    # plot
    fig, axes = plt.subplots(nrows=2, ncols=3)
    fig.set_size_inches(30., 15., forward=True)
    group_info = 'group 27: ALT = [72.0, 90.0) deg, AZ = [90.0, 270.0) deg'
    plt.suptitle(group_info)

    # plot images
    #  rows: similar energy bin
    #  cols: same file
    bg_cube_model1.plot_image(energy=Quantity(1., 'TeV'), ax=axes[0, 0])
    axes[0, 0].set_title("{0}: {1}".format(name1, axes[0, 0].get_title()))
    bg_cube_model1.plot_image(energy=Quantity(10., 'TeV'), ax=axes[1, 0])
    axes[1, 0].set_title("{0}: {1}".format(name1, axes[1, 0].get_title()))
    bg_cube_model2.plot_image(energy=Quantity(1., 'TeV'), ax=axes[0, 1])
    axes[0, 1].set_title("{0}: {1}".format(name2, axes[0, 1].get_title()))
    bg_cube_model2.plot_image(energy=Quantity(10., 'TeV'), ax=axes[1, 1])
    axes[1, 1].set_title("{0}: {1}".format(name2, axes[1, 1].get_title()))

    # plot spectra
    #  rows: similar det bin
    #  cols: compare both files
    bg_cube_model1.plot_spectrum(coord=Angle([0., 0.], 'degree'),
                                 ax=axes[0, 2],
                                 style_kwargs=dict(color='blue',
                                                   label=name1))
    spec_title1 = axes[0, 2].get_title()
    bg_cube_model2.plot_spectrum(coord=Angle([0., 0.], 'degree'),
                                 ax=axes[0, 2],
                                 style_kwargs=dict(color='red',
                                                   label=name2))
    spec_title2 = axes[0, 2].get_title()
    if spec_title1 != spec_title2:
        s_error = "Expected same det binning, but got "
        s_error += "\"{0}\" and \"{1}\"".format(spec_title1, spec_title2)
        raise ValueError(s_error)
    else:
        axes[0, 2].set_title(spec_title1)

    # plot normalized models on top

    E_0 = E_REF
    norm = NORM
    index = INDEX

    plot_data_x = axes[0, 2].get_lines()[0].get_xydata()[:,0]
    plot_data_y = axes[0, 2].get_lines()[0].get_xydata()[:,1]
    plot_data_int = np.trapz(y=plot_data_y, x=plot_data_x)
    energy_band = np.array([plot_data_x[0], plot_data_x[-1]])
    model_int = int_power_law(energy_band, E_0, norm, index)
    normed_PL1 = plot_data_int/model_int*power_law(plot_data_x, E_0, norm, index)
    axes[0, 2].plot(plot_data_x, normed_PL1, color='blue',
                    linestyle='dotted', linewidth=2,
                    label='model index = {}'.format(index))

    index = INDEX + 1

    plot_data_x = axes[0, 2].get_lines()[0].get_xydata()[:,0]
    plot_data_y = axes[0, 2].get_lines()[0].get_xydata()[:,1]
    plot_data_int = np.trapz(y=plot_data_y, x=plot_data_x)
    energy_band = np.array([plot_data_x[0], plot_data_x[-1]])
    model_int = int_power_law(energy_band, E_0, norm, index)
    normed_PL2 = plot_data_int/model_int*power_law(plot_data_x, E_0, norm, index)
    axes[0, 2].plot(plot_data_x, normed_PL2, color='blue',
                    linestyle='dashed', linewidth=2,
                    label='model index = {}'.format(index))

    axes[0, 2].legend()

    bg_cube_model1.plot_spectrum(coord=Angle([2., 2.], 'degree'),
                                 ax=axes[1, 2],
                                 style_kwargs=dict(color='blue',
                                                   label=name1))
    spec_title1 = axes[1, 2].get_title()
    bg_cube_model2.plot_spectrum(coord=Angle([2., 2.], 'degree'),
                                 ax=axes[1, 2],
                                 style_kwargs=dict(color='red',
                                                   label=name2))
    spec_title2 = axes[1, 2].get_title()
    if spec_title1 != spec_title2:
        s_error = "Expected same det binning, but got "
        s_error += "\"{0}\" and \"{1}\"".format(spec_title1, spec_title2)
        raise ValueError(s_error)
    else:
        axes[1, 2].set_title(spec_title1)

    # plot normalized models on top

    E_0 = E_REF
    norm = NORM
    index = INDEX

    plot_data_x = axes[1, 2].get_lines()[0].get_xydata()[:,0]
    plot_data_y = axes[1, 2].get_lines()[0].get_xydata()[:,1]
    plot_data_int = np.trapz(y=plot_data_y, x=plot_data_x)
    energy_band = np.array([plot_data_x[0], plot_data_x[-1]])
    model_int = int_power_law(energy_band, E_0, norm, index)
    normed_PL1 = plot_data_int/model_int*power_law(plot_data_x, E_0, norm, index)
    axes[1, 2].plot(plot_data_x, normed_PL1, color='blue',
                    linestyle='dotted', linewidth=2,
                    label='model index = {}'.format(index))

    index = INDEX + 1

    plot_data_x = axes[1, 2].get_lines()[0].get_xydata()[:,0]
    plot_data_y = axes[1, 2].get_lines()[0].get_xydata()[:,1]
    plot_data_int = np.trapz(y=plot_data_y, x=plot_data_x)
    energy_band = np.array([plot_data_x[0], plot_data_x[-1]])
    model_int = int_power_law(energy_band, E_0, norm, index)
    normed_PL2 = plot_data_int/model_int*power_law(plot_data_x, E_0, norm, index)
    axes[1, 2].plot(plot_data_x, normed_PL2, color='blue',
                    linestyle='dashed', linewidth=2,
                    label='model index = {}'.format(index))

    axes[1, 2].legend()

    plt.show()


if __name__ == '__main__':
    """Main function: define arguments and launch the whole analysis chain.
    """
    input_file1 = '../test_datasets/background/bg_cube_model_true.fits.gz'
    input_file1 = datasets.get_path(input_file1, location='remote')
    name1 = 'true'

    input_file2 = '../test_datasets/background/bg_cube_model_reco.fits.gz'
    input_file2 = datasets.get_path(input_file2, location='remote')
    name2 = 'reco'

    plot_bg_cube_model_comparison(input_file1, name1,
                                  input_file2, name2)
