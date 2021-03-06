##############################################################################
# Copyright (c) 2018 Intel Corporation.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import ast
import tempfile
import unittest

import mock
from six.moves import configparser

from yardstick.benchmark import core
from yardstick.benchmark.core import report
from yardstick.cmd.commands import change_osloobj_to_paras


GOOD_YAML_NAME = 'fake_name'
GOOD_TASK_ID = "9cbe74b6-df09-4535-8bdc-dc3a43b8a4e2"
GOOD_DB_FIELDKEYS = [
    {u'fieldKey': u'metric1', u'fieldType': u'integer'},
    {u'fieldKey': u'metric4', u'fieldType': u'integer'},
    {u'fieldKey': u'metric2', u'fieldType': u'integer'},
    {u'fieldKey': u'metric3', u'fieldType': u'integer'},
]
GOOD_DB_METRICS = [
    {u'time': u'2018-08-20T16:49:26.372662016Z',
     u'metric1': 1, u'metric2': 0, u'metric3': 8, u'metric4': 5},
    {u'time': u'2018-08-20T16:49:27.374208000Z',
     u'metric1': 1, u'metric2': 1, u'metric3': 5, u'metric4': 4},
    {u'time': u'2018-08-20T16:49:28.375742976Z',
     u'metric1': 2, u'metric2': 2, u'metric3': 3, u'metric4': 3},
    {u'time': u'2018-08-20T16:49:29.377299968Z',
     u'metric1': 3, u'metric2': 3, u'metric3': 2, u'metric4': 2},
    {u'time': u'2018-08-20T16:49:30.378252032Z',
     u'metric1': 5, u'metric2': 4, u'metric3': 1, u'metric4': 1},
    {u'time': u'2018-08-20T16:49:30.379359421Z',
     u'metric1': 8, u'metric2': 5, u'metric3': 1, u'metric4': 0},
]

yardstick_config = """
[DEFAULT]
dispatcher = influxdb
"""


def my_query(query_sql):
    get_fieldkeys_cmd = 'show field keys'
    get_metrics_cmd = 'select * from'

    if get_fieldkeys_cmd in query_sql:
        return GOOD_DB_FIELDKEYS
    elif get_metrics_cmd in query_sql:
        return GOOD_DB_METRICS
    return []


class ReportTestCase(unittest.TestCase):

    @mock.patch.object(report.influx, 'query', new=my_query)
    @mock.patch.object(configparser.ConfigParser,
        'read', side_effect=mock.mock_open(read_data=yardstick_config))
    def test_report_generate_nsb_simple(self, *args):
        tmpfile = tempfile.NamedTemporaryFile(delete=True)

        args = core.Param({"task_id": [GOOD_TASK_ID], "yaml_name": [GOOD_YAML_NAME]})
        params = change_osloobj_to_paras(args)

        with mock.patch.object(report.consts, 'DEFAULT_HTML_FILE', tmpfile.name):
            report.Report().generate_nsb(params)

        data_act = None
        time_act = None
        keys_act = None
        tree_act = None
        with open(tmpfile.name) as f:
            for l in f.readlines():
                 if "var report_data = {" in l:
                     data_act = ast.literal_eval(l.strip()[18:-1])
                 elif "var report_time = [" in l:
                     time_act = ast.literal_eval(l.strip()[18:-1])
                 elif "var report_keys = [" in l:
                     keys_act = ast.literal_eval(l.strip()[18:-1])
                 elif "var report_tree = [" in l:
                     tree_act = ast.literal_eval(l.strip()[18:-1])

        data_exp = {
            'metric1': [1, 1, 2, 3, 5, 8],
            'metric2': [0, 1, 2, 3, 4, 5],
            'metric3': [8, 5, 3, 2, 1, 1],
            'metric4': [5, 4, 3, 2, 1, 0],
        }
        time_exp = [
            '16:49:26.372662', '16:49:27.374208', '16:49:28.375742',
            '16:49:29.377299', '16:49:30.378252', '16:49:30.379359',
        ]
        keys_exp = [
            'metric1', 'metric2', 'metric3', 'metric4',
        ]
        tree_exp = [
            {'parent': '#', 'text': 'metric1', 'id': 'metric1'},
            {'parent': '#', 'text': 'metric2', 'id': 'metric2'},
            {'parent': '#', 'text': 'metric3', 'id': 'metric3'},
            {'parent': '#', 'text': 'metric4', 'id': 'metric4'},
        ]

        self.assertEqual(data_exp, data_act)
        self.assertEqual(time_exp, time_act)
        self.assertEqual(keys_exp, keys_act)
        self.assertEqual(tree_exp, tree_act)
