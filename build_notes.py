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

    # Theorem pages generation zone.
    def __get_theorems(self, file: str, theorem: str) -> list[str]:
        """
        Get the theorems from the latex file.
        :param file: The latex file to get the theorems from.
        :param file: str
        :param theorem: The theorem to get the theorems for.
        :param theorem: str
        :return: list[str]
        """
        with open(file, 'r') as f:
            file = f.read()
            matches = None
            try:
                theorem_re = r'(?s)(?<=\\begin{' + theorem + r'}).*?(?=\\end{' + theorem + r'})'
                matches = re.findall(theorem_re, file)
            except Exception:
                print("No definitions for this chapter found.")
            return matches

    def __parse_theorems(self, matches, matches_comp: list) -> None:
        """
        Get the hyperlink section of the theorem.
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

    def __craft_theorem_page(self, matches_comp: list, theorem: str) -> None:
        """
        Craft the theorem page with all the theorems and sections/subsections.
        :param matches_comp: List of matches to append to.
        :param matches_comp: list[str]
        :param theorem: The theorem to craft the theorem page for.
        :param theorem: str
        :return: None
        """
        with open(f"{self.note_dir}/{theorem}s.tex", 'r') as f:
            file = f.read()
        theorem_cap = theorem[0].upper() + theorem[1:] + 's'
        file = "\setcounter{chapter}{" + str(self.chapter_counter - 1) + "}\n\chapter{" + theorem_cap + "}\n"
        self.chapter_counter += 1
        sections = []
        section_template = '\section{'
        theorem_template_0 = '\n\subsection{'
        theorem_template_1 = '}\hyperref['
        theorem_template_2 = ']{link}\n\n'
        # Generate sections alphabetically.
        for match in matches_comp:
            section = section_template + match[2][0] + '}\n'
            full_theorem = theorem_template_0 + match[2] + theorem_template_1 + match[1] + theorem_template_2 + match[2]
            if section not in sections:
                sections.append(section)
                file = file + sections[-1] + full_theorem
            else:
                file = file.replace(section, section + full_theorem)
        with open(f"{self.note_dir}/{theorem}s.tex", 'w') as f:
            f.write(file)

    def __fill_theorem_page(self, theorem: str) -> None:
        """
        Extract and generate a page with all theorems.
        :param theorem: The theorem to generate the theorems page for.
        :param theorem: str
        :return: None
        """
        # [match_str, hyperref, theorem_name, theorem_text]
        matches_comp = []
        # Extract the theorems.
        for f in os.listdir(self.note_dir):
            if re.search(r'(?<=chpt_).*(?=.tex)', f):    
                matches = self.__get_theorems(f'{self.note_dir}/{f}', theorem)
                self.__parse_theorems(matches, matches_comp)
        # Create the {theorem}s.tex file.
        if os.path.exists(f"{self.note_dir}/{theorem}s.tex"):
            subprocess.call(f"rm {self.note_dir}/{theorem}s.tex", shell=True)
        subprocess.call(f"touch {self.note_dir}/{theorem}s.tex", shell=True)
        self.__craft_theorem_page(matches_comp, theorem)

    def __gen_theorems_pages(self) -> None:
            """
            Generate all theorem pages.
            :return: None
            """
            with open(f"{self.note_dir}/main_temp.tex", 'r') as f:
                main_file = f.read()
            with open('lib/preamble.tex', 'r') as f:
                preamble_file = f.read()
            f.close()
            matches_l1 = re.findall(r'(?s)(?<=\\declaretheorem).*?(?=\\)', preamble_file)
            temp: str = ''
            for match in matches_l1:
                temp += match + '\n'
            self.declared_theorems = re.findall(r'(?s)(?<={).*?(?=})', temp)
            for theorem in self.declared_theorems:
                theorem_input = r'\\input{' + theorem + 's.tex}' 
                try:
                    re.search(theorem_input, main_file).group(0)
                    self.__fill_theorem_page(theorem)
                except Exception:
                    pass
    
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
        temp = ''
        for theorem in self.declared_theorems:
            theorem = theorem + 's.tex'
            temp += theorem + ' '
        subprocess.call(f'rm -f *.dvi *.ptc *.log *.aux *.toc *.out', shell=True, cwd=self.note_dir)
        subprocess.call(f'rm -f preamble.tex main_temp.tex {temp}', shell=True, cwd=self.note_dir)

    def build_notes(self, note) -> None:
        """
        Build the notes
        :param notes: The notes to build.
        :param notes: list
        :return: None
        """
        self.note = note
        self.note_dir = os.path.join('./src', note)
        self.__gen_preamble()
        self.__update_chapter_numbers()
        self.__gen_theorems_pages()
        # Call __build_notes() twice since Table of Contents isn't added properly the first time with (funny business with pdflatex).
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
