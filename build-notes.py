#!/usr/bin/env python3
from distutils.command.build import build
import subprocess
import os, sys, getopt

def __build_notes(note) -> None:
    """
    Build the notes.
    :param note: The note to build using pdflatex & cleanup with latexmk.
    :param note: str
    :return: None
    """
    note_dir = os.path.join('./src', note)
    # Build the note.
    subprocess.call('pdflatex master.tex', shell=True, cwd=note_dir)
    
    # Move the pdf to the build directory
    if os.path.exists(os.path.join(note_dir, 'master.pdf')):
        
        if not os.path.exists(f'./build/{note}'):
            os.makedirs(f'./build/{note}')
        if os.path.exists(f'./build/{note}.pdf'):
           subprocess.call(f'rm ./build/{note}.pdf', shell=True)
        subprocess.call(f'mv master.pdf ../../build/{note}', shell=True, cwd=note_dir)
        # Rename the pdf to the note name.
        subprocess.call(f'mv build/{note}/master.pdf build/{note}/{note}.pdf', shell=True)
    
def build_notes(note) -> None:
    """
    Build the twice since LaTeX ain't acting right with creating the TOC.
    :param notes: The notes to build.
    :param notes: list
    :return: None
    """
    __build_notes(note)
    __build_notes(note)

def clean_build(note) -> None:
    """
    Clean the build directory.
    :param note: The note to clean.
    :param note: str
    :return: None
    """
    note_dir = os.path.join('./src', note)
    subprocess.call('latexmk -c', shell=True, cwd=note_dir)
    files_to_remove = ('*.dvi', '*.ptc', '*.log')
    for f in os.listdir(note_dir):
        if f.endswith(files_to_remove):
            subprocess.call(f'rm {files_to_remove}', shell=True, cwd=note_dir)

def main(argv) -> None:
    """
    main function.
    :param argv: The arguments passed to the script.
    :param argv: list
    :return: None
    """
    note = ''
    try:
        opts, _ = getopt.getopt(argv,"hn:",["note="])
    except getopt.GetoptError:
        print('build-notes.py -n <note>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('build-notes.py -n <note>')
            print('build all notes: build-notes.py -n all')
            sys.exit()
        elif opt in ("-n", "--note"):
            note = arg
    if note == 'all':
        my_list = os.listdir('./src')
        for note in my_list:
            build_notes(note)
            clean_build(note)
    else:
        build_notes(note)
        clean_build(note)
    print("Notes built.")

if __name__ == "__main__":
    main(sys.argv[1:])