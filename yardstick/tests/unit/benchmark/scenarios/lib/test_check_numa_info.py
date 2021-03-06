##############################################################################
# Copyright (c) 2017 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import mock
import unittest

from yardstick.benchmark.scenarios.lib.check_numa_info import CheckNumaInfo


class CheckNumaInfoTestCase(unittest.TestCase):

    @mock.patch.object(CheckNumaInfo, '_check_vm2_status')
    def test_run(self, mock_check_vm2):
        scenario_cfg = {'info1': {}, 'info2': {}}
        obj = CheckNumaInfo(scenario_cfg, {})
        obj.run({})
        mock_check_vm2.assert_called_once()

    def test_check_vm2_status_length_eq_1(self):
        info1 = {
            'pinning': [0],
            'vcpupin': [{
                'cpuset': '1,2'
            }]
        }
        info2 = {
            'pinning': [0],
            'vcpupin': [{
                'cpuset': '1,2'
            }]
        }
        scenario_cfg = {'info1': info1, 'info2': info2}
        obj = CheckNumaInfo(scenario_cfg, {})
        status = obj._check_vm2_status(info1, info2)
        self.assertTrue(status)

    def test_check_vm2_status_length_gt_1(self):
        info1 = {
            'pinning': [0, 1],
            'vcpupin': [{
                'cpuset': '1,2'
            }]
        }
        info2 = {
            'pinning': [0, 1],
            'vcpupin': [{
                'cpuset': '1,2'
            }]
        }
        scenario_cfg = {'info1': info1, 'info2': info2}
        obj = CheckNumaInfo(scenario_cfg, {})
        status = obj._check_vm2_status(info1, info2)
        self.assertFalse(status)

    def test_check_vm2_status_length_not_in_set(self):
        info1 = {
            'pinning': [0],
            'vcpupin': [{
                'cpuset': '1,7'
            }]
        }
        info2 = {
            'pinning': [0],
            'vcpupin': [{
                'cpuset': '1,7'
            }]
        }
        scenario_cfg = {'info1': info1, 'info2': info2}
        obj = CheckNumaInfo(scenario_cfg, {})
        status = obj._check_vm2_status(info1, info2)
        self.assertFalse(status)
