#!/usr/bin/env python
# -*- coding: utf-8 -*-

from allosaurus.app import read_recognizer
model = read_recognizer()

def recognize(input_file):
   return model.recognize(input_file)

if __name__ == "__main__":
   recognize()
