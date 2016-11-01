# -*- coding: utf-8 -*-
# Little tool to convert Markdown to cool LaTeX documents.
# Written by YoPox, Hadrien and pierrotdu18

# Import
import re
import sys

# Foo
global tikz_needed
tikz_needed = False

# Documentation
global doc

doc = """
mdConvert help
Full version

Usage :
    main.py <input> <options> (normal use of the function, provides a fresh .tex document)
    main.py --help (to get this text exactly)

Options :
    -o : shortcut for --output
    --ouput <output> : output file name (same as input file name by default)

    -d : shortcut for --date
    --date <date> : date of the document (none by default)

    -a : shortcut for --author
    --author <author> : author of the document (none by default)

    -t : shortcut for --title
    --title <title> : title of the document (none by default)

    -c : shortcut for --documentclass
    --documentclass <class> : document class (article by default)

    -p : shortcut for --packages
    --packages <pcks> : list of additionnal packages with syntax
                        {[options1]{package1},[options2]{package2},...}
                        (none by default)

    -T : shortcut for --tableofcontents
    --tableofcontents : if a table of contents is needed ('on' by default)

    -r : shortcut for --robot option
    --robot : put this option if you want to use RobotMono font for your code

    -l : shortcut for --lua
    --lua : put this option if you are intending to compile your .tex document with LuaLaTeX or not. It is automatically set to True if there are trees in your document.

Go to https://github.com/YoPox/mdConvert/ for more information
"""

# Managing arguments
global ARGV

ARGV = {
    'output': '',
    'input': '',
    'documentclass': 'report',
    'tableofcontents': True,
    'help': False,
    'lua': False,
    'robot': False
}


def arg_treatment():
    global ARGV

    # input
    if len(sys.argv) > 1:
        ARGV['input'] = sys.argv[1]

    # list of possible options
    options_with_args = {
        '-o': 'output',
        '--ouput': 'output',
        '-d': 'date',
        '--date': 'date',
        '-a': 'author',
        '--author': 'author',
        '-t': 'title',
        '--title': 'title',
        '-c': 'documentclass',
        '--documentclass': 'documentclass',
        '-p': 'packages',
        '--packages': 'packages'
    }
    bool_options = {
        '-h': 'help',
        '--help': 'help',
        '-T': 'tableofcontents',
        '--tableofcontents': 'tableofcontents',
        '--lua': 'lua',
        '-l': 'lua',
        '--robot': 'robot',
        '-r': 'robot'
    }

    # options treatment
    for i in range(2, len(sys.argv)):
        if sys.argv[i] in options_with_args and i + 1 < len(sys.argv):
            ARGV[options_with_args[sys.argv[i]]] = sys.argv[i + 1]
        elif sys.argv[i] in bool_options:
            ARGV[options_bools[sys.argv[i]]] = True

    if ARGV['output'] == '':
        ARGV['output'] = re.sub(
            r"^(?P<name>(?:(?!\.md$).)+)(?:\.md$)?", r"\g<name>.tex", ARGV['input'])

# Parsing functions

# Block parsing

def block_code_parse(matchObj):
    # Option syntax : "java" if wanted language is java, and "nb-java" if
    # wanted language is java AND non breaking is wanted
    code = matchObj.group('code')
    __option = matchObj.group('option')
    option = re.sub(r"nb\-(?P<option>.*)", r"\g<option>", __option)
    non_breaking = __option != option
    out = ''
    if non_breaking:
        # putting the code in a minipage will prevent from page breaking
        out += "\\begin{minipage}{\\linewidth}\n"
    if option != '':
        if option.lower() == 'ocaml':
            # because lstlisting doesn't know ocaml
            option = 'Caml'
        out += r"\lstset{language=" + option + "}\n"
    out += "\\begin{lstlisting}\n"
    out += code
    out += "\n\\end{lstlisting}"
    if non_breaking:
        out += "\\begin{minipage}{\\linewidth}\n"
    return out

def tree_parse(matchObj):
    global tikz_needed
    tikz_needed = True
    if "nTREE" in matchObj.group(0):
        return ntree_parse(matchObj)
    else:
        return binary_tree_parse(matchObj)

def binary_tree_parse(matchObj):
    # Possible options :
    #   - c : center
    option = matchObj.group('option')
    nodes = [list(x) for x in re.findall(r'([A-Z]) "([^"]*?)"', matchObj.group('tree'))]
    l = len(nodes)
    out = "\n\\begin{center}" if option == 'c' else ""
    out += "\n\\begin{tikzpicture}[nodes={circle, draw}]\n\\graph[binary tree layout, fresh nodes]{\n"
    # The package used to draw trees is TikZ and that requiers LuaLaTeX to compile (the algorithm aiming at computing distance
    # between elements of the graphs is written in Lua)
    # The traversal is a pre-order traversal
    # If you don't understand that code you should go to math spé in Lycée
    # Henri IV and ask E. T.
    def get_tree():
        def aux(i, depth):
            if nodes[i][0] == 'F':
                f = nodes[i][1]
                return ('"' + (block_parse(f) if f != '()' else '') + '"', i + 1)
            else:
                (g, r1) = aux(i + 1, depth + 1)
                (d, r2) = aux(r1, depth + 1)
                return ('"' + block_parse(nodes[i][1]) + '"' + " -- {" + g + "," + d + "}", r2)
        (ans, r) = aux(0, 1)
        if r != l:
            return ""
        else:
            return re.sub(r"\n ?\n", r"\n", ans) + "};\n"

    out += get_tree() + "\\end{tikzpicture}\n" + ("\\end{center}\n" if option == 'c' else "")
    return out

def ntree_parse(matchObj):
    # Possible options :
    #   - c : center
    # /!\ if you want to use bold or italic etc. in a nTREE you must type it in LaTeX, not in MarkdownBG
    option = matchObj.group('option')
    tree = matchObj.group('tree')
    out = "\n\\begin{center}" if option == 'c' else ""
    out += "\n\\begin{tikzpicture}[nodes={circle, draw}]\n\\graph[binary tree layout, fresh nodes]{\n"
    out += tree + "};\n\\end{tikzpicture}\n" + ("\\end{center}\n" if option == 'c' else "")
    return out


def quote_parse(matchObj):
    quotes = matchObj.group('quote')
    quotes = [ x for x in re.split(r"(?:^|\n)> (.*)", quotes) if x!= '' and x!= '\n' ]
    try:
        # For quotations with a reference
        reference = matchObj.group('reference')
        out = ''
        for quote in quotes:
            out += block_parse(quote) + r"\\"
        return r"\epigraph{" + out[0:-2] + "}" + "{" + block_parse(reference) + "}"
    except:
        # For quotations without a reference
        out = "\n\\medskip\n\\begin{displayquote}\n"
        for quote in quotes:
            out += block_parse(quote) + r"\\"
        return out[0:-2] + "\n\\end{displayquote}\n\\medskip\n"


def itemize_parse(matchObj):
    # Catching the itemize block from the match object
    itemize = matchObj.group(0)

    # Removing left indentation
    itemize = re.sub(r"(?:^|(?<=\n))(?:    |\t)(?P<item>.*)", r"\g<item>", itemize)

    # Splitting items and removing '-' symbol from each item
    items = re.split(r"(?:^|(?<=\n))- ((?:.|\n(?!-))*)", itemize)

    # Removing '' and '\n' from items
    items = [ x for x in items if x!='' and x != '\n']


    # Generate out string
    out = "\\begin{itemize}\n"

    # Adding parsed items
    for item in items:
        out += "\t\\item " + re.sub(r"\n(?P<line>.*)", r"\n\t\g<line>", block_parse(item)) + '\n'
    out += "\\end{itemize}\n"

    return out


def enumerate_parse(matchObj):
    # Catching the itemize block from the match object
    itemize = matchObj.group(0)

    # Removing left indentation
    itemize = re.sub(r"(?:^|(?<=\n))(?:    |\t)(?P<item>.*)", r"\g<item>", itemize)

    # Splitting items and removing '-' symbol from each item
    items = re.split(r"(?:^|(?<=\n))[0-9]+\. ((?:.|\n(?![0-9]+\. ))*)", itemize)

    # Removing '' and '\n' from items
    items = [ x for x in items if x != '' and x != '\n' ]

    # Generate out string
    out = "\\begin{enumerate}\n"

    # Adding parsed items
    for item in items:
        out += "\t\\item " + re.sub(r"\n(?P<line>.*)", r"\n\t\g<line>", block_parse(item)) + '\n'
    out += "\\end{enumerate}\n"

    return out


def table_parse(matchObj):
    # Catching matchObj infos
    if 'option' in matchObj.groupdict():
    # If an option is specified
        option = matchObj.group('option')
    else:
        option = ''
    table = matchObj.group('table')

    # Finding the number of rows
    n = len(re.findall(r"(?<=\|)([^\|]*)(?=\|)", re.findall("^.*", table)[0]))

    # Creating out string
    out = '\\begin{center}\n\\begin{tabular}'

    # Treating option
    if option != '':
        if len(option) == 1:
            out += '{' + ('|' + option) * n + '|}'
        else:
            options = option.split()
            out += '{'
            for op in options:
                out += '|' + option
            out += '|}'
    else:
        out += '{' + ('|' + 'l') * n + '|}'

    out += '\n'

    # Filling the table
    for line in [ line for line in re.findall(r"(?:^|(?<=\n)).*", table) if line != '' and line != '\n' ]:
    # For each line of the table
        out += "\\hline\n"
        for element in [ x for x in re.findall(r"(?<=\| )([^\|]*)(?= \|)", line) if x != '' and x != '\n' ]:
        # For each element of the line
            # Removing spaces from begining or end of element
            element = re.sub(r"(?:\s*)(?P<inside>\S.*\S)(?:\s*)", r"\g<inside>", element)

            # Adding the parsed element
            out += block_parse(element) + '&'
        out = out[0:-1] + '\\\\\n'
    out = out[0:-3] + '\n\\hline\n\\end{tabular}\n\\end{center}\n'

    return out

def title_parse(matchObj):
    level = len(matchObj.group('level')) - 1
    star = matchObj.groupdict()['star'] is not None
    title = matchObj.group('title')
    paragraph = matchObj.group('paragraph')
    out = ''
    out += [r"\chapter",
            r"\section",
            r"\subsection",
            r"\subsubsection",
            r"\paragraph",
            r"\subparagraph",
            r'\subsubparagraph'][level]
    if star:
        out += '*'
    out += '{' + inline_parse(title) + '}' + (r"\mbox{}\\" if level >= 5 else '') + '\n'
    out += block_parse(paragraph)
    return out

def block_parse(block):
    if re.sub(r'\n', '', block) == '':
        return block
    
    out = ''

    # A block can be several blocks itself
    # Blocks can be :
    #   - a paragraph
    #   - block code
    #   - itemize/enumerate
    #   - block quote
    #   - a table
    #   - a latex \[ \]
    #   - a tree or a ntree
    #   - a comment
    #   - something between two of the blocks above
    # 'block' is going to be splitted into sub-blocks that will be treated recursively
    # A block is some kind of node in a tree
    # A leaf is a piece of inline text or an block "elementary brick"

    keys = ['code', 'comment', 'latex', 'title', 'itemize', 'enumerate', 'table', 'quotation', 'tree']

    detection_regex = {
        'code':        r"(```[^\n]*\n(?:(?!```)(?:.|\n))*\n```)",
        'comment':     r"(<!\-\-(?:(?!\-\->)(?:.|\n))*\-\->)",
        'latex':       r"(\\\[(?:.|\n)*?\\\])",
        'title':       r"((?:^|(?<=\n))#+\*? [^\n]*(?:(?!\n#+ )(?:.|\n))*)",
        'itemize':     r"((?:(?:^|(?<=\n))(?:    |\t)- (?:.|\n(?!\n))*)+)",
        'enumerate':   r"((?:(?:^|(?<=\n))(?:    |\t)[0-9]+\. (?:.|\n(?!\n))*)+)",
        'table':       r"((?:!!.*\n)?(?:(?:^|(?<=\n))\|(?:[^\|]*\|)+(?:(?:\n(?=\|))|$)?)+)",
        'quotation':   r"((?:^|(?<=\n))> (?:.|\n(?=> ))*(?:\n\(.+\))?)",
        'tree' :       r"(!\[(?:[a-z]-)?n?TREE (?:(?!\]!).)*\]!)"
    }

    parse_regex = {
        'code':        r"```(?P<option>[^\n]*)\n(?P<code>(?:(?!```)(?:.|\n))*)\n```",
        'comment':     r"<!\-\-(?P<comment>(?:(?!\-\->)(?:.|\n))*)\-\->",
        'latex':       r"(?P<everything>.*)",
        'title':       r"(?:^|(?<=\n))(?P<level>#+)(?P<star>\*)? (?P<title>[^\n]*)(?P<paragraph>(?:(?!\n#+ )(?:.|\n))*)",
        'itemize':     r"(?:.|\n)*",
        'enumerate':   r"(?:.|\n)*",
        'table':       r"(?:!!tab (?P<options>.*)\n)?(?P<table>(?:(?:^|(?<=\n))\|(?:[^\|]*\|)+(?:(?:\n(?=\|))|$)?)+)",
        'quotation':   r"(?P<quote>(?:^>|(?<=\n)>) (?:.|\n(?=> ))*)\n?(?:\((?P<reference>.+)\))?",
        'tree' :       r"!\[(?:(?P<option>[a-z])-)?n?TREE (?P<tree>(?:(?!\]!).)*)\]!"
    }
    
    parse_repl = {
        'code':        block_code_parse,
        'comment':     "% \g<comment>",
        'latex':       "\g<everything>",
        'title':       title_parse,
        'itemize':     itemize_parse,
        'enumerate':   enumerate_parse,
        'table':       table_parse,
        'quotation':   quote_parse,
        'tree' :       tree_parse
    }

    for key in keys:
        if re.search(detection_regex[key], block):
            sub_blocks = re.split(detection_regex[key],block)
            if sub_blocks != ['', block, '']:
                for sub_block in sub_blocks:
                    out += block_parse(sub_block)
                return out
            break

    # Now we know that 'block' is an elementary brick, let's parse it
    for key in keys:
        if re.search(detection_regex[key], block):
        # If the block is this type of block
            return re.sub(parse_regex[key], parse_repl[key], block)

    # If we arrive to this point, this means block is not a block; it is just an inline part so we just have to
    return inline_parse(block)

# Inline parsing

def inline_parse(line):
    if re.sub(r'\n', '', line) == '':
        return line

    out = ''

    keys = ['code', 'latex', 'quote1', 'quote2', 'bold', 'underline', 'italic', 'strike']

    detection_regex = {
        'code':       r"(`(?:[^`\n]*?)`)",
        'latex':      r"(\$(?:(?!\$).*)\$)",
        'quote1':     r"(\"(?! )[^\"]*\")",
        'quote2':     r"('(?! )[^'\n ]*')",
        'bold':       r"(\*(?! )[^\*]*\*)",
        'underline':  r"(_(?! )[^_]*_)",
        'italic':     r"(%(?! )[^%]*%)",
        'strike':     r"(~(?! )[^~]*~)"
    }
    parse_regex = {
        'code':      r"`(?P<inside>[^`\n]*)`",
        'latex':     r"\$(?P<inside>(?!\$).*)\$",
        'quote1':    r"\"(?! )(?P<inside>[^\"]*?)\"",
        'quote2':    r"'(?! )(?P<inside>[^'\n ]*?)'",
        'bold':      r"\*(?! )(?P<inside>[^\*]*)\*",
        'underline': r"_(?! )(?P<inside>[^_]*)_",
        'italic':    r"%(?! )(?P<inside>[^%]*)%",
        'strike':    r"~(?! )(?P<inside>[^~]*)~"
    }
    parse_borders = {
        'code':      (r'\verb`',   '`'),
        'latex':     ('',           ''),
        'quote1':    (r'\say{',    '}'),
        'quote2':    (r'\say{',    '}'),
        'bold':      (r'\textbf{', '}'),
        'underline': (r'\ul{',     '}'),
        'italic':    (r'\textit{', '}'),
        'strike':    (r'\st{',     '}'),
    }

    for key in keys:
        if re.search(detection_regex[key], line):
            sub_lines = re.split(detection_regex[key], line)
            if sub_lines != ['', line, '']:
                for sub_line in sub_lines:
                    out += inline_parse(sub_line)
                return out

    # If we arrive here, that's because 'line' is an atom.
    # Congratulations !
    # Now we are going to parse it.

    for key in keys:
        if re.search(detection_regex[key], line):
            inside = re.sub(parse_regex[key], r"\g<inside>", line)
            return parse_borders[key][0] + (inline_parse(inside) if key not in ('code', 'latex') else inside) + parse_borders[key][1]

    # If we arrive here... it is because 'line' is not a cool piece of mdbg, yet, we can do smth to it

    supl_regex = [
        r"^[-\*_]{3,}",                                     # horizontal line
        r"\* \* \*",                                        # removing decoration
        r"(?:^|(?<=\n))!(?!\[)(?P<remainder>.*)",           # no indent
        r"_",                                               # replacing _ by \_
        r"&",                                               # replacing & by \&
        r"#",                                               # replacing # by \#
        r"%",                                               # replacing % by \%
        r"€",                                               # replacing € by \euro{}
        r"""\[(?P<text>.*)\]\((?P<link>[^ ]*)( ".*")?\)""", # links
        r"\<(?P<link>https?://[^ ]*)\>",                    # links
        r"[ ]*/(?=\n|$)",                                   # newline
        r"(?<!\\)LaTeX"                                     # LaTeX
    ]
    supl_repl = [
        r"\\hrulefill\n",                                    
        r'',                                                 
        r'\\noindent\n\g<remainder>',                       
        r"\_",                                              
        r"\&",                                              
        r"\#",                                              
        r"\%",                                              
        r"\euro{}",                                         
        r"\\href{\g<link>}{\g<text>}",                       
        r"\\href{\g<link>}{\g<link>}",                       
        r"\\newline",  
        r"\\LaTeX{}"                                    
    ]

    for i in range(len(supl_regex)):
        line = re.sub(supl_regex[i], supl_repl[i], line)

    return line

# Main


def main():
    global ARGV, doc

    # Preparing arguments and files
    # If some help is asked ?
    if ARGV['help']:
        print(doc)
        return 0

    # Treating arguments
    arg_treatment()
    inFile = ARGV['input']
    outFile = ARGV['output']

    # In case of no arguments given
    if inFile == '':
        print(doc)
        return -1

    # Preparing output file
    output = open(outFile, 'w')
    output.seek(0)

    # Reading the input file
    inputFile = open(inFile, 'r')
    contents = inputFile.read()

    # Writing in the output file
    # Document class
    output.write("\\documentclass{" + ARGV['documentclass'] + "}\n")

    # Packages
    # Some packages are loaded by default, the user can ask to load more packages
    # by putting them in the -p or --packages option

    # If a tree is detected, tikz and his libraries are loaded and lua option is put on True
    ARGV['lua'] = ARGV['lua'] or tikz_needed

    # Text encoding packages
    if ARGV['lua']:
        output.write("\\usepackage{fontspec}\n")
    else:
        output.write("\\usepackage[utf8]{inputenc}\n\\usepackage[T1]{fontenc}\n")

    additionnal_packages = []
    if 'packages' in ARGV:
        temp = ARGV['packages']
        if temp[0] != '{' or temp[-1] != '}':
            # If the user doesn't know the syntax of argument -p...
            print(doc)
            return -1
        else:
            temp = temp[1:-1]
            additionnal_packages = temp.split(', ')

    packages = ["[frenchb]{babel}",
                "[dvipsnames]{xcolor}",
                "[a4paper]{geometry}",
                "{amsmath}",
                "{amssymb}",
                "{listings}",
                "{enumerate}",
                "{epigraph}",
                "{soul}",
                "{csquotes}",
                "{dirtytalk}",
                "{hyperref}",
                "[official]{eurosym}"] + additionnal_packages

    if tikz_needed:
        packages.append('{tikz}')

    for package in packages:
        output.write(r"\usepackage" + package + '\n')
        if 'tikz' in package:
            # TikZ libraries for trees
            output.write(
                "\\usetikzlibrary{graphs,graphdrawing,arrows.meta}\n\\usegdlibrary{trees}\n")
        elif 'geometry' in package:
            # Changing the margins
            output.write(
                "\\geometry{top=2cm, bottom=2cm, left=3cm, right=3cm}\n")

    # RobotMono font
    if ARGV['robot']:
        output.write("\setmonofont{[RobotoMono-Regular.ttf]}\n")

    # Syntax highliting
    if '`' in contents:
        # If the document is likely to contain a piece of code
        output.write(r"\lstset{basicstyle=\ttfamily,keywordstyle=\color{RedViolet},stringstyle=\color{Green},commentstyle=\color{Gray},identifierstyle=\color{NavyBlue},numberstyle=\color{Gray},numbers=left,breaklines=true,breakatwhitespace=true,breakautoindent=true,breakindent=5pt,showstringspaces=false, tabsize=4}" + '\n')

    # Presentation
    if 'title' in ARGV:
        output.write(r"\title{" + ARGV['title'] + "}\n")
    if 'author' in ARGV:
        output.write(r"\author{" + ARGV['author'] + "}\n")
    if 'date' in ARGV:
        output.write(r"\date{" + ARGV['date'] + "}\n")

    output.write("\\begin{document}\n")
    output.write("\\nocite{*}\n")

    if 'title' in ARGV:
        output.write("\\maketitle\n")

    if ARGV['tableofcontents']:
        output.write("\n\\tableofcontents\n")
    output.write("\n")

    # Creation of the main string
    main_string = block_parse(contents)

    # Formating line breaks
    main_string = re.sub(r"\\medskip", r"\n\\medskip\n", main_string)
    main_string = re.sub(r"[\n]{2,}", r"\n\n", main_string)
    main_string = re.sub(
        r"\\medskip[\n]{1,}\\medskip", r"\n\\medskip\n", main_string)

    # Writing the main string in the output file
    output.write(main_string)

    # Goodbye
    output.write("\n\\end{document}")

    inputFile.close()
    output.close()

    print("LaTeX output file written in :", outFile)


# Execution
if __name__ == '__main__':
    main()
else:
    print(doc)
