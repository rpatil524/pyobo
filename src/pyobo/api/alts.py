# -*- coding: utf-8 -*-

"""High-level API for alternative identifiers."""

import logging
from functools import lru_cache
from typing import List, Mapping, Optional

from tqdm import tqdm

from .utils import get_version
from ..getters import get
from ..identifier_utils import normalize_curie, wrap_norm_prefix
from ..path_utils import prefix_cache_join
from ..utils.cache import cached_multidict

__all__ = [
    'get_id_to_alts',
    'get_alts_to_id',
    'get_primary_curie',
    'get_primary_identifier',
]

logger = logging.getLogger(__name__)

NO_ALTS = {
    'ncbigene',
}


@lru_cache()
@wrap_norm_prefix
def get_id_to_alts(prefix: str, force: bool = False) -> Mapping[str, List[str]]:
    """Get alternate identifiers."""
    if prefix in NO_ALTS:
        return {}

    path = prefix_cache_join(prefix, 'alt_ids.tsv', version=get_version(prefix))
    header = [f'{prefix}_id', 'alt_id']

    @cached_multidict(path=path, header=header, force=force)
    def _get_mapping() -> Mapping[str, List[str]]:
        if force:
            tqdm.write(f'[{prefix}] forcing reload for alts')
        else:
            logger.info('[%s] no cached alts found. getting from OBO loader', prefix)
        obo = get(prefix, force=force)
        return obo.get_id_alts_mapping()

    return _get_mapping()


@lru_cache()
@wrap_norm_prefix
def get_alts_to_id(prefix: str, force: bool = False) -> Mapping[str, str]:
    """Get alternative id to primary id mapping."""
    return {
        alt: primary
        for primary, alts in get_id_to_alts(prefix, force=force).items()
        for alt in alts
    }


def get_primary_curie(curie: str) -> Optional[str]:
    """Get the primary curie for an entity."""
    prefix, identifier = normalize_curie(curie)
    primary_identifier = get_primary_identifier(prefix, identifier)
    if primary_identifier is not None:
        return f'{prefix}:{primary_identifier}'


@wrap_norm_prefix
def get_primary_identifier(prefix: str, identifier: str) -> str:
    """Get the primary identifier for an entity.

    :param prefix: The name of the resource
    :param identifier: The identifier to look up
    :returns: the canonical identifier based on alt id lookup

    Returns the original identifier if there are no alts available or if there's no mapping.
    """
    if prefix in NO_ALTS:  # TODO later expand list to other namespaces with no alts
        return identifier

    alts_to_id = get_alts_to_id(prefix)
    if alts_to_id and identifier in alts_to_id:
        return alts_to_id[identifier]
    return identifier