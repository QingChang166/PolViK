# Local Agreement and Knowledge‐Graph Integrated Visualizations

This repository contains the data, scripts, and configuration needed to generate three-layer network visualizations of local peace agreements in the CAR and Mali. It combines geospatial shapefiles from GADM, cleaned agreement data at both the agreement and actor levels, and Python code to render the map, agreement-party, and conflict-rival layers with interconnecting edges.

'plot_with_edges_centroids.png': The bottom layer shows a map of the Central African Republic with a marker at Bria’s centroid, the location of the October 2017 agreement. The middle layer displays blue nodes for each agreement party. Orange lines connect each party node to the prefectures where that party was active before the local agreement was signed. The top layer shows red nodes for the parties’ rivals. Green dashed lines link each rival node to the agreement party it opposed.
