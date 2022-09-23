import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import rgb2hex
import seaborn as sns
import pandas as pd
import umap

# make random np operations reproducible
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


def show_2D_umap_grays(
    feature_data: np.ndarray,
    metadata_series: pd.Series,
    colored_classes: list,
    save_path=None,
    point_size: int = 5,
    alpha: float = 1,
    palette: str = "bright",
):        
    # create umap object for dimension reduction
    reducer = umap.UMAP(random_state=0, n_components=2)
    # Fit UMAP and extract latent vars
    embedding = pd.DataFrame(reducer.fit_transform(feature_data), columns=["UMAP1", "UMAP2"])
    # add phenotypic class to embeddings
    embedding[metadata_series.name] = metadata_series.tolist()
    
    fig = plt.figure(figsize=(15, 15))
    ax = fig.gca()
    cmap = sns.color_palette(palette, len(colored_classes))
    legend_elements = []

    # add each phenotypic class to 3d graph and legend
    for index, metadata_class in enumerate(
        embedding[metadata_series.name].unique().tolist()
    ):
        class_embedding = embedding.loc[
            embedding[metadata_series.name] == metadata_class
        ]
        x = class_embedding["UMAP1"]
        y = class_embedding["UMAP2"]
        if metadata_class in colored_classes:
            color = rgb2hex(cmap[colored_classes.index(metadata_class)])
        else:
            color = "#808080"
        
        ax.scatter(x, y, c=color, marker="o", alpha=alpha, s=point_size)
        legend_elements.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label=metadata_class,
                markerfacecolor=color,
                markersize=10,
            )
        )

    plt.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))
    # Label axes, title
    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")
    ax.set_title("2 Dimensional UMAP")

    # save umap
    if not save_path == None:
        plt.savefig(save_path, bbox_inches="tight")

    plt.show()


def show_2D_umap(
    x_data: np.ndarray,
    y_data: np.ndarray,
    metadata_series: pd.Series,
    save_path=None,
    point_size: int = 5,
    alpha: float = 1,
    palette: str = "bright",
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
    point_size : int, optional
        size of umap points, by default 5
    alpha : float, optional
        opacity of umap points, by default 1
    palette : str, optional
        color palette used to color points, by default "bright"
    """

    plt.figure(figsize=(15, 12))

    # Produce scatterplot with umap data, using metadata to color points
    sns_plot = sns.scatterplot(
        palette=palette,
        x=x_data,
        y=y_data,
        hue=metadata_series.tolist(),
        alpha=alpha,
        linewidth=0,
        s=point_size,
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


def show_1D_umap(
    feature_data: np.ndarray,
    metadata_series: pd.Series,
    save_path: str = None,
    point_size: int = 5,
    alpha: float = 1,
    palette: str = "bright",
):
    """
    show (and save) 1D umap, colored by metadata

    Parameters
    ----------
    feature_data : np.ndarray
        data for features to plot
    metadata_series : pd.Series
        metadata used to color data
    save_path : str, optional
        where to save umap, by default None
    point_size : int, optional
        size of umap points, by default 5
    alpha : float, optional
        opacity of umap points, by default 1
    palette : str, optional
        color palette used to color points, by default "bright"
    """
    # create umap object for dimension reduction
    reducer = umap.UMAP(random_state=0, n_components=1)

    # Fit UMAP and extract latent var 1
    embedding = pd.DataFrame(reducer.fit_transform(feature_data), columns=["UMAP1"])

    # create random y distribution to space out points
    y_distribution = np.random.rand(feature_data.shape[0])
    embedding["y_distribution"] = y_distribution.tolist()

    plt.figure(figsize=(15, 12))

    # Produce scatterplot with umap data, using phenotypic classses to color
    sns_plot = sns.scatterplot(
        palette=palette,
        x="UMAP1",
        y="y_distribution",
        data=embedding,
        hue=metadata_series.tolist(),
        alpha=alpha,
        linewidth=0,
        s=point_size,
    )
    # Adjust legend
    sns_plot.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    # Label axes, title
    sns_plot.set_xlabel("UMAP 1")
    sns_plot.set_ylabel("Random Distribution")
    sns_plot.set_title("1 Dimensional UMAP")

    # save umap
    if not save_path == None:
        plt.savefig(save_path, bbox_inches="tight")

def show_2D_umap_grays(
    feature_data: np.ndarray,
    metadata_series: pd.Series,
    colored_classes: list,
    save_path=None,
    point_size: int = 5,
    alpha: float = 1,
    palette: str = "bright",
):        
    # create umap object for dimension reduction
    reducer = umap.UMAP(random_state=0, n_components=2)
    # Fit UMAP and extract latent vars
    embedding = pd.DataFrame(reducer.fit_transform(feature_data), columns=["UMAP1", "UMAP2"])
    # add phenotypic class to embeddings
    embedding[metadata_series.name] = metadata_series.tolist()
    
    fig = plt.figure(figsize=(15, 15))
    ax = fig.gca()
    cmap = sns.color_palette(palette, len(colored_classes))
    legend_elements = []

    # add each phenotypic class to 3d graph and legend
    for index, metadata_class in enumerate(
        embedding[metadata_series.name].unique().tolist()
    ):
        class_embedding = embedding.loc[
            embedding[metadata_series.name] == metadata_class
        ]
        x = class_embedding["UMAP1"]
        y = class_embedding["UMAP2"]
        if metadata_class in colored_classes:
            color = rgb2hex(cmap[colored_classes.index(metadata_class)])
        else:
            color = "#808080"
        
        ax.scatter(x, y, c=color, marker="o", alpha=alpha, s=point_size)
        legend_elements.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label=metadata_class,
                markerfacecolor=color,
                markersize=10,
            )
        )

    plt.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))
    # Label axes, title
    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")
    ax.set_title("2 Dimensional UMAP")

    # save umap
    if not save_path == None:
        plt.savefig(save_path, bbox_inches="tight")

    plt.show()

def show_3D_umap(
    feature_data: np.ndarray,
    metadata_series: pd.Series,
    save_path=None,
    point_size: int = 5,
    alpha: float = 1,
    palette: str = "bright",
):
    """
    show (and save) 3D umap, colored by metadata

    Parameters
    ----------
    feature_data : np.ndarray
        data for features to plot
    metadata_series : pd.Series
        metadata used to color data
    save_path : str, optional
        where to save umap, by default None
    point_size : int, optional
        size of umap points, by default 5
    alpha : float, optional
        opacity of umap points, by default 1
    palette : str, optional
        color palette used to color points, by default "bright"
    """
    # create umap object for dimension reduction
    reducer = umap.UMAP(random_state=0, n_components=3)

    # Fit UMAP and extract latent vars 1-3
    embedding = pd.DataFrame(
        reducer.fit_transform(feature_data), columns=["UMAP1", "UMAP2", "UMAP3"]
    )

    # add phenotypic class to embeddings
    embedding[metadata_series.name] = metadata_series.tolist()

    fig = plt.figure(figsize=(17, 17))
    ax = fig.gca(projection="3d")
    cmap = sns.color_palette(palette, embedding[metadata_series.name].nunique())
    legend_elements = []

    # add each phenotypic class to 3d graph and legend
    for index, metadata_class in enumerate(
        embedding[metadata_series.name].unique().tolist()
    ):
        class_embedding = embedding.loc[
            embedding[metadata_series.name] == metadata_class
        ]
        x = class_embedding["UMAP1"]
        y = class_embedding["UMAP2"]
        z = class_embedding["UMAP3"]
        ax.scatter(x, y, z, c=rgb2hex(cmap[index]), marker="o", alpha=alpha, s=point_size)
        legend_elements.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label=metadata_class,
                markerfacecolor=rgb2hex(cmap[index]),
                markersize=10,
            )
        )

    plt.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))
    # Label axes, title
    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")
    ax.set_zlabel("UMAP 3")
    ax.set_title("3 Dimensional UMAP")

    # save umap
    if not save_path == None:
        plt.savefig(save_path, bbox_inches="tight")

    plt.show()
