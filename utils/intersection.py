import sys

from tokenizer import Tokenizer
import os


class Intersection:

    @staticmethod
    def comparison(file_path_one: 'str', file_path_two: 'str') -> (set, int):
        token_set_one = set(Tokenizer.tokenize(file_path_one))
        token_set_two = set(Tokenizer.tokenize(file_path_two))

        intersect = token_set_one.intersection(token_set_two)

        return intersect, len(intersect)
