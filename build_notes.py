#!/usr/bin/env python3
import subprocess
import os, sys, getopt, re

def gen_preamble(note) -> None:
    """
    Generate the preamble for the notes.
    :param note: The note to generate the preamble for.
    :param note: str
    :return: None
    """
    author = ''
    author_latex = '\n\\author '
    if os.path.exists('.cfg'):
        with open('.cfg', 'r') as f:
            for line in f:
                author = re.search('(?<=Author: ).*(?=)', line).group(0)
                if author != '':
                    author_latex = author_latex + '{' + author + '}' + '\n'
                    break
    else:
        print("No .cfg file found.")
        sys.exit()
    note_dir = os.path.join('./src', note)
    if os.path.exists(f"{note_dir}/preamble.tex"):
        subprocess.call(f"rm {note_dir}/preamble.tex", shell=True)
    subprocess.call(f"cp lib/preamble.tex {note_dir}/preamble.tex", shell=True)
    with open(f"{note_dir}/preamble.tex", 'a') as f:
        f.write(f"{author_latex}")

def __build_notes(note) -> None:
    """
    Build the notes.
    :param note: The note to build using pdflatex & cleanup with latexmk.
    :param note: str
    :return: None
    """
    note_dir = os.path.join('./src', note)
    # Build the note.
    subprocess.call('pdflatex main.tex', shell=True, cwd=note_dir) 
    # Move the pdf to the build directory
    if os.path.exists(os.path.join(note_dir, 'main.pdf')):     
        if not os.path.exists(f'./build/{note}'):
            os.makedirs(f'./build/{note}')
        if os.path.exists(f'./build/{note}.pdf'):
           subprocess.call(f'rm ./build/{note}.pdf', shell=True)
        subprocess.call(f'mv main.pdf ../../build/{note}', shell=True, cwd=note_dir)
        # Rename the pdf to the note name.
        subprocess.call(f'mv build/{note}/main.pdf build/{note}/{note}.pdf', shell=True)
    
def build_notes(note) -> None:
    """
    Build the twice since LaTeX ain't acting right with creating the TOC.
    :param notes: The notes to build.
    :param notes: list
    :return: None
    """
    gen_preamble(note)
    __build_notes(note)
    __build_notes(note)

def clean_src(note) -> None:
    """
    Clean the build directory.
    :param note: The note to clean.
    :param note: str
    :return: None
    """
    note_dir = os.path.join('./src', note)
    subprocess.call(f'rm -f *.dvi *.ptc *.log *.aux *.toc *.out', shell=True, cwd=note_dir)
    subprocess.call(f'rm preamble.tex', shell=True, cwd=note_dir)

def main(argv) -> None:
    """
    main function.
    :param argv: The arguments passed to the script.
    :param argv: list
    :return: None
    """
    note = ''
    try:
        opts, _ = getopt.getopt(argv, "h:c:n:", ["help", "clean", "note="])
    except getopt.GetoptError:
        print('build-notes.py -n <note>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('build-notes.py -n <note>')
            print('clean the build dir: build-notes.py -clean')
            print('build all notes: build-notes.py -n all')
            sys.exit()
        elif opt in ("-c", "--clean"):
            for f in os.listdir("build"):
                if os.path.exists(f"build/{f}/{f}.pdf"):    
                    subprocess.call(f"rm build/{f}/{f}.pdf", shell=True)
            else:
                print("path: build does not exist")
        elif opt in ("-n", "--note"):
            note = arg
    if note == 'all':
        my_list = os.listdir('./src')
        for note in my_list:
            build_notes(note)
            clean_src(note)
    elif note != '':
        build_notes(note)
        clean_src(note)
    print("Notes built.")

if __name__ == "__main__":
    main(sys.argv[1:])
