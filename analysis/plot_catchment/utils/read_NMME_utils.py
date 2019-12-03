#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 21:56:00 2018

@author: eriddle
"""
import netCDF4 as nc4

def open_file(filename,fileformat):
    if fileformat in ['nc4']:
        file=nc4.Dataset(fn,'r')
    return file