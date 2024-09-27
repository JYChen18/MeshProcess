import os 
import argparse
from glob import glob
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import get_config

if __name__ == '__main__':
    path_cfg = get_config('customized')
    
    raw_lst = glob(os.path.join(path_cfg['processed_folder'], '**', path_cfg['tasks']['_coacd']['input_path']))
    coacd_lst = glob(os.path.join(path_cfg['processed_folder'], '**', path_cfg['tasks']['_coacd']['output_path']))
    mani_lst = glob(os.path.join(path_cfg['processed_folder'], '**', path_cfg['tasks']['_manifold']['output_path']))
    simp_lst = glob(os.path.join(path_cfg['processed_folder'], '**', path_cfg['tasks']['_simplify']['output_path']))
    print(simp_lst[0])
    print('Raw object number: ', len(raw_lst))
    print('CoACD success rates: ', len(coacd_lst) / len(raw_lst))
    print('Manifold success rates: ', len(mani_lst) / len(coacd_lst))
    print('Simplify success rates: ', len(simp_lst) / len(mani_lst))
    print('Total success rates: ', len(simp_lst) / len(raw_lst))
    