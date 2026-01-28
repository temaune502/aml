"""
Regex модуль для AML: базові операції пошуку та заміни.
"""

import re

def matches(pattern, text):
    """Перевірити повний збіг (re.fullmatch). Повертає True/False."""
    return re.fullmatch(pattern, text) is not None

def search(pattern, text):
    """Знайти перший збіг. Повертає словник з match, span, groups або None."""
    m = re.search(pattern, text)
    if not m:
        return None
    return {
        "match": m.group(0),
        "span": [m.span()[0], m.span()[1]],
        "groups": list(m.groups())
    }

def findall(pattern, text):
    """Знайти всі збіги. Повертає список рядків або кортежів."""
    res = re.findall(pattern, text)
    # re.findall може повертати кортежі груп — AML підтримує списки, перетворимо кортежі у списки
    out = []
    for item in res:
        if isinstance(item, tuple):
            out.append(list(item))
        else:
            out.append(item)
    return out

def replace(pattern, repl, text, count=0):
    """Замінити за шаблоном (re.sub). Повертає новий рядок."""
    return re.sub(pattern, repl, text, count=count)