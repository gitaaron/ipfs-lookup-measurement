import matplotlib.pyplot as plt
from helpers import calc
from models.model_data_set import DataSet

def plot_num_providers_in_first_referal(data_set: DataSet):
    fig1, ax1 = plt.subplots(figsize=(12,6), dpi=80)

    retrievals = data_set.many_provider_retrievals

    breakdown = calc.first_referal_num_providers_in_percent(retrievals)

    ax1.bar(list(breakdown.keys()), list(breakdown.values())) 

    ax1.set_ylabel('Percent')

    ax1.set_xlabel('First Referal Provider Count')

    ax1.set_title('Number of Providers returned in First Referals')

    txt = f"Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
