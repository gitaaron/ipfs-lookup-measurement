from models.model_data_set import DataSet
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import numpy as np


# `freq` is specified by Pandas `date_range`
# https://pandas.pydata.org/docs/reference/api/pandas.date_range.html
def plot_interval_property(data_set: DataSet, freq: str, sys_prop: str):
    occurances = [pd.to_datetime(she.occurred) for she in data_set.sys_health_events]
    ts_occurances = [ts.value for ts in occurances]

    start = None
    end = None
    for ts in occurances:
        if start is None or ts < start:
            start = ts
        if end is None or ts > end:
            end = ts


    edges = [pd.to_datetime(v) for v in pd.date_range(start=start, end=end+timedelta(seconds=1), freq=freq).values]
    ts_edges = [ts.value for ts in edges]
    bucket_locations = np.digitize(ts_occurances, ts_edges)

    region_bucket_am_vals = {}
    region_bucket_am_avgs = {}
    for agent in data_set.agent_events_map.keys():
        region_bucket_am_vals[agent.region] = {}
        for bl in range(len(edges)):
            region_bucket_am_vals[agent.region][bl] = []
        region_bucket_am_avgs[agent.region] = {}


    for idx, she in enumerate(data_set.sys_health_events):
        bl = bucket_locations[idx]
        region_bucket_am_vals[she.agent.region][bl-1].append(she[sys_prop])

    for region,bucket_am_vals in region_bucket_am_vals.items():
        for b,am_vals in bucket_am_vals.items():
            region_bucket_am_avgs[region][b] = np.mean(am_vals)

    region_sorted_ams = {}

    for region,bucket_am_avgs in region_bucket_am_avgs.items():
        region_sorted_ams[region] = [bucket_am_avgs.get(i, np.nan) for i in range(len(edges))]

    DF = pd.DataFrame(region_sorted_ams, index=edges).bfill()
    ax = DF.plot(x_compat=True, rot=90, figsize=(16, 5),)
    ax.set_ylabel(sys_prop)
    ax.set_title(f"{sys_prop} by Region ({freq}.)")

    txt = f"Sample Size: {len(data_set.sys_health_events)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)

