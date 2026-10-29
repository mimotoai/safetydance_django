import os
import shutil
import sys

__location__ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(__location__, "../src"))

import safetydance_django

# -- Run sphinx-apidoc -----------------------------------------------------
# Regenerates docs/api on every build, so no one runs apidoc by hand.
from sphinx.ext import apidoc

output_dir = os.path.join(__location__, "api")
module_dir = os.path.join(__location__, "../src/safetydance_django")
shutil.rmtree(output_dir, ignore_errors=True)
apidoc.main(["-f", "-o", output_dir, module_dir])

# -- General configuration -------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

project = "safetydance_django"
copyright = "2019-2026, David Charboneau"
version = safetydance_django.__version__
release = version

exclude_patterns = ["_build"]
pygments_style = "sphinx"

# -- Options for HTML output -----------------------------------------------
html_theme = "alabaster"
html_theme_options = {"sidebar_width": "300px", "page_width": "1200px"}
html_static_path = ["_static"]
htmlhelp_basename = "safetydance_django-doc"

# -- Options for LaTeX output ----------------------------------------------
latex_documents = [
    ("index", "user_guide.tex", "safetydance_django Documentation",
     "David Charboneau", "manual"),
]

# -- External mapping ------------------------------------------------------
python_version = ".".join(map(str, sys.version_info[0:2]))
intersphinx_mapping = {
    "python": ("https://docs.python.org/" + python_version, None),
    "django": ("https://docs.djangoproject.com/en/stable/",
               "https://docs.djangoproject.com/en/stable/_objects/"),
}
