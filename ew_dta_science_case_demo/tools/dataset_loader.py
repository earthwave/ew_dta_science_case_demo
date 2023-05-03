"""A module to load and plot datasets on the /dtadata drive."""
from __future__ import annotations
from datetime import datetime
from datetime import timedelta
import os

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tifffile

MIN_X = -1905772.0
MAX_X = -1405772.0
MIN_Y = -845000.0
MAX_Y = -145000.0

RESOLUTION = 1000

class OpenScienceDataset():
    """Class for loading a DTA dataset."""

    def __init__(self: OpenScienceDataset, dataset_name) -> None:
        self.base_dir = '/dtadata/open_science_case/open_science_common_grid/'
        self.dataset_name = dataset_name
        self.data, self.dates, self.info = self._load_dataset()
        self.units = self._get_units()

    def _get_units(self):
        if self.dataset_name == 'eolis_dems':
            units = 'm'
        if self.dataset_name == 'mean_sea_level_pressure':
            units = 'Pa'
        if self.dataset_name == '10m_wind_speed':
            units = 'm/s'
        if self.dataset_name == 'sea_water_salinity':
            units = 'ppt'
        if self.dataset_name == 'ice_flow':
            units = 'm/yr'
        if self.dataset_name == 'grounding_line_migration_rates':
            units = 'm/yr'
        if self.dataset_name == 'ice_shelf_basal_melt_rate':
            units = 'm/yr'
        if self.dataset_name == 'sea_water_potential_temperature':
            units = 'degrees C'
        if self.dataset_name == 'el_nino':
            units = 'SST'

        return units

    def _load_dataset(self):
        if self.dataset_name in ['eolis_dems', 'sea_water_potential_temperature', 'sea_water_salinity']:
            tifs_for_dataset = os.listdir(os.path.join(self.base_dir, self.dataset_name))
            dates = sorted([datetime.strptime(tif.removesuffix('.tiff'), "%m_%Y") for tif in tifs_for_dataset])
            data = []
            for date in dates:
                if self.dataset_name == 'eolis_dems':
                    data.append(tifffile.imread(os.path.join(self.base_dir, self.dataset_name, f'{date.strftime(format="%m_%Y")}.tiff'))[::-1]) # the eolis dems are upside down
                else:
                    data.append(tifffile.imread(os.path.join(self.base_dir, self.dataset_name, f'{date.strftime(format="%m_%Y")}.tiff')))

            data = np.stack(data)
            info = f'Monthly data between {dates[0].strftime(format="%Y-%m-%d")} and {dates[-1].strftime(format="%Y-%m-%d")}'

        if self.dataset_name == 'mean_sea_level_pressure':
            tifs_for_dataset = os.listdir(os.path.join(self.base_dir, self.dataset_name))
            dates = sorted([datetime.strptime(tif[4:].removesuffix('.tiff'), "%m_%Y") for tif in tifs_for_dataset])
            data = []
            for date in dates:
                data.append(tifffile.imread(os.path.join(self.base_dir, self.dataset_name, f'msl_{date.strftime(format="%m_%Y")}.tiff')))

            data = np.stack(data)
            info = f'Monthly data between {dates[0].strftime(format="%Y-%m-%d")} and {dates[-1].strftime(format="%Y-%m-%d")}'

        if self.dataset_name == '10m_wind_speed':
            tifs_for_dataset = os.listdir(os.path.join(self.base_dir, self.dataset_name))
            dates = sorted(set([datetime.strptime(tif[4:].removesuffix('.tiff'), "%m_%Y") for tif in tifs_for_dataset]))

            data_u = []
            data_v = []
            for date in dates:
                data_u.append(tifffile.imread(os.path.join(self.base_dir, self.dataset_name, f'u10_{date.strftime(format="%m_%Y")}.tiff')))
                data_v.append(tifffile.imread(os.path.join(self.base_dir, self.dataset_name, f'v10_{date.strftime(format="%m_%Y")}.tiff')))

            data = np.stack([np.stack(data_u), np.stack(data_v)])

            info = f'Monthly data between {dates[0].strftime(format="%Y-%m-%d")} and {dates[-1].strftime(format="%Y-%m-%d")} with dimension \n' \
                    '(Direction (U/V), Time, X, Y)'

        if self.dataset_name == 'ice_flow':
            tifs_for_dataset = os.listdir(os.path.join(self.base_dir, self.dataset_name))
            dates = sorted([datetime.strptime(tif.split('_')[-1].removeprefix('c').removesuffix('.tif'), "%Y") for tif in tifs_for_dataset])
            data = []
            for date in dates:
                filename = f'WAIS_vel_c{date.strftime(format="%Y")}.tif' if date.year != 2015 else f'WAIS_vel_{date.strftime(format="%Y")}.tif'
                data.append(tifffile.imread(os.path.join(self.base_dir, self.dataset_name, filename)))

            data = np.stack(data)
            info = '2003: Composite c.2003 ice-flow magnitude grid (m yr-1) generated from the temporal stacking of multiple ice velocity measurements acquired between 1999 and 2006.5.\n' \
                   '2008: Composite c.2008 ice-flow magnitude grid (m yr-1) generated from the temporal stacking of multiple ice velocity measurements acquired between 2006 and 2010.5.\n' \
                   '2010: Composite c.2010 ice-flow magnitude grid (m yr-1) generated from the temporal stacking of multiple ice velocity measurements acquired between 2008 and 2012\n' \
                   '2015: 2015 ice-flow magnitude grid (m yr-1) acquired from the NASA ITS_LIVE data archive.'
            
        if self.dataset_name == 'grounding_line_migration_rates':
            tifs_for_dataset = sorted(os.listdir(os.path.join(self.base_dir, self.dataset_name)))
            data = np.stack([tifffile.imread(os.path.join(self.base_dir, self.dataset_name, tif)) for tif in tifs_for_dataset])

            dates = [datetime(2005, 6, 1), datetime(2012, 6, 1)]
            info = '2005.5: Observed grounding-line migration rate (m yr-1) over the period 2003-2008.\n' \
                   '2012.5: Observed grounding-line migration rate (m yr-1) over the period 2010-2015.'

        if self.dataset_name == 'ice_shelf_basal_melt_rate':
            with Dataset(os.path.join(self.base_dir, 'ice_shelf_basal_melt_rate', 'amundsen-open-science-final.nc')) as nc:
                dates = [datetime(int(date), 1, 1) + timedelta(int((date % 1) * 365)) for date in nc.variables['dates'][:]]
                data = nc.variables['melt'][:]
            
            info = f'Monthly data between {dates[0].strftime(format="%Y-%m-%d")} and {dates[-1].strftime(format="%Y-%m-%d")}'
        
        if self.dataset_name == 'el_nino':
            with open(os.path.join(self.base_dir, 'monthly_el_nino_oscillation.txt')) as f:
                lines = f.readlines()[1:] # remove first line

                dates = []
                data = []
                for line in lines[:-9]:
                    data_in_line = line.split('  ')
                    year = int(data_in_line[0])
                    dates.extend([datetime(year, month, 1) for month in np.arange(1, 13, 1)])
                    data.extend([float(value.replace('\n', '')) for value in data_in_line[1:]])

                info = ''.join(lines[-7:])

        return data, dates, info

    def plot2d(self, ax, extent, min_t, max_t, colourmap='viridis', transparency=1):

        min_x_index, max_x_index, min_y_index, max_y_index = OpenScienceDataset._extent_to_common_grid_indices(extent)
        min_t_index, max_t_index =  self._min_t_max_t_to_date_indices(min_t, max_t)
        data_to_plot = self.data[max_t_index][max_y_index:min_y_index, min_x_index:max_x_index] - \
                       self.data[min_t_index][max_y_index:min_y_index, min_x_index:max_x_index]
        
        if self.dataset_name == 'grounding_line_migration_rates':
            data_to_plot = self.data[max_t_index][max_y_index:min_y_index, min_x_index:max_x_index]

        time_delta_plot = \
            ax.imshow(data_to_plot, cmap=colourmap, alpha=transparency, interpolation='nearest', extent=extent)
        
        cbar = plt.colorbar(time_delta_plot, shrink=0.4, location='right', pad=0.1)

        return time_delta_plot, cbar.set_label(f'{self.dataset_name} ({self.units})')

    def plot_time_series(self, ax, extent, min_t, max_t):

        min_t_index, max_t_index =  self._min_t_max_t_to_date_indices(min_t, max_t)
        dates_to_plot = self.dates[min_t_index:max_t_index]

        if self.dataset_name == 'el_nino':
            time_series_data =  self.data[min_t_index:max_t_index]

        else:
            min_x_index, max_x_index, min_y_index, max_y_index = OpenScienceDataset._extent_to_common_grid_indices(extent)
            time_series_data = [np.nanmean(data) for data in self.data[min_t_index:max_t_index, max_y_index:min_y_index, min_x_index:max_x_index]]

        time_series_plot = ax.plot(dates_to_plot, time_series_data)
        ax.set_title(self.dataset_name)
        ax.set_ylabel(self.units)
        ax.xaxis.set_major_locator(mdates.YearLocator())

        return time_series_plot

    def _min_t_max_t_to_date_indices(self, min_t, max_t):
        
        min_t_index = self.dates.index(min(self.dates, key=lambda d: abs(d - min_t)))
        max_t_index = self.dates.index(min(self.dates, key=lambda d: abs(d - max_t)))

        if min_t <= self.dates[0]:
            min_t_index = 0
        if max_t >= self.dates[-1]:
            max_t_index = -1

        return min_t_index, max_t_index

    def _extent_to_common_grid_indices(extent):
        '''Since everything is on a common grid, we get the indices corresponding to an extent'''

        assert extent[0] >= MIN_X, f'Min x must be greater than or equal to {MIN_X}'
        assert extent[1] <= MAX_X, f'Max x must be less than or equal to {MAX_X}'
        assert extent[2] >= MIN_Y, f'Min y must be greater than or equal to {MIN_Y}'
        assert extent[3] <= MAX_Y, f'Max y must be less than or equal to {MAX_Y}'

        min_x_index = int((extent[0] - MIN_X) / RESOLUTION)
        max_x_index = - int((MAX_X - extent[1]) / RESOLUTION) - 1
        min_y_index = - int((extent[2] - MIN_Y) / RESOLUTION) -1
        max_y_index = int((MAX_Y - extent[3]) / RESOLUTION)

        return min_x_index, max_x_index, min_y_index, max_y_index
