# -*- coding: utf-8 -*-

"""Extraction of mappings from OBO documents."""

from .extract_synonyms import get_synonyms  # noqa: F401
from .extract_xrefs import get_all_xrefs, get_xrefs, iterate_xrefs_from_graph  # noqa: F401