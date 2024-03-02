# 2. Format Training Data

In this module, we associate features extracted from labeled frames with their Mitocheck-assigned phenotypic class label.
After extracting the features from these labeled frames with `idrstream`, we associate the center coordinates of cells from [features.samples.txt](../mitocheck_metadata/features.samples.txt) with their `idrstream`-derived outlines to assign a phenotypic class (as assigned by Mitocheck) to cell features.

**Note:** We replace `Shape1` and `Shape3` with binuclear and polylobed respectively (their corresponding classes).
See [#16](https://github.com/WayScience/mitocheck_data/issues/16) for more details.

## Step 1: Format Training Data

Use the commands below to format the training data:

```sh
# Make sure you are located in 2.format_training_data
cd 2.format_training_data

# Activate mitocheck_data conda environment
conda activate mitocheck_data

# Format data
bash format_training_data.sh
```
