import os
import sys

data_dir=sys.argv[1]

for file in os.listdir(f'{data_dir}/patches/fuse/revFiles').copy():
    if not os.path.exists(f'{data_dir}/patches/fuse/DiffEntries/{file}.txt'):
        print(f'Remove {file}')
        os.remove(f'{data_dir}/patches/fuse/revFiles/{file}')
        os.remove(f'{data_dir}/patches/fuse/prevFiles/prev_{file}')