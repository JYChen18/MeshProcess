import os 
import argparse
from glob import glob
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import get_config

if __name__ == '__main__':
    path_cfg = get_config('main', 'customized')
    
    raw_lst = glob(os.path.join(path_cfg['processed_folder'], '**', path_cfg['tasks']['_normalize']['input_path']))
    coacd_lst = glob(os.path.join(path_cfg['processed_folder'], '**', path_cfg['tasks']['_coacd']['output_path']))
    simp_lst = glob(os.path.join(path_cfg['processed_folder'], '**', path_cfg['tasks']['_change_mesh_format']['output_path']))

    print('Raw object number: ', len(raw_lst))
    print('CoACD success rates: ', len(coacd_lst) / len(raw_lst))
    print('Manifold+Simplify success rates: ', len(simp_lst) / len(coacd_lst))
    print('Total success rates: ', len(simp_lst) / len(raw_lst))
    