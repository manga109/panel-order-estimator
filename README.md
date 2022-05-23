# Comic Panel Order Estimator
This tool uses the method described by Kovanen et al. [1] to estimate the order of comic panels as follows:

![Example estimation result.](./res/two-page.png)


## Setup
First install the package requirements:
```bash
pip install manga109api
```

Also, place the Manga109 dataset somewhere on your local environment.


## Usage
Basic usage:
```bash
python main.py --title ARMS --page 10
```

Advanced usage:
```bash
python main.py --title ARMS --page 10 \
    --dataset-root ./dataset/Manga109_released_2021_02_28 \
    --threshold 0.25 \
    --initial-cut two-page-four-panel
```

The `--threshold` and `--initial-cut` options are explained in the "Explanation" section.

This command yields the image shown at the top of this page.


## Explanation
The panel ordering algorithm is based on Kovanen et al. [1].
The algorithm consists of the tree construction phase and the tree interpretation phase:

Tree construction phase:

- 1. If the current set of panels is separable into two parts with a horizonal line (the pivot),
  - Separate the set, and for each set, start from Step 1
- 2. Otherwise, if the current set of panels is separable into two parts with a vertical line (the pivot),
  - Separate the set, and for each set, start from Step 1
- 3. Otherwise, mark the set as inseparable

Tree interpretation phase:

- For horizontal divisions, order the sets with a top-to-bottom order.
- For vertical divisions, order the sets with a right-to-left order.

For each horizontal and vertical division in the tree construction phase, a node representing the division is created.
The inseparable sets in Step 3 become the leaf nodes of this tree, and are either individual panels or a set of overlapping panels.
The recursive tree structure used here is accessible using `BoxOrderEstimator.boxnode.bbset`.


### Panel Separation Threshold Details
Panel separation is done as follows:

- 1. Choose a horizontal/vertical division pivot.
- 2. For each panel, determine if the panel is separable with the pivot.
  - If there is any panel that is inseparable with the pivot, mark the pivot as invalid.
  - If all of the panels are separable with the pivot, return the sets of panels separated with the pivot.

Whether a panel is separable with a pivot is determined as follows:

- If the pivot does not pass through the panel, it is separable.
- If the pivot passes through the panel,
  - Find the ratio of how much of the panel is cut through with the pivot. The ratio is determined as the area of the smaller half of the separated panel areas, divided by the entire area.
  - If the ratio is smaller than a given fixed threshold, the pivot is valid and the panel is separable (the pivot cuts a small enough size of the panel). If the ratio is larger than the threshold, the pivot is invalid and the panel is inseparable.

The `--threshold` option specifies the ratio threshold used in this step.


### Initial cuts
The algorithm above does not generally work for side-by-side pages (which are most of the pages in the Manga109 dataset), since side-by-side pages are actually two individual pages concatenated to one page. For such pages, the algorithm must initially try to divide the page with a vertical pivot that crosses the center of the page image to separate the left and right pages.

Similarly, four-panel comics such as Youchien Boueigumi (by Tenya) in the Manga109 dataset is actually _four_ different pages concatenated to one page. For such pages, the algorithm must initially try three pivots (which divides the page into four parts).

The `--initial-cut` option is used to handle such cases. This option can take the following choices:

- `one-page` (or `None`) - No initial pivots are used
- `two-page` - One initial vertical pivot along the center is used
- `two-page-four-panel` - For four-panel comics; three initial vertical pivots are used

By default, `--initial-cut` is set to `two-page`, which is the case for most of the comics in the Manga109 dataset.
The `one-page` option is intended for spreaded pages, but even for such pages, the default `two-page` option works for most cases.
Therefore, it should be sufficient to only occasionally use `two-page-four-panel` for four-panel comic data for this option.


## Initial Cut Examples

```bash
python main.py --title ARMS --page 10 --dataset-root ./dataset/Manga109_released_2021_02_28
```

For four-panel manga:

```bash
python main.py --title YouchienBoueigumi --page 10 --dataset-root ./dataset/Manga109_released_2021_02_28 --initial-cut two-page-four-panel
```

For center-spreaded pages:

```bash
python main.py --title Saisoku --page 50 --dataset-root ~/dataset/Manga109_released_2021_02_28 --initial-cut one-page
```

## References
Paper [1]:

```
@INPROCEEDINGS{7351614,
  author={Kovanen, Samu and Aizawa, Kiyoharu},
  booktitle={2015 IEEE International Conference on Image Processing (ICIP)},
  title={A layered method for determining manga text bubble reading order},
  year={2015},
  volume={},
  number={},
  pages={4283-4287},
  doi={10.1109/ICIP.2015.7351614}}
```
