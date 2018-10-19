# TractographyMetrics
3D Slicer plug-in for the 'TractographyMetrics' tool

## Interface
The module takes three mandatory input. The fiber bundle to analyze, one scalar volume and the path of the text file.

Attention must be put when selecting the metrics maps (one mandatory, two optionals). The correspondence volume/name 
is not automatically verified. This could lead to incomprehension if the volumes are wrongly assigned
to the input field.
 
If the box 'Plot distribution' is ticked the scene will switch automatically to a layout with a plot window
containing the distribution of the selected metrics along the fiber lengths.

Each fiber is divided in twenty portions. In every fiber portions the metric values are mapped for all the points 
composing them. The section score is then computed as the mean of the metrics values.

Additionally, the output can be saved in the Excel file format or in a CSV table clicking the respective box.
The paths will be assumed the same as the text file, and only the extension is changed.

It is possible to quickly note key information, inserting them at the beginning of the text file. To do so, use
the text box in the final part of the interface.

 License
----

Apache License 2.0
