import pandas as pd
from pathlib import Path

def load_trip(folder,side):
    '''Load one PVS trip (one side) with labels, relative time and surface type.
    folder: path to the trip folder
    side: 'left' or 'right' '''

    folder=Path(folder)
    dataset_labels=pd.read_csv(folder/'dataset_labels.csv')
    gps_mpu_data=pd.read_csv(folder/f'dataset_gps_mpu_{side}.csv')

    assert len(gps_mpu_data)==len(dataset_labels), \
        'The number of rows in gps_mpu_data and dataset_labels do not match.'

    data=pd.concat([gps_mpu_data, dataset_labels], axis=1)
    data['t']=data['timestamp']-data['timestamp'].iloc[0]
    road=['asphalt_road', 'cobblestone_road', 'dirt_road']
    data['surface']=data[road].idxmax(axis=1)

    return data