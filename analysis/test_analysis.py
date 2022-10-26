import json, re
import log_parse
import quick_stats
from logs.model_logs_config import LogsConfig
from logs import load
from helpers import calc
import numpy as np


def test_file_size():
    logs_config = LogsConfig('./fixtures/log_config_one.test.json')
    log_parse.execute(logs_config, 'LATEST')
    stats = quick_stats.execute(logs_config)
    assert str(stats['file_size_avg_duration'][52429]['FETCHING']) == "1.5 (sec.)"
    assert str(stats['file_size_avg_duration'][524290]['FETCHING']) == "2.0 (sec.)"
    assert str(stats['phase_avg_duration']['FETCHING']) == f"{round((1+2+2)/3, 3)} (sec.)"


def test_agent_uptime():
    logs_config = LogsConfig('./fixtures/log_config_two.test.json')
    log_parse.execute(logs_config, 'LATEST')
    stats = quick_stats.execute(logs_config)
    assert json.dumps(stats['uptime'], default=str) == '{"count": 30, "max": "769.115 (sec.)", "min": "47.695 (sec.)", "avg_uptime": "365.655 (sec.)"}'
    data_set: DataSet = load.latest_data_set(logs_config)
    bins,sorted_avgs,width = calc.agent_uptime_duration_bins(data_set)
    np.testing.assert_allclose(bins, [ 47.695, 228.05, 408.405, 588.76 ])
    np.testing.assert_allclose(sorted_avgs, [1.0109956, 1.0118008571428572, 1.0095235, 1.0143448000000002])
