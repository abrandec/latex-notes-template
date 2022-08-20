![pdf gen](https://github.com/abrandec/latex-notes-template/actions/workflows/pdf_gen.yml/badge.svg)

# LaTeX Notes Template

Template for creating LaTeX notes.

## Dependencies
- [Python 3.10](https://www.python.org/downloads/release/python-3100/)
- [pdflatex](https://pypi.org/project/pdflatex/)

## Getting Started
```
# Clone this repository
$ git clone https://github.com/abrandec/latex-notes-template

# Go into the repository
$ cd latex-notes-template

# create a copy the sample_notes in src to start with
$ cp -r src/sample_notes src/NOTE_NAME
```

## Compiling Notes
```
# Compiling a single note
$ ./build_notes.py -note NOTE_NAME

# Compiling all notes in the src directory
$ ./build_notes.py -note all
```

## Cleaning Build Directory
```
$ ./build_notes.py -clean
```

## License
[MIT](https://github.com/abrandec/latex-notes-template/blob/main/MIT-LICENSE.txt)
