# 3. Normalize Data

In this module, we use [UMAP](https://github.com/lmcinnes/umap) on control data to suggest batch effects are not the dominant signal in the mitosis movies.

Next, we derive a normalization scaler with [sklearn.preprocessing.StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html) from the negative control features.
[Caicedo et al, 2017](https://www.nature.com/articles/nmeth.4397) explain why the negative control features are a good normalization population for our use case:
> When choosing the normalizing population, we suggest the use of control samples (assuming that they are present in sufficient quantity), because the presence of dramatic phenotypes may confound results. This procedure is good practice regardless of the normalization being performed within plates or across the screen.

Because batch effects are likely not the dominant signal in the mitosis movies, we perform normalization across the entire screen.
In other words, we create one normalization scaler from all negative control features and apply this normalization scaler to all mitosis movie feature data.

