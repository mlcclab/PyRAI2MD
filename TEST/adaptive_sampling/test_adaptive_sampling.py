######################################################
#
# PyRAI2MD test adaptive sampling
#
# Author Jingbai Li
# Oct 19 2021
#
######################################################

import os, sys, shutil, json, subprocess

def TestAdaptiveSampling():
    """ adaptive sampling test

    1. adaptive sampling with energy grad soc training and prediction

    """
    pyrai2mddir = os.environ['PYRAI2MD']
    testdir = '%s/adaptive_sampling' % (os.getcwd())
    record = {
        'energy'   : 'FileNotFound',
        'orbital'  : 'FileNotFound',
        'freq'     : 'FileNotFound',
        'data'     : 'FileNotFound',
        'input'    : 'FileNotFound',
        'model'    : 'FileNotFound',
        'MOLCAS'   : 'VariableNotFound',
        }

    filepath = '%s/TEST/adaptive_sampling/data/atod.inp' % (pyrai2mddir)
    if os.path.exists(filepath):
        record['energy'] = filepath

    filepath = '%s/TEST/adaptive_sampling/data/atod.StrOrb' % (pyrai2mddir)
    if os.path.exists(filepath):
        record['orbital'] = filepath

    filepath = '%s/TEST/adaptive_sampling/data/atod.freq.molden' % (pyrai2mddir)
    if os.path.exists(filepath):
        record['freq'] = filepath

    filepath = '%s/TEST/adaptive_sampling/data/atod.json' % (pyrai2mddir)
    if os.path.exists(filepath):
        record['data'] = filepath

    filepath = '%s/TEST/adaptive_sampling/data/input' % (pyrai2mddir)
    if os.path.exists(filepath):
        record['input'] = filepath

    filepath = '%s/TEST/adaptive_sampling/data/NN-atod' % (pyrai2mddir)
    if os.path.exists(filepath):
        record['model'] = filepath

    if 'MOLCAS' in os.environ:
        record['MOLCAS'] = os.environ['MOLCAS']

    summary = """
 *---------------------------------------------------*
 |                                                   |
 |         Adaptive Sampling Test Calculation        |
 |                                                   |
 *---------------------------------------------------*

 Check files and settings:
-------------------------------------------------------
"""
    for key, location in record.items():
        summary += ' %-10s %s\n' % (key, location)

    for key, location in record.items():
        if location == 'FileNotFound':
            summary += '\n Test files are incomplete, please download it again, skip test\n\n'
            return summary, 'FAILED(test file unavailable)'
        if location == 'VariableNotFound':
            summary += '\n Environment variables are not set, cannot find program, skip test\n\n'
            return summary, 'FAILED(enviroment variable missing)'

    CopyInput(record, testdir)

    summary += """
 Copy files:
 %-10s --> %s/atod.inp (renamed to atod.molcas)
 %-10s --> %s/atod.StrOrb
 %-10s --> %s/atod.freq.molden
 %-10s --> %s/atod.json
 %-10s --> %s/NN-atod
 %-10s --> %s/input

 Run Adaptive sampling:
""" % ('energy', testdir,
       'orbital', testdir,
       'freq', testdir,
       'data', testdir,
       'model', testdir,
       'input', testdir)

    results, code = RunSampling(record, testdir, pyrai2mddir)
   
    summary += """
-------------------------------------------------------
                Adaptive Sampling OUTPUT
-------------------------------------------------------
%s
-------------------------------------------------------
""" % (results)   
    return summary, code
 
def CopyInput(record, testdir):
    if os.path.exists(testdir) == False:
        os.makedirs(testdir)

    shutil.copy2(record['energy'], '%s/atod.molcas' % (testdir))
    shutil.copy2(record['orbital'], '%s/atod.StrOrb' % (testdir))
    shutil.copy2(record['freq'], '%s/atod.freq.molden' % (testdir))
    shutil.copy2(record['data'], '%s/atod.json' % (testdir))

    if os.path.exists('%s/NN-atod' % (testdir)) == True:
        shutil.rmtree('%s/NN-atod' % (testdir))
    shutil.copytree(record['model'], '%s/NN-atod' % (testdir))

    with open(record['input'], 'r') as infile:
        file = infile.read().splitlines()
    input = ''
    for line in file:
        if len(line.split()) > 0:
            if 'molcas' in line.split()[0]:
                input += 'molcas  %s\n' % (record['MOLCAS'])
            else:
                input += '%s\n' % (line)
        else:
            input += '%s\n' % (line)

    with open('%s/input' % (testdir), 'w') as out:
        out.write(input)

def Collect(testdir, title):
    with open('%s/%s.log' % (testdir, title), 'r') as logfile:
        log = logfile.read().splitlines()
    for n, line in enumerate(log):
        if """ Number of iterations:""" in line:
            results = log[n - 1:]
            break
    results = '\n'.join(results) + '\n'

    return results

def RunSampling(record, testdir, pyrai2mddir):
    maindir = os.getcwd()
    results = ''

    os.chdir(testdir)
    subprocess.run('python3 %s/pyrai2md.py input > stdout' % (pyrai2mddir), shell = True)
    os.chdir(maindir)
    tmp = Collect(testdir, 'atod')
    results += tmp

    if len(tmp.splitlines()) < 10:
        code = 'FAILED(adaptive sampling runtime error)'
        return results, code
    else:
        code = 'PASSED'
        results += ' adaptive sampling done\n'

    return results, code
