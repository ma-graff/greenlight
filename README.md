# Traffic Optimization with Genetic Algorithm

This project demonstrates the use of a Genetic Algorithm (GA) to optimize traffic flow using Python, [SUMO](https://www.eclipse.org/sumo/), and [DEAP](https://deap.readthedocs.io/).

## Features

- Simulates traffic scenarios in SUMO
- Uses DEAP to evolve traffic signal timings
- Aims to minimize overall travel time and congestion

## Requirements

- Python 3.7+
- [SUMO](https://www.eclipse.org/sumo/)
- `deap`, `traci`, `numpy`

Install dependencies:
```bash
pip install deap numpy traci
```

## Usage

1. Configure your SUMO network and route files.
2. Run the optimization script:
    ```bash
    python optimize_traffic.py
    ```
3. Results and best signal timings will be displayed after evolution.

## Project Structure

- `optimize_traffic.py` — Main script for running the GA
- `sumo_config/` — SUMO network and route files

## References

- [DEAP Documentation](https://deap.readthedocs.io/)
- [SUMO Documentation](https://sumo.dlr.de/docs/)
