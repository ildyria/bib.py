# check-bib
Simple script to align and check your file.bib.

## Quick download

```
wget https://raw.githubusercontent.com/ildyria/bib.py/master/bib.py | python3 -
```

## What does it ?

This script aims to improve your bib file without modifying its content:
- fix alignments
- order entries alphabetically
- warn about missing fields

it also comes with the following options:

```
▶ ./bib.py -h
usage: bib.py [-h] [-o [OUTPUT]] [-v] [--diagnostic] [--no-summary] [--extend]
              [-p] [-i] [-y] [-dr]
              [input]

Normalize a decently formatted bibtex.

positional arguments:
  input                 input: file.bib

optional arguments:
  -h, --help            show this help message and exit
  -o [OUTPUT], --output [OUTPUT]
                        ouput: file.bib
  -v, --verbose         enable debugger output
  --diagnostic          check for missing fields (all)
  --no-summary          Don't check for missing fields (only mandatory)
  --extend              if a field is missing, add it to the generated bibtex.
  -p, --purify          extra fields are stripped from the generated bibtex.
  -i, --interactive     Interactive.
  -y, --yes             Override Interactive and select default answer.
  -dr, --dry-run        Dry-run.
```



## Examples

![](screenshots/cmd-options.png)
![](screenshots/summary-example.png)
