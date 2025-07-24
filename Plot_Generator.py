import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd


def CA_Overlay_Tiled(time_df, cur_df, save_path, color_by='Pixel', tile_by="Wavelength", target_pixels=[1, 2, 3, 4],
                     pixel_area=.09):
    wavelength_array = list(dict.fromkeys([col.split('nm')[0][-3:] for col in cur_df.columns]))
    power_array = list(dict.fromkeys([col.split('_Power-')[1].split("_")[0] for col in cur_df.columns]))
    pixel_array = list(dict.fromkeys([col.split('_P')[1][0:1] for col in cur_df.columns]))

    cur_df = cur_df / pixel_area

    fig, axes = plt.subplots(1, 1, figsize=(10, 8))
    tile_index_1 = 0
    tile_index_2 = 0

    if tile_by == 'Wavelength':
        fig, axes = plt.subplots(2, 5, figsize=(12, 6))
    elif tile_by == 'Pixel':
        fig, axes = plt.subplots(2, 2)

    for col in cur_df.columns:
        pixel = int(col.split('_P')[1][0:1])
        wavelength = col.split('nm')[0][-3:]
        power = int(col.split('_Power-')[1].split("_")[0])
        cur = cur_df[col]
        w_no = wavelength_array.index(wavelength)

        if tile_by == 'Wavelength':
            if w_no > 4:
                tile_index_1 = 1
                tile_index_2 = w_no % 5
            else:
                tile_index_1 = 0
                tile_index_2 = w_no

            axes[tile_index_1, tile_index_2].set_title(f"{wavelength}nm", fontsize=11, pad=-13, y=1.000001)
            line_label = f"{wavelength}-P{pixel}"


        elif tile_by == 'Pixel':

            if pixel > 2:
                tile_index_1 = 1
                tile_index_2 = (pixel - 1) % 2
            else:
                tile_index_1 = 0
                tile_index_2 = pixel - 1

            axes[tile_index_1, tile_index_2].set_title(f"Pixel {pixel}", fontsize=11, pad=-13, y=1.000001)

            line_label = f"{wavelength}"

        else:
            pass

        if color_by == 'Pixel':
            colors = ['r', 'g', 'b', 'k']
            line_color = colors[pixel - 1]
        elif color_by == 'Power':
            line_color = 'k'
        elif color_by == 'Wavelength':
            colors = [wavelength_to_rgb(wavelength) for wavelength in np.array(wavelength_array, dtype=int)]
            line_color = colors[w_no]
        else:
            line_color = 'k'

        if pixel in target_pixels:
            axes[tile_index_1, tile_index_2].plot(time_df, cur, color=line_color, label=line_label)
            axes[tile_index_1, tile_index_2].set_ylim(cur_df.min().min() - .15 * cur_df.min().min(),
                                                      cur_df.max().max() + .20 * cur_df.max().max())
            axes[tile_index_1, tile_index_2].tick_params(direction='in')

            if tile_index_1 == 1:
                axes[tile_index_1, tile_index_2].set_xlabel("Time (s)", fontsize=11)
            else:
                axes[tile_index_1, tile_index_2].set_xticklabels([])

            if tile_index_2 == 0:
                axes[tile_index_1, tile_index_2].set_ylabel('Current Density (uA/cm$^2$)', fontsize=11)
            else:
                axes[tile_index_1, tile_index_2].set_yticklabels([])

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', fontsize=4, bbox_to_anchor=(.955, .935))

    plt.tight_layout()

    if save_path == None:
        fig.show()
    else:
        fig.savefig(save_path, dpi=600)
        plt.close()


def CA_Bar_Graph(compiled_cur_sums, save_path, pixel_area=.09, colorblind=False):
    # Sample data

    # Create bar plot

    wavelength_array = list(dict.fromkeys([col.split('nm')[0][-3:] for col in compiled_cur_sums.columns]))
    int_wavelength_array = np.array([int(i) for i in wavelength_array])
    average_current_densities = []
    average_errors = []
    colors = []

    if colorblind==False:
        for wavelength in int_wavelength_array:
            colors.append(wavelength_to_rgb(wavelength))
    else:
        colors = plt.get_cmap('viridis')
        colors = colors(range(0, 300, 30))

    for wavelength in wavelength_array:
        wav_curs = compiled_cur_sums.drop(columns=compiled_cur_sums.columns[
            [i for i, v in enumerate(compiled_cur_sums.columns) if f"{wavelength}" not in v]])
        average_current_densities.extend([wav_curs.mean().mean()])
        average_errors.extend([wav_curs.values.std()])

    average_current_densities = np.array(average_current_densities)/pixel_area
    average_errors = np.array(average_errors) / pixel_area


    absolute_max = max(abs(np.array(average_current_densities)))
    # Setup figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # Define width and bar positions
    x = np.arange(len(wavelength_array))
    bar_width = .7

    # Create rounded bars manually
    for i, val in enumerate(average_current_densities):
        # Draw with a rounded box
        rounded_bar = patches.FancyBboxPatch(
            (x[i] - bar_width / 2, 0),  # lower-left corner
            bar_width, val,  # width, height
            boxstyle="square,pad=0",  # rounded corners
            edgecolor='black',
            facecolor=colors[i],
            capstyle = 'round'
        )
        ax.add_patch(rounded_bar)

    plt.errorbar(x, average_current_densities, yerr=average_errors, capsize=2, elinewidth=1, ecolor='k', fmt='None')
    ax.set_xticks(x)
    ax.set_xticklabels(wavelength_array, fontsize='12')
    plt.tick_params(axis='y', labelsize=12)
    ax.set_xlim(-.5, 9.5)
    ax.set_ylim(-absolute_max*1.05, absolute_max*1.05)
    ax.tick_params(direction='in')
    #plt.bar(wavelength_array, average_current_densities, color=colors)

    # Add labels and title
    plt.xlabel('Wavelength (nm)', fontsize=14, labelpad=10)
    plt.ylabel('Average Photocurrent (uA/cm$^{2}$)', fontsize=14)
    plt.axhline(y=0, color='black', linestyle='--', linewidth=1)

    # Display plot
    plt.tight_layout()

    if save_path == None:
        fig.show()
    else:
        fig.savefig(save_path, dpi=600)
        plt.close()

    final_summary = pd.DataFrame()
    final_summary['Averages'] = average_current_densities
    final_summary['Errors'] = average_errors
    final_summary['Wavelength'] = wavelength_array

    return final_summary

def CV_CSC_Bar_Graph(headers, data_array, title):
    pass


# Takes in an array for potential input and Dataframe (with proper titles) for current_df
def CV_Fill_Plot_Wavelength(potential_array, current_df, title):
    pass


# Generates a simple overlayed plot. Options for the sorting features are 'Power', 'Wavelength', or 'Pixel'
def CV_Overlay_Tiled(potential_array, current_df, save_path, all_scans=False, dark_repeat=True, color_by='Pixel',
                     tile_by="Wavelength", dash_by='Power', target_pixels=[1, 2, 3, 4]):
    wavelength_array = list(dict.fromkeys([col.split('nm')[0][-3:] for col in current_df.columns]))
    power_array = list(dict.fromkeys([col.split('_Power-')[1].split("_")[0] for col in current_df.columns]))
    pixel_array = list(dict.fromkeys([col.split('_P')[1][0:1] for col in current_df.columns]))
    scan_array = [int(i) for i in list(dict.fromkeys([col.split('Scan')[1] for col in current_df.columns]))]

    fig, axes = plt.subplots(1, 1, figsize=(10, 8))
    tile_index_1 = 0
    tile_index_2 = 0

    if tile_by == 'Wavelength':
        fig, axes = plt.subplots(2, 5, figsize=(12, 6))
    elif tile_by == 'Pixel':
        fig, axes = plt.subplots(2, 2)

    for col in current_df.columns:
        pixel = int(col.split('_P')[1][0:1])
        wavelength = col.split('nm')[0][-3:]
        power = int(col.split('_Power-')[1].split("_")[0])
        scan = int(col.split('Scan')[1])
        cur = current_df[col]
        w_no = wavelength_array.index(wavelength)

        power_status = False
        if power > 0:
            power_status = True
        else:
            power_status = False
            if w_no != np.shape(wavelength_array)[0] - 1:
                if not dark_repeat:
                    continue

        if tile_by == 'Wavelength':
            if w_no > 4:
                tile_index_1 = 1
                tile_index_2 = w_no % 5
            else:
                tile_index_1 = 0
                tile_index_2 = w_no

            axes[tile_index_1, tile_index_2].set_title(f"{wavelength}nm", fontsize=11, pad=-13, y=1.000001)

            if power_status == True:
                line_label = f"Pixel {pixel} - On"
            else:
                line_label = f"Pixel {pixel} - Off"

        elif tile_by == 'Pixel':
            axes[tile_index_1, tile_index_2].set_title(f"Pixel {pixel}", fontsize=11, pad=-13, y=1.000001)
            if pixel > 2:
                tile_index_1 = 1
                tile_index_2 = (pixel - 1) % 2
            else:
                tile_index_1 = 0
                tile_index_2 = pixel - 1

            if power_status == True:
                line_label = f"{wavelength} - On"
            else:
                line_label = f"{wavelength} - Off"

        if color_by == 'Pixel':
            colors = ['r', 'g', 'b', 'k']
            line_color = colors[pixel - 1]
        elif color_by == 'Power':
            line_color = 'k'
        elif color_by == 'Wavelength':
            colors = plt.get_cmap('jet')
            colors = colors(range(0, 300, 30))
            line_color = colors[w_no]
        else:
            line_color = 'k'

        if dash_by == "Power":
            if power > 0:
                line_dash = '-'
            else:
                line_dash = '--'
        else:
            line_dash = '-'

        if pixel in target_pixels:
            if not all_scans and scan != max(scan_array):
                continue

            axes[tile_index_1, tile_index_2].plot(potential_array, cur, color=line_color, linestyle=line_dash,
                                                  label=line_label)
            axes[tile_index_1, tile_index_2].set_ylim(current_df.min().min(), current_df.max().max())
            axes[tile_index_1, tile_index_2].tick_params(direction='in')

        if tile_index_1 == 1:
            axes[tile_index_1, tile_index_2].set_xlabel("Voltage (V)", fontsize=11)
        else:
            axes[tile_index_1, tile_index_2].set_xticklabels([])

        if tile_index_2 == 0:
            axes[tile_index_1, tile_index_2].set_ylabel("Current (uA)", fontsize=11)
        else:
            axes[tile_index_1, tile_index_2].set_yticklabels([])

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', fontsize=4, bbox_to_anchor=(.955, .935))

    plt.tight_layout()

    if save_path == None:
        fig.show()
    else:
        fig.show()
        fig.savefig(save_path, dpi=600)
        plt.close()


def OCP_Overlay_Tiled(time_df, potential_df, save_path, color_by='Pixel', tile_by="Wavelength", target_pixels=[1, 2, 3, 4],):

    wavelength_array = list(dict.fromkeys([col.split('nm')[0][-3:] for col in potential_df.columns]))
    power_array = list(dict.fromkeys([col.split('_Power-')[1].split("_")[0] for col in potential_df.columns]))
    pixel_array = list(dict.fromkeys([col.split('_P')[1][0:1] for col in potential_df.columns]))


    fig, axes = plt.subplots(1, 1, figsize=(10, 8))
    tile_index_1 = 0
    tile_index_2 = 0

    if tile_by == 'Wavelength':
        fig, axes = plt.subplots(2, 5, figsize=(12, 6))
    elif tile_by == 'Pixel':
        fig, axes = plt.subplots(2, 2)

    for col in potential_df.columns:
        pixel = int(col.split('_P')[1][0:1])
        wavelength = col.split('nm')[0][-3:]
        power = int(col.split('_Power-')[1].split("_")[0])
        pot = potential_df[col]
        w_no = wavelength_array.index(wavelength)

        if tile_by == 'Wavelength':
            if w_no > 4:
                tile_index_1 = 1
                tile_index_2 = w_no % 5
            else:
                tile_index_1 = 0
                tile_index_2 = w_no

            axes[tile_index_1, tile_index_2].set_title(f"{wavelength}nm", fontsize=11, pad=-13, y=1.000001)
            line_label = f"{wavelength}-P{pixel}"


        elif tile_by == 'Pixel':

            if pixel > 2:
                tile_index_1 = 1
                tile_index_2 = (pixel - 1) % 2
            else:
                tile_index_1 = 0
                tile_index_2 = pixel - 1

            axes[tile_index_1, tile_index_2].set_title(f"Pixel {pixel}", fontsize=11, pad=-13, y=1.000001)

            line_label = f"{wavelength}"

        else:
            pass

        if color_by == 'Pixel':
            colors = ['r', 'g', 'b', 'k']
            line_color = colors[pixel - 1]
        elif color_by == 'Power':
            line_color = 'k'
        elif color_by == 'Wavelength':
            colors = [wavelength_to_rgb(wavelength) for wavelength in np.array(wavelength_array, dtype=int)]
            line_color = colors[w_no]
        else:
            line_color = 'k'

        if pixel in target_pixels:
            axes[tile_index_1, tile_index_2].plot(time_df, pot, color=line_color, label=line_label)
            axes[tile_index_1, tile_index_2].set_ylim(potential_df.min().min() - .15 * potential_df.min().min(),
                                                      potential_df.max().max() + .20 * potential_df.max().max())
            axes[tile_index_1, tile_index_2].tick_params(direction='in')

            if tile_index_1 == 1:
                axes[tile_index_1, tile_index_2].set_xlabel("Time (s)", fontsize=11)
            else:
                axes[tile_index_1, tile_index_2].set_xticklabels([])

            if tile_index_2 == 0:
                axes[tile_index_1, tile_index_2].set_ylabel('Potential (V)', fontsize=11)
            else:
                axes[tile_index_1, tile_index_2].set_yticklabels([])

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', fontsize=4, bbox_to_anchor=(.955, .935))

    plt.tight_layout()

    if save_path is None:
        fig.show()
    else:
        fig.savefig(save_path, dpi=600)
        plt.close()



def OCP_Bar_Graph(headers, data_array):
    pass

def wavelength_to_rgb(wavelength, gamma=0.8):
    ''' taken from http://www.noah.org/wiki/Wavelength_to_RGB_in_Python
    This converts a given wavelength of light to an
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    Additionally alpha value set to 0.5 outside range
    '''
    wavelength = float(wavelength)
    real_wavelength = wavelength

    if wavelength >= 380 and wavelength <= 750:
        A = 1.
    else:
        A=0.5
    if wavelength < 380:
        wavelength = 380.
    if wavelength >750:
        wavelength = 750.
    if wavelength >= 380 and wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif wavelength >= 440 and wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif wavelength >= 490 and wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif wavelength >= 510 and wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif wavelength >= 580 and wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif wavelength >= 645 and wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0

    else:
        R = 0.0
        G = 0.0
        B = 0.0

    if real_wavelength > 860:
        R = R/2

    return [R,G,B,A]

if __name__ == "__main__":
    pass
