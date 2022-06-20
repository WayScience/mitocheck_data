# 2. Segment Nuclei

In this module, we present our pipline for segmenting nuclei from the mitosis movies.

### Segmentation

We use CellPose algorithm to segment the nuclei from each mitosis movie. 
CellPose was first introduced in [Stringer, C., Wang, T., Michaelos, M. et al., 2020](https://doi.org/10.1038/s41592-020-01018-x) and we use the [python implementation](https://github.com/mouseland/cellpose).