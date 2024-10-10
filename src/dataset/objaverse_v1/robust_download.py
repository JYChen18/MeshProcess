import os 
import argparse
import multiprocessing
import time 

def download_process(run_file, args, output_file):
    os.system(f'python -u {run_file} -c {args.category} -n {args.n_worker} > {output_file} 2>&1')
    return 


def monitor_file(output_file, check_time):
    last_size = os.path.getsize(output_file)
    while True:
        time.sleep(check_time)  
        current_size = os.path.getsize(output_file)
        if current_size == last_size:
            print("Process is stuck, restarting...")
            return True
        last_size = current_size
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--category', type=str, required=True,
        choices=['Human-Shape', 'Animals', 'Daily-Used', 'Furnitures',
                'Buildings&&Outdoor', 'Transportations', 'Plants', 
                'Food', 'Electronics', 'Poor-quality'])
    parser.add_argument('-n', '--n_worker', type=int, default=10)
    parser.add_argument('-t', '--check_time', type=int, default=60)
    args = parser.parse_args()

    output_file = 'output.txt'
    open(output_file, 'a').close()
    run_file = __file__.replace('robust_download', 'download')
    
    while True:
        p1 = multiprocessing.Process(target=download_process, args=(run_file, args, output_file))
        p1.start()

        if monitor_file(output_file, args.check_time):
            p1.terminate()
            p1.join()