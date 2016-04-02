#coding=utf-8

from uwsgidecorators import *


@cron(-1, -1, -1, -1, -1)
def test(num):
    print('123')
