import json, re
import log_parse
import quick_stats
from logs.model_logs_config import LogsConfig



def test_analysis():
    logs_config = LogsConfig('./fixtures/log_config.test.json')
    log_parse.execute(logs_config, 'ALL')
    stats = quick_stats.execute(logs_config)
    assert str(stats['file_size_avg_duration'][52429]['FETCHING']) == "1.0 (sec.)"

    print(json.dumps(stats, indent=4, default=str))
