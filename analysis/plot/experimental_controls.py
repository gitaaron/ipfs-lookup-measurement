from pickled.model_retrieval import Retrieval
import matplotlib.pyplot as plt
import pandas as pd

def plot_num_providers(retrievals:list[Retrieval], title: str):

    num_providers_in_retrievals = []

    for ret in retrievals:
        num_providers_in_retrievals.append(len(ret.provider_peers))

    start_dates = [ret.retrieval_started_at for ret in retrievals]

    DF = pd.DataFrame(
            {
                "num_providers_in_retrievals":num_providers_in_retrievals,
            }, index=start_dates)

    ax = DF.plot(x_compat=True, rot=90, figsize=(16, 5),)
    ax.set_ylabel('Number Providers found during Retrieval')
    ax.set_title(title)
    txt = f"Sample Size: {len(retrievals)}"
    plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', fontsize=6)
