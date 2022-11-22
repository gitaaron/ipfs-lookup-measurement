import matplotlib.pyplot as plt
from helpers import calc, reduce
from models.model_data_set import DataSet
from models.model_time_interval import TimeInterval

def plot_num_providers_in_first_referal(data_set: DataSet, publish_age_interval: TimeInterval):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)

    retrievals = data_set.many_provider_retrievals
    retrievals = reduce.by_least_num_providers(retrievals, 5)
    if publish_age_interval is not None:
        retrievals = reduce.by_publish_age_interval(data_set, retrievals, publish_age_interval)

    breakdown = calc.first_referal_num_providers_in_percent(retrievals)

    ax1.bar([str(num) for num in sorted(list(breakdown.keys()))], list(breakdown.values())) 

    ax1.set_ylabel('Percent')

    ax1.set_xlabel('First Referal Provider Count')

    ax1.set_title('Number of Providers returned in First Referals')

    txt = f"Sample Size: {len(retrievals)}, Total Providers >= 5"
    if publish_age_interval is not None:
        txt+= f", Publish Age Interval: {publish_age_interval}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)

