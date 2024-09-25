import os 
import trimesh
import argparse 
from util_file import write_json 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type=str, required=True)
    args = parser.parse_args()

    obj_code_lst = os.listdir(args.folder)
    for obj_code in obj_code_lst:
        tm = trimesh.load(os.path.join(args.folder, obj_code, 'coacd/simply.obj'))
        obb_length = tm.bounding_box_oriented.primitive.extents
        gravity_center = tm.center_mass
        write_json({'gravity_center': gravity_center.tolist(), 'obb': obb_length.tolist()}, os.path.join(args.folder, obj_code, 'info.json'))
        
        