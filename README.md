
# GreenLight: Traffic Signal Optimization with Genetic Algorithms

**Team:** Leeza Shewchenko, Matt Graff, Jordan Bona

## Project Summary
GreenLight is a Python-based toolkit for optimizing traffic signal timings using genetic algorithms (GA) and the SUMO traffic simulator. The goal is to reduce vehicle wait times and emissions in urban networks, with a focus on Victoria, BC. The system automatically tunes traffic light phases to minimize a multi-objective fitness function combining CO₂ emissions, fuel consumption, and total waiting time.

## Features
- **Automated traffic light optimization** using a customizable genetic algorithm
- **SUMO integration** for realistic traffic simulation and emissions modeling
- **Flexible fitness function**: minimize CO₂, fuel, and waiting time (with normalization and weighting options)
- **Jupyter notebook tutorials** for reproducible experiments and visualization
- **Support for real-world and synthetic networks**

## Requirements
- Python 3.8+
- [SUMO](https://www.eclipse.org/sumo/) (Simulation of Urban MObility) installed and available in your system PATH
- Python packages:
  - numpy
  - pandas
  - matplotlib
  - (optional) jupyter

*Install Python dependencies using `setup.ipynb`*

## Getting Started

To set up the environment and run the optimization workflow, please follow the instructions in `setup.ipynb` and complete the full tutorial in `tutorial.ipynb`.

All code examples, usage, and visualization steps are provided in the notebooks for a reproducible and interactive experience.

## Fitness Function
The default fitness function is:

```python
fitness = -(CO2_emissions + fuel_consumption + waiting_time)
```
You can adjust weights in `ga.py` if you want to prioritize one metric.

## Data Sources
- OpenStreetMap data
- City of Victoria Traffic Cabinet data

