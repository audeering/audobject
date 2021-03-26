import configparser
from datetime import date
import os
import subprocess


config = configparser.ConfigParser()
config.read(os.path.join('..', 'setup.cfg'))

# Project -----------------------------------------------------------------
author = config['metadata']['author']
copyright = f'2020-{date.today().year} audEERING GmbH'
project = config['metadata']['name']

# The x.y.z version read from tags
try:
    version = subprocess.check_output(['git', 'describe', '--tags',
                                       '--always'])
    version = version.decode().strip()
except Exception:
    version = '<unknown>'
title = f'{project} Documentation'


# General -----------------------------------------------------------------
master_doc = 'index'
extensions = []
source_suffix = '.rst'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']
pygments_style = None
extensions = [
    'jupyter_sphinx',  # executing code blocks
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # support for Google-style docstrings
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
    'sphinx_copybutton',  # for "copy to clipboard" buttons
]

# Ignore package dependencies during building the docs
autodoc_mock_imports = [
    'tqdm',
]

# Reference with :ref:`data-header:Database`
autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2

# Do not copy prompot output
copybutton_prompt_text = r'>>> |\.\.\. '
copybutton_prompt_is_regexp = True

# Mapping to external documentation
intersphinx_mapping = {
    'audeer': ('https://audeering.github.io/audeer/', None),
    'audfactory': ('https://audeering.github.io/audfactory/', None),
    'python': ('https://docs.python.org/3/', None),
}

# Disable Gitlab as we need to sign in
linkcheck_ignore = [
    'https://gitlab.audeering.com',
]

# HTML --------------------------------------------------------------------
html_theme = 'sphinx_audeering_theme'
html_theme_options = {
    'display_version': True,
    'logo_only': False,
    'footer_links': False,
}
html_context = {
    'display_github': True,
}
html_title = title
