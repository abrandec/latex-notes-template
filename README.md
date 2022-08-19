# LaTeX Notes Template

This is a template for creating LaTex notes.

## Dependencies
[Python 3.10](https://www.python.org/downloads/release/python-3100/)
[pdflatex](https://pypi.org/project/pdflatex/)
[latexmk](https://ctan.org/pkg/latexmk/)

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
$ ./build-notes.py -note NOTE_NAME

# Compiling all notes in the src directory
$ ./build-notes.py -note all
```

## License
[MIT](https://github.com/abrandec/web_crawler/blob/main/MIT-LICENSE.txt)