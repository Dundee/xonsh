#!/usr/bin/env python
# coding=utf-8
"""The xonsh installer."""
from __future__ import print_function, unicode_literals
import os
import sys
import json
from tempfile import TemporaryDirectory
try:
    from setuptools import setup
    from setuptools.command.sdist import sdist
    from setuptools.command.install import install
    from setuptools.command.develop import develop
    HAVE_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    from distutils.command.sdist import sdist as sdist
    from distutils.command.install import install as install
    HAVE_SETUPTOOLS = False

try:
    from jupyter_client.kernelspec import KernelSpecManager
    HAVE_JUPYTER = True
except ImportError:
    HAVE_JUPYTER = False

from xonsh import __version__ as XONSH_VERSION

TABLES = ['xonsh/lexer_table.py', 'xonsh/parser_table.py']


CONDA = ("--conda" in sys.argv)
if CONDA:
    sys.argv.remove("--conda")

def clean_tables():
    for f in TABLES:
        if os.path.isfile(f):
            os.remove(f)
            print('Remove ' + f)


def build_tables():
    print('Building lexer and parser tables.')
    sys.path.insert(0, os.path.dirname(__file__))
    from xonsh.parser import Parser
    Parser(lexer_table='lexer_table', yacc_table='parser_table',
           outputdir='xonsh')
    sys.path.pop(0)


def install_jupyter_hook(root=None):
    if not HAVE_JUPYTER:
        print('Could not install Jupyter kernel spec, please install Jupyter/IPython.')
        return
    spec = {"argv": [sys.executable, "-m", "xonsh.jupyter_kernel",
                                     "-f", "{connection_file}"],
            "display_name":"Xonsh",
            "language":"xonsh",
            "codemirror_mode":"shell",
            }
    if CONDA:
        d = os.path.join(sys.prefix + '/share/jupyter/kernels/xonsh/')
        os.makedirs(d, exist_ok=True)
        if sys.platform == 'win32':
            # Ensure that conda-build detects the hard coded prefix
            spec['argv'][0] = spec['argv'][0].replace(os.sep, os.altsep)
        with open(os.path.join(d, 'kernel.json'), 'w') as f:
            json.dump(spec, f, sort_keys=True)
    else:
        with TemporaryDirectory() as d:
            os.chmod(d, 0o755)  # Starts off as 700, not user readable
            with open(os.path.join(d, 'kernel.json'), 'w') as f:
                json.dump(spec, f, sort_keys=True)
            print('Installing Jupyter kernel spec...')
            KernelSpecManager().install_kernel_spec(d, 'xonsh', user=('--user' in sys.argv), replace=True, prefix=root)

class xinstall(install):
    def run(self):
        clean_tables()
        build_tables()
        install_jupyter_hook(self.root if self.root else None)
        install.run(self)


class xsdist(sdist):
    def make_release_tree(self, basedir, files):
        clean_tables()
        build_tables()
        sdist.make_release_tree(self, basedir, files)


if HAVE_SETUPTOOLS:
    class xdevelop(develop):
        def run(self):
            clean_tables()
            build_tables()
            develop.run(self)


def main():
    if sys.version_info[0] < 3:
        sys.exit('xonsh currently requires Python 3.4+')
    try:
        if '--name' not in sys.argv:
            print(logo)
    except UnicodeEncodeError:
        pass
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'r') as f:
        readme = f.read()
    skw = dict(
        name='xonsh',
        description='an exotic, usable shell',
        long_description=readme,
        license='BSD',
        version=XONSH_VERSION,
        author='Anthony Scopatz',
        maintainer='Anthony Scopatz',
        author_email='scopatz@gmail.com',
        url='https://github.com/scopatz/xonsh',
        platforms='Cross Platform',
        classifiers=['Programming Language :: Python :: 3'],
        packages=['xonsh'],
        scripts=['scripts/xonsh', 'scripts/xonsh.bat'],
        cmdclass={'install': xinstall, 'sdist': xsdist},
        )
    if HAVE_SETUPTOOLS:
        skw['setup_requires'] = ['ply']
        skw['install_requires'] = ['ply']
        skw['entry_points'] = {
            'pygments.lexers': ['xonsh = xonsh.pyghooks:XonshLexer',
                                'xonshcon = xonsh.pyghooks:XonshConsoleLexer',
                                ],
            }
        skw['cmdclass']['develop'] = xdevelop
    setup(**skw)

logo = """
                           ╓██▄
                          ╙██▀██╕
                         ▐██4Φ█▀█▌
                       ²██▄███▀██^██
                     -███╩▀ " ╒▄█████▀█
                      ║██▀▀W╤▄▀ ▐║█╘ ╝█
                 ▄m▀%Φ▀▀  ╝*"    ,α█████▓▄,▄▀Γ"▀╕
                 "▀██¼"     ▄═╦█╟║█▀ ╓ `^`   ,▄ ╢╕
                  ,▀╫M█▐j╓╟▀ ╔▓▄█▀  '║ ╔    ╣║▌  ▀▄
               ▄m▀▀███╬█╝▀  █▀^      "ÜM  j▐╟╫╨▒   ╙▀≡═╤═m▀╗
               █æsæ╓  ╕, ,▄Ä   ▐'╕H   LU  ║║╠╫Å^2=⌐         █
            ▄æ%Å███╠█ª╙▄█▀      $1╙       ║║╟╫╩*T▄           ▌
           ╙╗%▄,╦██▌█▌█╢M         ╕      M║║║║█═⌐ⁿ"^         ╫
             ╙╣▀████@█░█    ▌╕╕   `      ▌║▐▐║█D═≈⌐¬ⁿ      s ║⌐
               ╙╬███▓║█`     ▌╚     ╕   ╕▌║▐▐╣▌⌐*▒▒Dù`       ▐▌
                ╙╬██╨U█      ╟      $ ▌ ▌▌▐▐▐M█▄═≤⌐%       ╓⌐ ▌
                 ║║█▄▌║             ╟ ▌ ▌M▐▐▐M█▀▒▒▒22,       ▐▌
                  ███╙^▌            ║ ▌ ⌐M▐▐▐M█≤⌐⌐¬──        ▐M
                  ║██ ▌╙   ╓       H║ ▌╒ M║▐▐M█"^^^^^"ⁿ      ║
                   ██╕╙@▓   ╕      ▌║ H'  ║▐▐▐█══=.,,,       █
                   ╙█▓╔╚╚█     ╠   ▌└╒ ▌▐ ╚║║║▀****ⁿ -      ╓▌
                    ╙█▌¼V╚▌   ▌  ╕ ▌ ║╒ ║ ▌▒╠█▀≤≤≤≤≤⌐       █
                     ╙█▌╔█╚▌     ┘ M ▌║ ╫ UUM██J^^"        ▐▌
                      ╙██╙█╙▌  ╕$j  ▐⌐▌ ▌║╝╟█Å%%%≈═        █
                       ╙╣█╣█^▌ ╠║▐  ║ ▌▐.DU██^[""ⁿ       -╒▌
                         ▀█▄█`▌ ░M▀ ▌▐ Å£╝╝█╜%≈═╓""w   ⁿ⌐ █
                          `▀▄▀`▌ ▌█▐⌐║▐UW╖██%≤═░*─    =z ▄Γ
                            ╙██╙▄▌█  ▌Å╛╣██╨%╤ƒⁿ=    -` ▄┘
                              █▌╢▓▌▌ W £6█╤,"ⁿ `   ▄≡▀▀▀
                               █"█▌▌╟Å╓█╓█▀%`    ▄▀
                               ╙▌██`▒U▓U█%╗*     █
                                ▌╫║ ▌ÅÅ║▀╛¬`      `"█
                                ▌╫  ╫╟ █▄     ~╦%▒╥4^
                                ▌▌  "M█ `▀╕ X╕"╗▄▀^
                                █▌   ╓M   ╙▀e▀▀^
                                ╙██▄▄▀
                                  ^^
"""

if __name__ == '__main__':
    main()
