# Base module for AML language
# Contains basic functions and utilities
import time
import math
import random

# Hook injected by interpreter for cooperative cancellation
_aml_check_cancel = None
def  tuple_to_list(*args):
    """
    Convert a tuple to a list
    """
    return list(args)
def true():
    return True
def false():
    return False
def not_(value):
    return not value

def to_str(value):
    """
    Convert a value to a string
    """
    return str(value)
def print_message(*args):
    """
    Print a message to the console
    """
    print("".join(args))

def add(a, b):
    """
    Add two numbers
    """
    return a + b

def subtract(a, b):
    """
    Subtract b from a
    """
    return a - b

def multiply(a, b):
    """
    Multiply two numbers
    """
    return a * b

def divide(a, b):
    """
    Divide a by b
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def create_list(*args):
    """
    Create a list from arguments
    """
    return list(args)

def append_to_list(lst, item):
    """
    Append an item to a list
    """
    lst.append(item)
    return lst

def get_list_item(lst, index):
    """
    Get an item from a list by index
    """
    if index < 0 or index >= len(lst):
        raise IndexError("List index out of range")
    return lst[index]

def set_list_item(lst, index, value):
    """
    Set an item in a list by index
    """
    if index < 0 or index >= len(lst):
        raise IndexError("List index out of range")
    lst[index] = value
    return lst

def sleep_ms(ms):
    """
    Sleep for a specified number of milliseconds
    """
    time.sleep(ms / 1000.0)
    
def wait(seconds):
    """
    Wait for a specified number of seconds
    """
    try:
        deadline = time.time() + float(seconds)
    except Exception:
        deadline = time.time() + seconds
    check = _aml_check_cancel
    # Sleep in small slices to allow early exit on cancellation
    while True:
        if check and callable(check) and check():
            break
        now = time.time()
        if now >= deadline:
            break
        remaining = deadline - now
        time.sleep(0.05 if remaining > 0.05 else remaining)

# Additional list helpers for completeness
def list_length(lst):
    """
    Return length of a list
    """
    return len(lst)

def remove_from_list(lst, item):
    """
    Remove first occurrence of item from list
    """
    try:
        lst.remove(item)
    except ValueError:
        raise ValueError("Item not found in list")
    return lst

def pop_from_list(lst, index):
    """
    Pop item by index from list
    """
    if index < 0 or index >= len(lst):
        raise IndexError("List index out of range")
    return lst.pop(index)

def sort_list(lst):
    """
    Sort list in ascending order (in place)
    """
    try:
        lst.sort()
    except TypeError:
        raise TypeError("List elements are not comparable for sorting")
    return lst

def reverse_list(lst):
    """
    Reverse list (in place)
    """
    lst.reverse()
    return lst

# Extended list utilities
def extend_list(lst, other):
    """
    Extend list with another iterable
    """
    lst.extend(other)
    return lst

def insert_into_list(lst, index, value):
    """
    Insert value at given index
    """
    if index < 0 or index > len(lst):
        raise IndexError("List index out of range for insert")
    lst.insert(index, value)
    return lst

def index_of(lst, value):
    """
    Return index of value or -1 if not found
    """
    try:
        return lst.index(value)
    except ValueError:
        return -1

def list_contains(lst, value):
    """
    Check whether list contains value
    """
    return value in lst

def slice_list(lst, start, end=None, step=None):
    """
    Slice list similar to Python slicing
    """
    return lst[slice(start, end, step)]

def concat_lists(a, b):
    """
    Return a new list that is a + b
    """
    return list(a) + list(b)

def clear_list(lst):
    """
    Clear list (in place) and return it
    """
    lst.clear()
    return lst

def copy_list(lst):
    """
    Return a shallow copy of the list
    """
    return list(lst)

def unique_list(lst):
    """
    Return list with unique elements preserving order
    """
    seen = set()
    result = []
    for x in lst:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result

# =============================
# Conversions & Types
# =============================
def to_int(value):
    """Convert value to int (from str/float/bool)."""
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int,)):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            # Try float then int
            return int(float(value))
    return int(value)

def to_float(value):
    """Convert value to float."""
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(value)

def to_bool(value):
    """Convert value to bool, strings handled: 'true/false', 'yes/no', '1/0'."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("true", "yes", "y", "1", "on"): return True
        if v in ("false", "no", "n", "0", "off"): return False
        return bool(value)
    return bool(value)

def type_of(value):
    """Return AML-friendly type name: number/string/bool/list/dict/none/object."""
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return "object"

def is_none(value):
    return value is None

def is_bool(value):
    return isinstance(value, bool)

def is_string(value):
    return isinstance(value, str)

def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def is_list(value):
    return isinstance(value, list)

def is_dict(value):
    return isinstance(value, dict)

def length(value):
    """Generic length for list/string/dict; raises for unsupported."""
    if isinstance(value, (list, str, dict)):
        return len(value)
    raise TypeError("length() supports list, string, dict")

# =============================
# String utilities
# =============================
def string_lower(s):
    """Return lowercase string."""
    return str(s).lower()

def string_upper(s):
    """Return uppercase string."""
    return str(s).upper()

def string_trim(s):
    """Trim leading/trailing whitespace."""
    return str(s).strip()

def starts_with(s, prefix):
    """Check if string starts with prefix."""
    return str(s).startswith(str(prefix))

def ends_with(s, suffix):
    """Check if string ends with suffix."""
    return str(s).endswith(str(suffix))

def string_contains(s, sub):
    """Check if substring present in string."""
    return str(sub) in str(s)

def string_split(s, sep=None, maxsplit=-1):
    """Split string into list by separator (None = whitespace)."""
    return str(s).split(sep, maxsplit)

def join_strings(items, sep=""):
    """Join list of items into string with separator."""
    return str(sep).join(map(str, items))

def string_slice(s, start, end=None, step=None):
    """Slice string similar to Python slicing."""
    return str(s)[slice(start, end, step)]

# =============================
# Dict utilities
# =============================
def dict_get(d, key):
    """Get value by key; raises KeyError if missing."""
    if key in d:
        return d[key]
    raise KeyError("Key not found: %r" % (key,))

def dict_get_default(d, key, default=None):
    """Get value by key or default if missing."""
    return d[key] if key in d else default

def dict_set(d, key, value):
    """Set value by key; returns dict."""
    d[key] = value
    return d

def has_key(d, key):
    """Return True if key exists in dict."""
    return key in d

def remove_key(d, key):
    """Remove key; raises KeyError if missing; returns dict."""
    del d[key]
    return d

def dict_keys(d):
    """Return list of keys."""
    return list(d.keys())

def dict_values(d):
    """Return list of values."""
    return list(d.values())

def dict_items(d):
    """Return list of [key, value] pairs for AML friendliness."""
    return [[k, d[k]] for k in d]

def merge_dicts(a, b):
    """Return a shallow-merged dict (a overridden by b)."""
    out = dict(a)
    out.update(dict(b))
    return out

def update_dict(d, updates):
    """Update dict in place with another mapping; returns dict."""
    d.update(dict(updates))
    return d

# =============================
# Numbers & math
# =============================
def clamp(value, min_value, max_value):
    """Clamp value into [min_value, max_value]."""
    if min_value > max_value:
        raise ValueError("min_value > max_value")
    return max(min_value, min(max_value, value))

def abs_val(x):
    """Absolute value."""
    return abs(x)

def floor(x):
    """Floor value."""
    return math.floor(x)

def ceil(x):
    """Ceil value."""
    return math.ceil(x)

def round_to(x, ndigits=0):
    """Round to ndigits."""
    return round(x, ndigits)

def min_val(a, b):
    return a if a <= b else b

def max_val(a, b):
    return a if a >= b else b

def sum_list(lst):
    """Sum of numeric list."""
    return sum(lst)

def average_list(lst):
    """Average of numeric list; raises on empty."""
    if not lst:
        raise ValueError("Cannot average empty list")
    return sum(lst) / len(lst)

# =============================
# Ranges & random
# =============================
def range_list(start, stop=None, step=1):
    """Create list like Python range. If stop is None -> range(0, start)."""
    if stop is None:
        return list(range(0, int(start), int(step)))
    return list(range(int(start), int(stop), int(step)))

def random_int(min_value, max_value):
    """Random integer in [min_value, max_value]."""
    return random.randint(int(min_value), int(max_value))

def random_float(min_value=0.0, max_value=1.0):
    """Random float in [min_value, max_value]."""
    return random.uniform(float(min_value), float(max_value))

def choose(lst):
    """Return random element from list; raises if empty."""
    if not lst:
        raise ValueError("Cannot choose from empty list")
    return random.choice(lst)

def shuffle_list(lst):
    """Shuffle list in place; returns list."""
    random.shuffle(lst)
    return lst

# =============================
# Time helpers
# =============================
def sleep_millis(ms):
    """Sleep given milliseconds."""
    try:
        duration = float(ms) / 1000.0
    except Exception:
        duration = ms / 1000.0
    wait(duration)

def current_time_ms():
    """Current time in milliseconds since epoch."""
    return int(time.time() * 1000)