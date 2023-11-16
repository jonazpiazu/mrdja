#!/usr/bin/env python

import logging
from dataclasses import dataclass, InitVar
from pathlib import Path
import os
import requests
from typing import Dict
from natsort import natsorted
import open3d as o3d
import py7zr
import multivolumefile


@dataclass(frozen=False)
class IndustrialDataset:
    scene: str = 'EvenTableSinglePartZivid'
    data_root: str = os.environ.get('OPEN3D_DATA_ROOT')

    def __post_init__(self):
        self.file_index = {"EvenTableSinglePartZivid": ["https://github.com/jonazpiazu/lanverso-industrial-dataset/raw/main/EvenTableSinglePartZivid.7z.0001",
                                                        "https://github.com/jonazpiazu/lanverso-industrial-dataset/raw/main/EvenTableSinglePartZivid.7z.0002",
                                                        "https://github.com/jonazpiazu/lanverso-industrial-dataset/raw/main/EvenTableSinglePartZivid.7z.0003",
                                                        "https://github.com/jonazpiazu/lanverso-industrial-dataset/raw/main/EvenTableSinglePartZivid.7z.0004"],
                           "EvenTableSinglePartRealsense": ["https://github.com/jonazpiazu/lanverso-industrial-dataset/raw/main/EvenTableSinglePartRealsense.7z.0001"]}
        if not self.data_root:
            logging.debug('Using default download path')
            self.data_root = os.environ.get('HOME') + '/open3d_data'

        if not Path(self.data_root).exists():
            Path(self.data_root).mkdir()
        download_path = Path(self.data_root) / Path('download') 
        if not download_path.exists():
            download_path.mkdir()
        extract_base_dir = Path(self.data_root) / Path('extract') 
        if not extract_base_dir.exists():
            extract_base_dir.mkdir()
        
        for file_url in self.file_index.get(self.scene):
            destination_file = download_path / Path(file_url.split("/")[-1])
            if destination_file.exists():
                logging.debug('File already downloaded, skipping download')
            else:
                logging.info(f'Downloading {file_url}')
                self.download_file(file_url, destination_file)
                logging.info(f'Downloaded to {destination_file}')
        
        extract_path = extract_base_dir / Path(self.scene)
        self.paths = None
        if not extract_path.exists():
            extract_path.mkdir()
            logging.info(f'Created directory {extract_path}')

            compressed_target = download_path / destination_file.stem
            logging.info(f'Extracting {compressed_target}')
            with multivolumefile.open(compressed_target , mode='rb') as target_archive:
                with py7zr.SevenZipFile(target_archive, 'r') as archive:
                    archive.extractall(extract_path)
                    self.paths = [str(Path(extract_path) / Path(f.filename)) for f in archive.list()]
            logging.info(f'Extracted to {extract_path}')

        else:
            self.paths = [str(f) for f in extract_path.iterdir() if f.is_file()]

        self.paths = natsorted(self.paths)

    def download_file(self, url, destination_file):
        response = requests.get(url)
        if response.status_code == 200:
            with open(destination_file, 'wb') as file:
                file.write(response.content)
            return destination_file
        else:
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    dataset = IndustrialDataset()
    for pcd_path in dataset.paths:
        pcd = o3d.io.read_point_cloud(pcd_path)
        print(pcd)

    dataset = IndustrialDataset(scene='EvenTableSinglePartRealsense')
    for pcd_path in dataset.paths:
        pcd = o3d.io.read_point_cloud(pcd_path)
        print(pcd)
