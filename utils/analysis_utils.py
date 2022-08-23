import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import umap

np.random.seed(0)


def get_2D_umap_embeddings(feature_data: np.ndarray, random_state: int = 0):
    """
    get 2D umap embeddings for numpy array as x and y vectors

    Parameters
    ----------
    feature_data : np.ndarray
        feature data to find embeddings for
    random_state : int, optional
        random state for umap embeddings, by default 0

    Returns
    -------
    np.ndarray, np.ndarray
        X data vector, y data vector
    """
    # create umap object for dimension reduction
    reducer = umap.UMAP(random_state=random_state, n_components=2)

    # Fit UMAP and extract latent vars 1-2
    embedding = reducer.fit_transform(feature_data)
    embedding = np.transpose(embedding)

    # convert to seaborn-recognizable vectors
    x_data = embedding[0]
    y_data = embedding[1]

    return x_data, y_data


def show_2D_umap(
    x_data: np.ndarray, y_data: np.ndarray, metadata_series: pd.Series, save_path=None
):
    """
    show 2D umap, save if desired

    Parameters
    ----------
    x_data : np.ndarray
        vector with X coordinates
    y_data : np.ndarray
        vector with Y coordinates
    metadata_series : pd.Series
        metadata for how to color umap points
    save_path : pathlib.Path, optional
        path to save umap image, by default None
    """

    plt.figure(figsize=(15, 12))

    # Produce scatterplot with umap data, using metadata to color points
    sns_plot = sns.scatterplot(
        palette="bright",
        x=x_data,
        y=y_data,
        hue=metadata_series.tolist(),
        alpha=1,
        linewidth=0,
        s=5,
    )
    # Adjust legend
    sns_plot.legend(
        loc="center left", bbox_to_anchor=(1, 0.5), title=metadata_series.name
    )
    # Label axes, title
    sns_plot.set_xlabel("UMAP 1")
    sns_plot.set_ylabel("UMAP 2")
    sns_plot.set_title("2 Dimensional UMAP")

    # save umap
    if not save_path == None:
        plt.savefig(save_path, bbox_inches="tight")
