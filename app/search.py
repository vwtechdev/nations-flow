import unicodedata

from django.db import connection
from django.db.models import CharField, Q, TextField, Transform


class Unaccent(Transform):
    function = 'UNACCENT'
    lookup_name = 'unaccent'
    bilateral = True


CharField.register_lookup(Unaccent)
TextField.register_lookup(Unaccent)


def strip_accents(text):
    """Remove acentos/diacríticos de um texto para permitir busca flexível."""
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii')


def search_q(term, *fields):
    """Constrói um Q de busca case- e accent-insensitive sobre os campos dados.

    No PostgreSQL usa o lookup `unaccent` (extensão habilitada por migração)
    tanto na coluna quanto no termo; em outros backends (ex.: SQLite em dev)
    cai para `icontains` com o termo original (comportamento atual).
    """
    q = Q()
    if connection.vendor == 'postgresql':
        term = strip_accents(term)
        lookup = 'unaccent__icontains'
    else:
        lookup = 'icontains'
    for field in fields:
        q |= Q(**{f'{field}__{lookup}': term})
    return q