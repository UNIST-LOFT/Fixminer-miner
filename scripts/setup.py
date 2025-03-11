import os
import argparse
import re
import sys
import json
import shutil
import subprocess
import multiprocessing as mp
import logging

def shellGitCheckout(cmd,timeout =600,enc='utf-8',cwd=os.getcwd()):
    output = ''
    errors = ''
    # logging.debug(cmd)

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,encoding=enc,cwd=cwd) as p:
        try:
            output, errors = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as t:
            p.terminate()
            p.communicate()

    return output,errors

def is_template(tool:str):
    if tool.lower() in ('tbar','avatar','kpar','fixminer'):
        return True
    else: return False

arg_parser = argparse.ArgumentParser('setup.py')
arg_parser.add_argument('tool',type=str,help='Name of the tool')
arg_parser.add_argument('project_path',type=str,help='Path to the (buggy) project')
arg_parser.add_argument('patch_path',type=str,help='Path to the patches')
arg_parser.add_argument('work_dir',type=str,help='Path to the working directory')
arg_parser.add_argument('--fixminer-path',type=str,help='Path to the Fixminer miner repository',
                        required=False,default=os.getcwd())
arg_parser.add_argument('-j','--parallel',type=int,help='Parallel job for each versions',default=1,required=False)

args=arg_parser.parse_args(sys.argv[1:])
tool:str = args.tool
project_path:str = args.project_path
patch_path:str = args.patch_path
work_dir:str = args.work_dir
fixminer_path:str = args.fixminer_path

logger=logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)

# Generate required directories
if os.path.exists(work_dir):
    os.system('rm -rf '+work_dir)
os.makedirs(work_dir)
os.makedirs(os.path.join(work_dir,'patches'))
os.makedirs(os.path.join(work_dir,'patches','fuse'))
os.makedirs(os.path.join(work_dir,'patches','fuse','DiffEntries'))
os.makedirs(os.path.join(work_dir,'patches','fuse','prevFiles'))
os.makedirs(os.path.join(work_dir,'patches','fuse','revFiles'))

# Generate config.yml
body=f"""java:
    8home:  /usr/lib/jvm/java-8-openjdk-amd64
spinfer:
    home:   /Users/anil.koyuncu/projects/fixminer/spinfer/spinfer.native
coccinelle:
    home:   /Users/anil.koyuncu/projects/fixminer/spinfer/statics

dataset:
#    home:   /Users/anilkoyuncu/projects/fixminer/fixminer-core/python/data/gumInputLinux

    inputPath : {work_dir}/patches
    repo:   {work_dir}/datasets

fixminer:
    projectType : java
    datapath: {work_dir}/



    pjName : patches
    portDumps : 6399
    numOfWorkers : 14
    hostname : localhost
    hunkLimit : 2
    patchSize : 50


    projectList : fuse
    inputPath : {work_dir}/patches
    redisPath : {fixminer_path}/python/data/redis
    srcMLPath :  /usr/local/bin/srcml
"""
with open(os.path.join(work_dir,'config.yml'),'w') as f:
    f.write(body)

def process(version):
    global logger
    # Checkout the buggy version
    if os.path.exists(f'{project_path}/{version}'):
        shutil.rmtree(f'{project_path}/{version}')
    logger.info(f'Checkout {version}...')
    res=subprocess.run(['defects4j','checkout','-p',version.split('_')[0],'-v',version.split('_')[1]+'b','-w',f'{project_path}/{version}'],
                       cwd=project_path,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    if res.returncode!=0:
        logger.warning(res.stdout)
        raise Exception(f'Failed to checkout {version}')
    
    with open(f'{patch_path}/{version}/switch-info.json') as f:
        switch_info = json.load(f)['rules']
    
    for file in switch_info:
        if is_template(tool):
            file_path=file['file_name']
        else:
            file_path=file['file']
        logger.info(f'Processing {version}:\t{file_path}...')
        for func in file['functions']:
            for line in func['lines']:
                for p in line['cases']:
                    patch_loc=p['location']
                    file_name=f'{version}_{file_path.replace("/","#")}'
                    patch_name=f'{version}_{patch_loc.replace("/","#")}'
                    
                    shutil.copyfile(f'{project_path}/{version}/{file_path}',f'{work_dir}/patches/fuse/prevFiles/prev_{patch_name}')
                    shutil.copyfile(f'{patch_path}/{version}/{patch_loc}',f'{work_dir}/patches/fuse/revFiles/{patch_name}')

                    # Generate diff file with git diff
                    shutil.copyfile(f'{project_path}/{version}/{file_path}',f'{project_path}/{version}/{file_path}.orig')
                    shutil.copyfile(f'{patch_path}/{version}/{patch_loc}',f'{project_path}/{version}/{file_path}')
                    cmd = 'git diff'# + shaOld + ':' + filePath + '..' + sha + ':' + filePath  # + '> ' + folderDiff + '/' + sha + '_' + shaOld + '_' + savePath.replace('.java','.txt')

                    output,errors = shellGitCheckout(cmd,enc='latin1',cwd=f'{project_path}/{version}')
                    if errors:
                        raise FileNotFoundError

                    # Parse the diff
                    regex = r"@@\s\-\d+,*\d*\s\+\d+,*\d*\s@@ ?(.*\n)*"
                    match = re.search(regex, output)
                    if not match:
                        logger.error('re.search not found')
                        exit(1)
                    not_matched, matched = output[:match.start()], match.group()
                    numberOfHunks = re.findall(r'@@\s\-\d+,*\d*\s\+\d+,*\d*\s@@', matched)
                    if len(numberOfHunks) == 0:
                        logger.error('re.findall not found')
                        exit(1)
                    diffFile = file_path + '\n' + matched.replace(' @@ ', ' @@\n')
                    with open(f'{work_dir}/patches/fuse/DiffEntries/{patch_name}.txt','w') as writeFile:
                        writeFile.writelines(diffFile)

                    # Rollback the patches
                    shutil.copyfile(f'{project_path}/{version}/{file_path}.orig',f'{project_path}/{version}/{file_path}')
                    os.remove(f'{project_path}/{version}/{file_path}.orig')

# Copy orig and patched files, and generate diff files in parallel
pool=mp.Pool(args.parallel)
for version in os.listdir(patch_path):
    if 'Mockito' in version:
        continue
    pool.apply_async(process,(version,))
pool.close()
pool.join()