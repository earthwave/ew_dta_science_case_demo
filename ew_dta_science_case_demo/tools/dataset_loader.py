"""A module to load and plot datasets on the /dtadata drive."""
from __future__ import annotations
from datetime import datetime
from datetime import timedelta
import os

from netCDF4 import Dataset
import numpy as np
import tifffile

class OpenScienceDataset():
    """Class for loading a DTA dataset."""

    def __init__(self: OpenScienceDataset, dataset_name) -> None:
        self.base_dir = '/dtadata/open_science_case/open_science_common_grid/'
        self.dataset_name = dataset_name
        self.data, self.dates, self.info = self._load_dataset()

    def _load_dataset(self):
        if self.dataset_name in ['eolis_dems', 'sea_level_pressure', 'sea_water_potential_temperature', 'sea_water_salinity']:
            tifs_for_dataset = os.listdir(os.path.join(self.base_dir, self.dataset_name))
            dates = sorted([datetime.strptime(tif.removesuffix('.tiff'), "%m_%Y") for tif in tifs_for_dataset])
            data = []
            for date in dates:
                data.append(tifffile.imread(os.path.join(self.base_dir, self.dataset_name, f'{date.strftime(format="%m_%Y")}.tiff')))

            data = np.stack(data)
            info = f'Monthly data between {dates[0].strftime(format="%Y_%m_%d")} and {dates[-1].strftime(format="%Y_%m_%d")}'

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
            with Dataset(os.path.join(self.base_dir, 'amundsen_melt_timeseries', 'amundsen-open-science-final.nc')) as nc:
                dates = [datetime(int(date), 1, 1) + timedelta(int((date % 1) * 365)) for date in nc.variables['dates'][:]]
                data = nc.variables['melt'][:]
            
            info = f'Monthly data starting between {dates[0].strftime(format="%Y_%m_%d")} and {dates[-1].strftime(format="%Y_%m_%d")}'

        return data, dates, info
