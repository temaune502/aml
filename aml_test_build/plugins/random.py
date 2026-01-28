import random as py_random

def randint(a, b):
    return py_random.randint(a, b)

def uniform(a, b):
    return py_random.uniform(a, b)

def choice(seq):
    return py_random.choice(seq)

def shuffle(seq):
    py_random.shuffle(seq)
    return seq

def random():
    return py_random.random()

def seed(a):
    py_random.seed(a)
