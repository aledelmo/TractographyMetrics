# Tractography Analysis
Neural connections geometrical and functional analysis

![tractography](https://i.imgur.com/FR9nYRm.jpg)

Compute multiple statistics about fiber bundles. Descriptive statistics and quantitative information about image information
and geometrical characteristics.

* **Bundle properties**
    * Number of fibers: number of streamlines composing the tractogram.
    * Number of points: number of points composing a streamline
* **Geometrical properties**
    * Lengths: length of the fiber (in mm). Computed by adding up the lengths of all segments. Feature: EDT
    * Shortest path: length of the straight segment connecting fibers endpoints
    * Turning angle: turning angle projected (Winding). Cumulative signed angle between each line segment and the previous one, expressed in degrees.
* **Connectivity properties**
    * Seeds position: position of the starting point (seed) of a streamline
    * Termination position: position of the endpoint (termination condition respected) of a streamline
    * Mid-point position: position of the central point of a streamline
* **Diffusion properties**
    * b-zero intensity: mapping of every point of the streamline on the baseline image. The exact mapped value is computed with a weighted interpolation of the b-zeros of the 12-connected voxel space around the point.
    * FA value: Mapping of every point of the streamline on the FA map.
    * MD value: Mapping of every point of the streamline on the MD map.
    
## Installation and Usage.

Installation:
```sh
$ git clone https://github.com/aledelmo/TractographyMetrics
$ cd TractographyMetrics
$ pip install -r requirements.txt
$ python -m tractography_metrics.py <tractogram_filepath> <output_txt_file>
```

To enrich analysis with diffusion information use the following optional keywords:

| short flag | long flag | Action |
| ------ | ------ | ------ |
| ```-bzero <filepath>``` | ```--b_zero <filepath>``` | Compute stats on the bzero volume  |
| ```-fa <metric_filepath>``` | ```--Fractional_Anisotropy <metric_filepath>``` | Compute stats on the FA metric volume |
| ```-md <metric_filepath>``` | ```--metric_filepath``` | Compute stats on the MD metric volume |

Save the output in a different format with the optional flags:

| short flag | long flag |
| ------ | ------ |
| ```-csv``` | ```--save_csv``` |
| ```-xlsx``` | ```--save_xlsx``` |

Add a header:

| short flag | long flag | Action |
| ------ | ------ | ------ |
| ```-hd <text>``` | ```--header <text>``` | Add any string of text to the stats |

When working on huge amounts of fibers you might experience computational issues. Try to downsample the tractogram with:

| short flag | long flag | Action |
| ------ | ------ | ------ |
| ```-r <resampling_percentage>``` | ```--resample <resampling_percentage>``` | Specify the downsample percentage of the tractogram fibers (value between 0 and 100) |

## Contacts

For any inquiries please contact: 
[Alessandro Delmonte](https://aledelmo.github.io) @ [alessandro.delmonte@institutimagine.org](mailto:alessandro.delmonte@institutimagine.org)

## License

This project is licensed under the [Apache License 2.0](LICENSE) - see the [LICENSE](LICENSE) file for
details
