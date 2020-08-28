import bugzoo
from bugzoo import server, Container
import csv
import os
from common.commons import *
DATA_PATH = os.environ["DATA_PATH"]
ROOT_DIR = os.environ["ROOT_DIR"]
DATASET = os.environ["dataset"]
COCCI_PATH = join(os.environ["coccinelle"],'spatch')
def patchSourceFile(bugPath,spfile,bugName):
    # print(bugPath)
    # srcName = bugPath.split('/')[-1].split('-')[0]
    srcPath = bugPath
    patchName = bugName



    if(isfile(join(DATA_PATH,"codeflaws",bugName,'patched',patchName+spfile+'.c'))):
        return join(DATA_PATH,"codeflaws",bugName,'patched',patchName+spfile+'.c')

    if not (isfile(join(DATA_PATH,"codeflaws",bugName,'patches',patchName+spfile+'.txt'))):
        cmd = COCCI_PATH + ' --sp-file ' + join(DATASET, 'cocci', spfile) + ' ' + srcPath + ' --patch -o' + join(
            DATA_PATH, "codeflaws", bugName, 'patches', patchName) + ' > ' + join(DATA_PATH, "codeflaws", bugName,
                                                                                   'patches',
                                                                                   patchName + spfile + '.txt')

        output, e = shellGitCheckout(cmd)
    # logging.info(output)
    patchSize = os.path.getsize(join(DATA_PATH,"codeflaws",bugName,'patches',patchName+spfile+'.txt'))
    if patchSize == 0 :
        # os.remove(join(DATA_PATH,"introclass",bugName,'patches',patchName+spfile+'.txt'))
        return None
    else:

        cmd = 'patch -d '+'/'.join(srcPath.split('/')[:-1])+' -i '+join(DATA_PATH,"codeflaws",bugName,'patches',patchName+spfile+'.txt')+' -o '+join(DATA_PATH,"codeflaws",bugName,'patched',patchName+spfile+'.c')
        o,e = shellGitCheckout(cmd)
        return join(DATA_PATH, "codeflaws", bugName, 'patched', patchName + spfile + '.c')

def getTestList(path):
    files = listdir(path)
    # inputs = [i for i in files if i.startswith('input-')]
    inputs = [i for i in files if i.startswith('heldout-input-')]
    return inputs


def readTestSuite(testPath):
    regex = r"([p|n0-9]+)\)"
    with open(testPath,mode='r') as testFile:
        test_str = testFile.read()
    matches = re.finditer(regex, test_str, re.MULTILINE)

    testList = []
    for matchNum, match in enumerate(matches, start=1):

         for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            testList.append(match.group(groupNum))
    return testList

def test_all(testerPath,validTests,testPath):
    test_outcomes = {}  # type: Dict[TestCase, TestOutcome]
    failure_cases = []
    failure = 0
    total = len(validTests)
    #remove prev outputs
    [os.remove(join(testPath, i)) for i in listdir(testPath) if i.endswith('my_output')]
    for test in validTests:
        # if test.name in validTests:
        # cmd = testerPath + ' < {} '.format(join(testPath,test))

        outpos = test.replace('input-','output-')
        # cmd = 'diff -u --brief -w {} <( '.format(join(testPath,outpos))+testerPath+' < {} )'.format(join(testPath,test))
        cmd = 'bash ' + join(ROOT_DIR,'data' , 'test-valid2.sh') + ' {} {} {} {} '.format(join(testPath, test),
                                                                              join(testPath, outpos), testerPath, join(testPath,'time.out'))
        out,e = shellGitCheckout(cmd)


        if 'Accepted' not in out or e != '':
        # if 'Accepted' not in out :
            failure += 1
            failure_cases.append(test)
            # test_outcomes.append(out.output)
            break

        # test_outcomes[test] = client.containers.test(container, test)
        # if test.expected_outcome != test_outcomes[test].passed:
        # if test_outcomes[test].passed != True:
        #     failure.append(test.name)
        #     failure_cases.append(test.command)
        #     break
    return failure_cases, failure, total

def validateCore(bugName):

    if not os.path.exists(join(DATA_PATH, 'codeflaws', bugName, 'patches')):
        os.makedirs(join(DATA_PATH, 'codeflaws', bugName, 'patches'))
    if not os.path.exists(join(join(DATA_PATH, 'codeflaws', bugName, 'patched'))):
        os.makedirs(join(DATA_PATH, 'codeflaws', bugName, 'patched'))

    fix = 'failure'
    output = ''
    # print("bugName: {}".format(bugName), end=' ')
    output += 'bugName:' + bugName + ', '

    # spfiles = listdir(join(DATASET, 'cocci'))
    spfiles = load_zipped_pickle(join(DATA_PATH, 'uniquePatternsMod.pickle'))

    # spfiles['uProjects'] = spfiles.uFiles.apply(lambda x: list(set([i.split('/{')[0].replace('(','') for i in x])))
    # spfiles = spfiles[~spfiles.uProjects.apply(lambda x: np.all([i == 'codeflaws' for i in x]))]
    spfiles.sort_values(by='uFilenames',inplace=True,ascending=False)
    spfiles = spfiles[['uid']]


    cmd = 'make -C ' + join(DATA_PATH, 'codeflaws', bugName) + ' clean'
    o, e = shellGitCheckout(cmd)
    # print("patching... " + bugName)

    contestid, problem, _, buggyId, acceptedId = bugName.split('-')


    # for idx, spfile in enumerate(spfiles):
    for idx, spfile in enumerate(spfiles.uid.values.tolist()):
        if spfile == '.DS_Store':
            continue

        # originalBugs = get_filepaths(join(DATA_PATH, 'manybugs', bugName, 'diffs'), preId)
        buggyFileName = contestid+'-'+problem+'-'+buggyId+'.c'
        path = join(DATA_PATH,'codeflaws',bugName,buggyFileName)
        patch = patchSourceFile(path, spfile, bugName)

        times = 0
        if patch is None:
            continue

        shutil.copy2(patch,join(DATA_PATH, 'codeflaws', bugName))

        cmd = 'make -C ' + join(DATA_PATH, 'codeflaws', bugName) + ' FILENAME=' + bugName + spfile
        o, e = shellGitCheckout(cmd)


        # patch_result = output
        # TODO logic
        # if patch_result.successful:
        if isfile(join(DATA_PATH,'codeflaws',bugName,bugName+spfile)):

            cmd = 'mv ' + join(DATA_PATH,'codeflaws',bugName,bugName+spfile) + ' ' + join(DATA_PATH,'codeflaws',bugName,contestid+'-'+problem+'-'+buggyId)
            o, e = shellGitCheckout(cmd)

            output += '@True:' + str(idx) + ':' + patch.split('/')[-1] + '@'
            validTests = getTestList(join(DATA_PATH, 'codeflaws', bugName))
            # validTests = readTestSuite(join(DATA_PATH, 'codeflaws', bugName, 'test-valid.sh'))
            post_failure_cases, post_failure, total = test_all(join(DATA_PATH, 'codeflaws', bugName, contestid+'-'+problem+'-'+buggyId), validTests, join(DATA_PATH, 'codeflaws', bugName))

            # print("{}".format(post_failure), end=' ')
            output += str(post_failure) + ' '
            if post_failure == 0:
                times += 1
                fix = 'success'
                # print("fix {} by {}".format(bugName, patch_name))
                output += 'fix {} by {} '.format(bugName, patch)
                break
            # print("@fail:{}@total:{}".format(post_failure, total),end=' ')
            # print("@post_failure_cases:{}".format(post_failure_cases))

            # cmd = 'docker rm -fv {}'.format(container.id)
            # out, e = shellGitCheckout(cmd)

    output += 'times:{}, '.format(times) + fix
    print(output)
    return output

    #         failure_cases, failure, total, test_outcomes = test_all(bug, container, client)
    #         if failure == 0:
    #             fix = 'success'
    #             # print("fix {} by {}".format(bugName, patch_name))
    #             output += 'fix {} by {} '.format(bugName, patch)
    #             break
    #         else:
    #             output += ' {}'.format(failure_cases)
    #     else:
    #         output += '@False:' + str(idx) + ':' + patch.split('/')[-1] + '@'
    # output += 'times:{}, '.format(times) + fix
    #
    # return output

def validate():
     # validateCore('405-B-bug-6537621-6537728')
     bugs2test= listdir(join(DATA_PATH, 'codeflaws'))
     bugs2test.sort()

     bugList = []
     for b in bugs2test:
         if b == '.DS_Store' or b == 'README.md' or b == 'codeflaws-defect-detail-info.txt' or b.endswith('.tar.gz'):
             continue
         bugList.append(b)
         # if b == '476-A-bug-16608008-16608059':
         #    bugList.append(b)

     # results = parallelRunMerge(testCore, bugList,max_workers=10)
     results = parallelRunMerge(validateCore, bugList)
     print('\n'.join(results))
     with open(join(DATA_PATH, 'codeFlawsResultsuFilenames'), 'w',
               encoding='utf-8') as writeFile:
         writeFile.write('\n'.join(results))
         validateCore(b)