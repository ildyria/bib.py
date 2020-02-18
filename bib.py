#!/usr/bin/env python3

import os
import sys
import re
import argparse

config = {}

# Cf manual of bibtex: https://ctan.org/pkg/bibtex
# in short: https://nwalsh.com/tex/texhelp/bibtx-7.html
BIBTEX = {
    # An article from a journal or magazine.
    'ARTICLE': [['author', 'title', 'journal', 'year'], ['volume', 'number', 'pages', 'month', 'note']],
    # A book with an explicit publisher.
    'BOOK': [['author', 'editor', 'title', 'publisher', 'year'], ['volume', 'number', 'series', 'address', 'edition', 'month', 'note']],
    # A book with an explicit publisher.
    'BOOKLET': [['author', 'editor', 'title', 'publisher', 'year'], ['volume', 'number', 'series', 'address', 'edition', 'month', 'note']],
    # An article in a conference proceedings.
    'CONFERENCE': [['author', 'title', 'booktitle', 'year'], ['editor', 'volume', 'number','series', 'pages', 'address', 'month', 'organization', 'publisher', 'note']],
    # A part of a book, which may be a chapter.
    'INBOOK': [['author', 'editor', 'title', 'chapter', 'pages', 'publisher', 'year'], ['volume', 'number', 'series', 'type', 'address', 'edition', 'month', 'note']],
    # A book with an explicit publisher.
    'INCOLLECTION': [['author', 'title', 'booktitle', 'publisher', 'year'], ['editor', 'volume', 'number', 'series', 'type', 'chapter', 'pages', 'address', 'edition', 'month', 'note']],
    # An article in a conference proceedings.
    'INPROCEEDINGS': [['author', 'title', 'booktitle', 'year'], ['editor', 'volume', 'number','series', 'pages', 'address', 'month', 'organization', 'publisher', 'note']],
    # Technical documentation
    'MANUAL': [['title'], ['author', 'organization', 'address', 'edition', 'month', 'year', 'note']],
    # A Master’s thesis
    'MASTERSTHESIS': [['author', 'title', 'school', 'year'], ['type', 'address', 'month', 'note']],
    # Use this type when nothing else fits
    'MISC': [[], ['author', 'title', 'howpublished', 'month', 'year', 'note']],
    # A PhD thesis
    'PHDTHESIS': [['author', 'title', 'school', 'year'], ['type', 'address', 'month', 'note']],
    # The proceedings of a conference.
    'PROCEEDINGS': [['title', 'year'], ['editor', 'volume', 'number','series', 'address', 'month', 'organization', 'publisher', 'note']],
    # A document having an author and title, but not formally published
    'TECHREPORT': [['author', 'title', 'institution', 'year'], ['type', 'number', 'address', 'month', 'note']],
    # A document having an author and title, but not formally published
    'UNPUBLISHED': [['author', 'title', 'note'], ['month', 'year']],
}



def Red(skk): return "\033[38;5;009m {}\033[00m".format(skk)
def Green(skk): return "\033[38;5;010m {}\033[00m".format(skk)
def Yellow(skk): return "\033[38;5;011m {}\033[00m".format(skk)
def Orange(skk): return "\033[38;5;202m {}\033[0m".format(skk)
def LightPurple(skk): return "\033[38;5;177m {}\033[00m".format(skk)
def Purple(skk): return "\033[38;5;135m {}\033[00m".format(skk)
def Cyan(skk): return "\033[38;5;014m {}\033[00m".format(skk)
def LightGray(skk): return "\033[38;5;252m {}\033[00m".format(skk)
def DarkGray(skk): return "\033[38;5;242m {}\033[00m".format(skk)

def debug(t):
    if config['debug']:
        print(t)

def diagnostic(t):
    if config['diagnostic']:
        print(t)

def save(fn, z):
    d = open(fn, 'w', encoding="utf-8")
    d.write(z)
    d.close()

def read(fn):
    data = '';
    with open(fn, 'r', encoding="utf-8") as file:
        data = file.read()

    return data.split('\n')



## block parsing of the data in the bibtex

def find_end_block(data, i):
    if data[i].strip()[:1] == '}':
        return i;
    if data[i].strip()[:1] == '@':
        return -1;
    else:
        return find_end_block(data, i + 1);

def find_block(data, i, list_block):
    if len(data)  == i:
        return list_block;

    if data[i].strip()[:1] == '@':
        end = find_end_block(data, i + 1);
        if end == -1:
            # this is a single line case or there is an error in the bibliography.
            list_block.append([i,i])
            return find_block(data, i + 1, list_block)
        else:
            list_block.append([i,end])
            return find_block(data, end + 1, list_block)

    else:
        # we are out of a block, we look for the next @
        return find_block(data, i + 1, list_block)



# now that we have the block, let's look at what is the content of each.
def find_subblock_end(block, i):
    if len(block) == i:
        return i - 1
    if block[i][-2:] == '},' or block[i][-2:] == '",':
        return i
    else:
        return find_subblock_end(block, i + 1)

def find_subblock(block, i, list_subblock):
    if len(block) == i:
        return list_subblock;
    if block[i] == '':
        return find_subblock(block, i+1, list_subblock)

    idx = block[i].find('=');
    if idx != -1:
        idx2 = block[i].find('{');
        if idx2 != -1:
            end = find_subblock_end(block, i)
        else:
            idx2 = block[i].find('"');
            if idx2 != -1:
            	end = find_subblock_end(block, i)
            else:
            	end = i
        list_subblock.append([i,end,idx])
        return find_subblock(block, end+1, list_subblock)
    else:
        print(Red("this should not happen"))
        return list_subblock;


def find_section(parts, section):
    for p in parts:
        if p[0] == section:
            return p[1]
    return 'not found'

def find_section_index(parts, section):
    i = 0
    for p in parts:
        if p[0] == section:
            return i
        i += 1
    return -1

def extract_subblock(block, start, end, eq):
    s = slice(start, end + 1, 1)

    k = block[s][0][0:eq].strip()
    # this is to remove the _ we add for non recognized sections
    # this is useful if we want to change the kind: Misc -> article etc...
    if k[:1] == '_':
        k = k[1:]

    c = ' '.join(block[s])[eq+1:].strip()
    if c[-1:] == ',':
        c = c[:-1]
    c = re.sub(' +', ' ',c)
    debug((k,c))
    return [k,c]



def parse(block, output):
    debug(DarkGray('--------------------------------'))
    i = block[0].find('{')
    kind = block[0][1:i]
    debug(DarkGray(kind))
    referer = block[0][i+1:-1]
    debug(DarkGray(referer))
    sub_blocks = find_subblock(block,1,[])
    debug(DarkGray(sub_blocks))
    sections = []
    for sub in sub_blocks:
        sections.append(extract_subblock(block, sub[0], sub[1], sub[2]))
    output.append({'kind': kind, 'referer': referer, 'sections': sections})



# differenciate the onliners from the actual blocks
def parse_blocks(list_block, content, oneliners, blocks):
    temp_block = []
    for cut in list_block:
        if cut[0] == cut[1]:
            oneliners.append(content[cut[0]])
        else:
            s = slice(cut[0], cut[1], 1)
            temp_block.append(content[s]);

    debug(DarkGray('++++++++++++++++++++++++++++++++'))
    for b in temp_block:
        parse(b, blocks)
    debug(DarkGray('++++++++++++++++++++++++++++++++'))


def authors(s):
    list_authors = s.split(' and ')
    out = ''
    if len(list_authors) > 0:
        out = list_authors[0]
        for i in range(1, len(list_authors)):
            out += ' and\n'
            out += ''.rjust(20) + list_authors[i]
    return out

def block_to_referer(block):
    return block['referer']

def generate_entry(block, summary):
    output = '\n';
    kind = block['kind'].upper();
    c_kind = Yellow(kind).ljust(13)

    referer = block['referer'];
    c_referer = Orange(referer).ljust(40)

    output += '@{}{{{},\n'.format(kind.lower(),referer)

    if kind not in BIBTEX:
        print(Red('DROPPED:') + '{} {}'.format(c_kind, c_referer))
    else:
        diagnostic(c_kind + ' ' + c_referer)
        # mandatory blocks:
        for i,t in {0: 'mandatory', 1: 'optional'}.items():
            diagnostic(DarkGray('{}---------------------------'.format(t.ljust(9,'-'))))
            if len(BIBTEX[kind][i]) > 0 and i > 0:
                output += '\n'
            for s in BIBTEX[kind][i]:
                idx = find_section_index(block['sections'], s)

                if idx == -1:
                    diagnostic(Red('field not found:'.ljust(17)) + s)
                    if i != 1 or config['extend']:
                        output += '  {:15}= {},\n'.format(s,'{}')

                    if i == 0 and config['summary']:
                        summary.append(c_kind + ' ' + c_referer)
                        summary.append(Red('field not found:'.ljust(17)) + s)

                else:
                    c = block['sections'].pop(idx)[1]
                    if c == '' or c == '{}':
                        diagnostic(Red('field not found:'.ljust(17)) + s)
                        if config['extend']:
                            output += '  {:15}= {},\n'.format(s,'{}')
                        if i == 0 and config['summary']:
                            summary.append(c_kind + ' ' + c_referer)
                            summary.append(Red('field not found:'.ljust(17)) + s)
                    else:
                        diagnostic(Green('field found:'.ljust(17)) + s.ljust(13) + c)
                        if s == 'author':
                            c = authors(c)
                        output += '  {:15}= {},\n'.format(s,c)

        if len(block['sections']) > 0:
            block['sections'].sort(key=lambda a : a[0])
            diagnostic(DarkGray('{}---------------------------'.format('ignored'.ljust(9,'-'))))
            output += '\n'
            for b in block['sections']:
                diagnostic(LightPurple('extra field:'.ljust(17)) + b[0].ljust(13) + b[1])
                if not config['purify']:
                    output += '  _{:14}= {},\n'.format(b[0],b[1])

        diagnostic(DarkGray('{}---------------------------'.format('done'.ljust(9,'-'))))

    output += '}\n'
    return output

def is_not_bib(s):
    return s != '' and s[-4:] != '.bib'

def check_bib(s):
    if is_not_bib(s):
        msg = "%r is not a .bib" % s
        raise argparse.ArgumentTypeError(msg)
    return s

def chose_file(fn = ''):
    while fn == '' or is_not_bib(fn):
        if fn != '':
            print("{} is not a proper bibtex file".format(fn))
        fn = input('Please chose a correct file: ')
    return fn

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1", "y")

def list_duplicate_referer(blocks):
    mapped = [block_to_referer(b) for b in blocks];
    duplicates = [Orange('\t{}'.format(r)) for r in mapped if mapped.count(r) > 1];
    if len(duplicates) == 0:
        print(Green("No duplicate referers found."))
    else:
        print(Orange("Duplicates referers:"));
        for t in set(duplicates):
            print(t) 


def parse_arguments():
    parser = argparse.ArgumentParser(description='Normalize a decently formatted bibtex.')
    parser.add_argument('input', nargs='?', default='', help='input: file.bib', type=check_bib)
    parser.add_argument('-o','--output', nargs='?', default='', help='ouput: file.bib', type=check_bib)
    parser.add_argument('-v','--verbose', action='store_true', help='enable debugger output')
    parser.add_argument('--diagnostic', action='store_true', help='check for missing fields (all)')
    parser.add_argument('--no-summary', action='store_true', help='Don\'t check for missing fields (only mandatory)')
    parser.add_argument('--extend', action='store_true', help='if a field is missing, add it to the generated bibtex.')
    parser.add_argument('-p','--purify', action='store_true', help='extra fields are stripped from the generated bibtex.')
    parser.add_argument('-i','--interactive', action='store_true', help='Interactive.')
    parser.add_argument('-y','--yes', action='store_true', help='Override Interactive and select default answer.')
    parser.add_argument('-dr','--dry-run', action='store_true', help='Dry-run.')
    parser.add_argument('-l','--list-duplicates', action='store_true', help='List duplicate referers.')
    args = parser.parse_args()

    # print(args)
    interactive = args.interactive or args.input == ''
    if not interactive:
        config['debug'] = args.verbose
        config['diagnostic'] = args.diagnostic
        config['summary'] = not args.no_summary
        config['extend'] = args.extend
        config['purify'] = args.purify
        config['input'] = args.input
        config['output'] = args.output if args.output != '' else args.input
        config['dry_run'] = args.dry_run
        config['list-duplicates'] = args.list_duplicates
        debug(args)
        debug(config)
        return

    # we are in interactive mode
    # are we in YES mode ?
    # 1. do we have a file name ?
    fn = ''
    bibfiles = [x for x in os.listdir('.') if x[-4:] == '.bib']
    if args.input != '':
        fn = args.input
    elif len(bibfiles) == 1:
        fn = bibfiles[0]

    if args.yes and fn != '':
        config['input'] = fn
    elif args.yes and fn == '':
        print(Red("Could not select automatically the bibtex file."))
    elif fn != '':
        tmp = input('Input file [{}]: '.format(fn))
        if tmp == '':
            config['input'] = fn
        else:
            config['input'] = chose_file(tmp)
    elif len(bibfiles) > 2:
        fn = input('Multiple bibtex files found, please chose: '+', '.join(bibfiles))
        config['input'] = chose_file(fn)
    else:
        fn = input('No bibtex files found, please enter a file name: ')
        config['input'] = chose_file(fn)

    if args.yes:
        config['debug'] = args.verbose
        config['diagnostic'] = args.diagnostic
        config['summary'] = not args.no_summary
        config['extend'] = args.extend
        config['purify'] = args.purify
        config['output'] = args.output if args.output != '' else config['input']
        config['dry_run'] = args.dry_run
        config['list-duplicates'] = args.list_duplicates
    else:
        v = args.verbose
        tmp = input('Enable verbose mode [{}]? '.format('Y/n' if v else 'y/N'))
        config['debug'] = str2bool(tmp if tmp != '' else ('Y' if v else 'n'))
        v = args.diagnostic
        tmp = input('Enable Diagnostics [{}]? '.format('Y/n' if v else 'y/N'))
        config['diagnostic'] = str2bool(tmp if tmp != '' else ('Y' if v else 'n'))
        v = not args.no_summary
        tmp = input('Enable Summary [{}]? '.format('Y/n' if v else 'y/N'))
        config['summary'] = str2bool(tmp if tmp != '' else ('Y' if v else 'n'))
        v = args.extend
        tmp = input('Add missing field [{}]? '.format('Y/n' if v else 'y/N'))
        config['extend'] = str2bool(tmp if tmp != '' else ('Y' if v else 'n'))
        v = args.purify
        tmp = input('Remove unnecessary fields [{}]? '.format('Y/n' if v else 'y/N'))
        config['purify'] = str2bool(tmp if tmp != '' else ('Y' if v else 'n'))
        v = args.dry_run
        tmp = input('Dry-run [{}]? '.format('Y/n' if v else 'y/N'))
        config['dry_run'] = str2bool(tmp if tmp != '' else ('Y' if v else 'n'))
        v = args.list_duplicates
        tmp = input('List duplicates [{}]? '.format('Y/n' if v else 'y/N'))
        config['list-duplicates'] = str2bool(tmp if tmp != '' else ('Y' if v else 'n'))

        fn = args.output if args.output != '' else config['input']
        fn = input('Output file [{}]:'.format(fn))
        if fn == '':
            fn = config['input']
        config['output'] = fn

    debug(args)
    debug(config)

def main():

    parse_arguments()

    if not os.path.isfile(config['input']):
        print(Red('File not found!'))
        return

    content = read(config['input'])
    list_block = find_block(content, 0, []);

    oneliners = []
    blocks = []

    # differenciate the onliners from the actual blocks
    parse_blocks(list_block, content, oneliners, blocks)

    blocks.sort(key=lambda a : a['referer'])

    for p in blocks:
        debug(DarkGray(p['kind']))
        debug(DarkGray(p['referer']))
        for s in p['sections']:
            debug(DarkGray((s)))

    output = ''
    summary = []

    for p in oneliners:
        output += p + '\n'
    for p in blocks:
        output += generate_entry(p, summary)

    if config['dry_run']:
        print(output)
    else:
        if config['input'] == config['output']:
            print(DarkGray('Input file is the same as output file, we will generate a backup at {}.bck'.format(config['input'])))
            os.rename(config['input'], config['input']+'.bck')
        save(config['output'], output)

    for s in summary:
        print(s)

    if config['list-duplicates']:
    	list_duplicate_referer(blocks);

main();
