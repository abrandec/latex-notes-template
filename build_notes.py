#!/usr/bin/env python3
import subprocess
import os, sys, getopt, re

class Note_Generator:
    def __init__(self) -> None:
        """
        Initialize the class.
        :return: None
        """
        # Internal variables.
        self.note_dir = None
        self.note = None
        self.chapter_counter = 0

    def __gen_preamble(self) -> None:
        """
        Generate the preamble for the notes.
        :return: None
        """
        title = ''
        author = ''
        title_latex = r'\n\\title'
        author_latex = '\n\n\\author'
        cfg_dest = os.path.join(self.note_dir, '.cfg')
        if os.path.exists(cfg_dest):
            with open(cfg_dest, 'r') as f:
                file = f.read()
                title = re.search('(?<=Title: ).*(?=)', file).group(0)
                author = re.search('(?<=Author: ).*(?=)', file).group(0)
                title_latex = 'makeatother' + title_latex + '{' + title + '}'
                author_latex = author_latex + '{' + author + '}' + '\n' 
        else:
            print("No .cfg file found.")
            sys.exit()
        if os.path.exists(f"{self.note_dir}/preamble.tex"):
            subprocess.call(f"rm {self.note_dir}/preamble.tex", shell=True)
        subprocess.call(f"cp lib/preamble.tex {self.note_dir}/preamble.tex", shell=True)
        with open(f"{self.note_dir}/preamble.tex", 'a') as f:
            f.write(f"{author_latex}")
        if not os.path.exists(f"{self.note_dir}/main.tex"):
            print(f"{self.note_dir}/main.tex not found.")
            sys.exit()
        if os.path.exists(f"{self.note_dir}/main_temp.tex"):
            subprocess.call(f"rm {self.note_dir}/main_temp.tex", shell=True)
        subprocess.call(f"cp {self.note_dir}/main.tex {self.note_dir}/main_temp.tex", shell=True)
        with open(f"{self.note_dir}/main_temp.tex", 'r') as f:
            file = f.read()
            file = re.sub('(?:makeatother)', title_latex, file)
        with open(f"{self.note_dir}/main_temp.tex", 'w') as f:
            f.write(file)
    
    def __get_definitions(self, file) -> list[str]:
        """
        Get the definitions from the latex file.
        :param file: The latex file to get the definitions from.
        :param file: str
        :return: list[str]
        """
        with open(file, 'r') as f:
            file = f.read()
            matches = None
            try:
                matches = re.findall(r'(?s)(?<=\\begin{definition}).*?(?=\\end{definition})', file)
            except Exception:
                print("No definitions for this chapter found.")
            return matches

    def __parse_definitions(self, matches, matches_comp: list) -> None:
        """
        Get the hyperlink section of the definition.
        :param matches: Defintions to parse.
        :param raw_def: str
        :param matches_comp: List of matches to append to.
        :param matches_comp: list[str]
        """
        for match in matches:
            # Debug these regexes yourself.
            def_hyperref = re.search(r'(?s)(?<=\\label{).*?(?=})', match).group(0)
            def_name_re = r'(?s)(?<=' + def_hyperref + r'}' + r'\n).*?(?=\\newline)'
            def_name = re.search(def_name_re, match).group(0)
            def_name = def_name.strip()
            def_text_re = r'(?s)(?<=' + def_name + r' \\newline\n).*$'
            def_text = re.search(def_text_re, match).group(0)
            matches_comp.append([match, def_hyperref, def_name, def_text])
            # Sort definitions by alphabetical order.
            matches_comp.sort(key=lambda x: x[2])

    def __craft_definitions_page(self, matches_comp: list) -> None:
        """
        Craft the definitions page with all the definitions and sections/subsections.
        :param matches_comp: List of matches to append to.
        :param matches_comp: list[str]
        :return: None
        """
        with open(f"{self.note_dir}/definitions.tex", 'r') as f:
            file = f.read()
        file = "\setcounter{chapter}{" + str(self.chapter_counter - 1) + "}\n\chapter{Definitions}\n"
        sections = []
        section_template = '\section{'
        definition_template_0 = '\n\subsection{'
        definition_template_1 = '}\hyperref['
        definition_template_2 = ']{link}\n\n'
        # Generate sections alphabetically.
        for match in matches_comp:
            section = section_template + match[2][0] + '}\n'
            definition = definition_template_0 + match[2] + definition_template_1 + match[1] + definition_template_2 + match[3]
            if section not in sections:
                sections.append(section)
                file = file + sections[-1] + definition
            else:
                file = file.replace(section, section + definition)
        with open(f"{self.note_dir}/definitions.tex", 'w') as f:
            f.write(file)
        
    def __gen_definitions_page(self) -> None:
        """
        Extract and generate a page with all definitions.
        :return: None
        """
        # [match_str, hyperref, definition_name, definition_text]
        matches_comp = []
        # Extract the definitions.
        for f in os.listdir(self.note_dir):
            if re.search(r'(?<=chpt_).*(?=.tex)', f):    
                matches = self.__get_definitions(f'{self.note_dir}/{f}')
                self.__parse_definitions(matches, matches_comp)
        # Create the definitions.tex file.
        if os.path.exists(f"{self.note_dir}/definitions.tex"):
            subprocess.call(f"rm {self.note_dir}/definitions.tex", shell=True)
        subprocess.call(f"touch {self.note_dir}/definitions.tex", shell=True)
        self.__craft_definitions_page(matches_comp)
        
    def __update_chapter_numbers(self) -> None:
        """
        Update the chapter numbers in the note.
        :return: None
        """
        # Update the chapter numbers.
        for file_name in os.listdir(self.note_dir):
            try:
                chapter_num = re.search(r'(?<=chpt_).*(?=.tex)', file_name).group(0)
                replacement_counter = '\setcounter{chapter}{' + chapter_num + '}\n'
                if chapter_num == '0':
                    replacement_counter = '\setcounter{chapter}{-1}\n'       
                with open(f"{self.note_dir}/{file_name}", 'r') as f:
                    file = f.readlines()
                file[0] = replacement_counter
                with open(f"{self.note_dir}/{file_name}", 'w') as f:
                    f.writelines(file)
                self.chapter_counter += 1
            except Exception:
                continue

    def __build_notes(self) -> None:
        """
        Build the note.
        :return: None
        """
        # Build the note.
        subprocess.call('pdflatex main_temp.tex', shell=True, cwd=self.note_dir) 
        # Move the pdf to the build directory
        if os.path.exists(os.path.join(self.note_dir, 'main_temp.pdf')):     
            if not os.path.exists(f'./build/{self.note}'):
                os.makedirs(f'./build/{self.note}')
            if os.path.exists(f'./build/{self.note}.pdf'):
               subprocess.call(f'rm ./build/{self.note}.pdf', shell=True)
            subprocess.call(f'mv main_temp.pdf ../../build/{self.note}', shell=True, cwd=self.note_dir)
            # Rename the pdf to the note name.
            subprocess.call(f'mv build/{self.note}/main_temp.pdf build/{self.note}/{self.note}.pdf', shell=True)

    def __clean_src(self) -> None:
        """
        Clean the build directory.
        :return: None
        """
        note_dir = os.path.join('./src', self.note)
        subprocess.call(f'rm -f *.dvi *.ptc *.log *.aux *.toc *.out', shell=True, cwd=note_dir)
        subprocess.call(f'rm -f preamble.tex main_temp.tex definitions.tex', shell=True, cwd=note_dir)

    def build_notes(self, note) -> None:
        """
        Build the notes twice since LaTeX isn't acting right when creating the Table of Contents.
        :param notes: The notes to build.
        :param notes: list
        :return: None
        """
        self.note = note
        self.note_dir = os.path.join('./src', note)
        self.__gen_preamble()
        self.__update_chapter_numbers()
        with open(f"{self.note_dir}/main_temp.tex", 'r') as f:
                file = f.read()
        try:
            re.search(r'\\input{definitions.tex}', file).group(0)
            self.__gen_definitions_page()
        except Exception:
            pass
        self.__build_notes()
        self.__build_notes()
        self.__clean_src()

def main(argv) -> None:
    """
    Main function.
    :param argv: The arguments passed to the script.
    :param argv: list
    :return: None
    """
    note_gen = Note_Generator()
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
            note_gen.build_notes(note)
    elif note != '':
        note_gen.build_notes(note)
    print("Notes built.")

if __name__ == "__main__":
    main(sys.argv[1:])
