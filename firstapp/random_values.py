#!/usr/bin/env python

import random


def random_string(number):
    return ''.join(
        [random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) for x in range(number)])
