import argparse
import os
import softwarePico.version as vers

parser = argparse.ArgumentParser(
    prog='python3 ./PYMakefile.py',
    description='Utility functions for building microPython bytecode and automating development tasks of the OPMS software.')		

parser.add_argument('--bytecode', help='compile to bytecode', action="store_true")
parser.add_argument('--verbose', help='will show extended output', action="store_true")
args = parser.parse_args()

exclude_files = ['main.py', 'config.py','__init__.py']
mpy_cross = '../micropython/mpy-cross/build/mpy-cross'

if args.bytecode:
    print('compiling to bytecode...')
    for fpath,fnames in vers.all_files.items():
        for fname in fnames:
            if (fname not in exclude_files) and (fname.split('.')[1] == 'py'):
                infile = './softwarePico-src' + fpath + fname
                outfile = './softwarePico-dist' + fpath + fname.split('.')[0] + '.mpy'
                print('compiling ' + infile)
                comd = mpy_cross + ' ' + infile + ' -o ' + outfile
                if args.verbose:
                    print(comd)
                os.popen(comd)
                
