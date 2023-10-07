import argparse, sys
import os
import softwarePico_src.version as vers

parser = argparse.ArgumentParser(
    prog='python3 ./PYMakefile.py',
    description='Utility functions for building microPython bytecode and automating development tasks of the OPMS software.')		

parser.add_argument('-a', '--all', help='compile to bytecode and sync static files', action="store_true")
parser.add_argument('--bytecode', help='compile to bytecode', action="store_true")
parser.add_argument('--syncfiles', help='sync static files', action="store_true")
parser.add_argument('--verbose', help='will show extended output', action="store_true")
args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

exclude_files = ['main.py','config.py','__init__.py']
mpy_cross = '../micropython/mpy-cross/build/mpy-cross'

def compile_bytecode():
    print('compiling to bytecode...')
    for fpath,fnames in vers.all_files.items():
        for fname in fnames:
            if (fname not in exclude_files) and (fname.split('.')[1] == 'mpy'):
                infile = './softwarePico_src' + fpath + fname.split('.')[0] + '.py'
                outfile = './softwarePico_dist' + fpath + fname.split('.')[0] + '.mpy'
                print('compiling ' + infile)
                comd = mpy_cross + ' ' + infile + ' -o ' + outfile
                if args.verbose:
                    print(comd)
                os.popen(comd)
            if fname in exclude_files:
                infile = './softwarePico_src' + fpath + fname
                outfile = './softwarePico_dist' + fpath + fname
                print('copying ' + infile)
                comd = 'cp ' + infile + ' ' + outfile
                if args.verbose:
                    print(comd)
                os.popen(comd)     

def syncfiles():
    print('syncing static files...')
    for fpath,fnames in vers.all_files.items():
        for fname in fnames:
            if (fname not in exclude_files) and (fname.split('.')[1] != 'mpy'):
                infile = './softwarePico_src' + fpath + fname
                outfile = './softwarePico_dist' + fpath + fname
                print('copying ' + infile)
                comd = 'cp ' + infile + ' ' + outfile
                if args.verbose:
                    print(comd)
                os.popen(comd)
    print('copying ./softwarePico_src/version.py')
    os.popen('cp ./softwarePico_src/version.py ./softwarePico_dist/version.py')


if args.bytecode:
    compile_bytecode()

if args.syncfiles:
    syncfiles()

if args.all:
    compile_bytecode()
    syncfiles()
