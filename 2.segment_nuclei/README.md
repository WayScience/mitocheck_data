# 2. Segment Nuclei

In this module, we present our pipeline for segmenting nuclei from the mitosis movies.


### Segmentation

We use the CellPose nucleus model to segment the nuclei from each mitosis movie. 
CellPose was first introduced in [Stringer, C., Wang, T., Michaelos, M. et al., 2020](https://doi.org/10.1038/s41592-020-01018-x) and we use the [python implementation](https://github.com/mouseland/cellpose).

Stringer et al. trained the CellPose nucleus model on a diverse set of nuclei images and is therefore a good selection for our use case.
The CellPose python implementation was particularly useful for building reproducible pipelines.

## Step 1: Execute Training Data Segmentation

```bash
# Run this script to segment training data
bash 2.segment_training_nuclei.sh
```