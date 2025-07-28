
import xml.etree.ElementTree as ET
import random
import os
import shutil
import subprocess
import sys
import argparse

# --- Parameter bounds (customize as needed) ---
PHASE_BOUNDS = {
    'duration': (5, 60),
    'minDur': (5, 30),
    'maxDur': (30, 90)
}

# --- Helper functions for XML manipulation ---
def load_netxml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return tree, root

def find_file_with_ext(folder, ext):
    for f in os.listdir(folder):
        if f.endswith(ext):
            return os.path.join(folder, f)
    raise FileNotFoundError(f"No file with extension {ext} found in {folder}")

def generate_sumocfg(netxml_path, rouxml_path, sumocfg_path, emission_path):
    config = f'''<configuration>\n  <input>\n    <net-file value=\"{os.path.basename(netxml_path)}\"/>\n    <route-files value=\"{os.path.basename(rouxml_path)}\"/>\n  </input>\n  <output>\n    <emission-output value=\"{os.path.basename(emission_path)}\"/>\n  </output>\n</configuration>\n'''
    with open(sumocfg_path, 'w') as f:
        f.write(config)

def extract_tlLogic(root):
    return [tl for tl in root.findall('tlLogic')]

def modify_tlLogic(tlLogic, phase_params):
    for phase, params in zip(tlLogic.findall('phase'), phase_params):
        phase.set('duration', str(params['duration']))
        if 'minDur' in params: phase.set('minDur', str(params['minDur']))
        if 'maxDur' in params: phase.set('maxDur', str(params['maxDur']))
    return tlLogic

def save_netxml(tree, out_path):
    tree.write(out_path, encoding='utf-8', xml_declaration=True)

# --- Genetic Algorithm Components ---
def random_phase_params(num_phases):
    params = []
    for _ in range(num_phases):
        duration = random.randint(*PHASE_BOUNDS['duration'])
        minDur = random.randint(*PHASE_BOUNDS['minDur'])
        maxDur = random.randint(max(minDur, PHASE_BOUNDS['maxDur'][0]), PHASE_BOUNDS['maxDur'][1])
        params.append({'duration': duration, 'minDur': minDur, 'maxDur': maxDur})
    return params

def mutate(individual, mutation_rate=0.1):
    for phase in individual:
        if random.random() < mutation_rate:
            phase['duration'] = random.randint(*PHASE_BOUNDS['duration'])
        if random.random() < mutation_rate:
            phase['minDur'] = random.randint(*PHASE_BOUNDS['minDur'])
        if random.random() < mutation_rate:
            phase['maxDur'] = random.randint(max(phase['minDur'], PHASE_BOUNDS['maxDur'][0]), PHASE_BOUNDS['maxDur'][1])
    return individual

def crossover(parent1, parent2):
    child = []
    for p1, p2 in zip(parent1, parent2):
        chosen = p1.copy() if random.random() < 0.5 else p2.copy()
        child.append(chosen)
    return child

def evaluate_fitness(netxml_path, rouxml_path, working_dir, run_sumo_func, emission_file):
    # Generate .sumocfg in working_dir
    sumocfg_path = os.path.join(working_dir, 'ga_tmp.sumocfg')
    generate_sumocfg(netxml_path, rouxml_path, sumocfg_path, emission_file)
    # Run SUMO simulation and parse emissions (minimize total CO2, fuel, and waiting time)
    run_sumo_func(sumocfg_path)
    # Parse emission file (assume exists after run)
    try:
        tree = ET.parse(emission_file)
        root = tree.getroot()
        total_co2 = 0.0
        total_fuel = 0.0
        total_waiting = 0.0
        for timestep in root.findall('timestep'):
            for vehicle in timestep.findall('vehicle'):
                total_co2 += float(vehicle.get('CO2', 0))
                total_fuel += float(vehicle.get('fuel', 0))
                total_waiting += float(vehicle.get('waiting', 0))
        # Minimize the sum of all three metrics
        fitness = -(total_co2 + total_fuel + total_waiting)
        return fitness
    except Exception as e:
        print(f"Error evaluating fitness: {e}")
        return float('-inf')

# --- Main GA Loop ---
def genetic_algorithm(
    input_dir, working_dir, output_dir, run_sumo_func,
    population_size=10, generations=5, mutation_rate=0.1, elite_size=2
):
    base_netxml = find_file_with_ext(input_dir, '.net.xml')
    base_rouxml = find_file_with_ext(input_dir, '.rou.xml')
    # Copy base files to working_dir
    os.makedirs(working_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    netxml_working = os.path.join(working_dir, os.path.basename(base_netxml))
    rouxml_working = os.path.join(working_dir, os.path.basename(base_rouxml))
    shutil.copy(base_netxml, netxml_working)
    shutil.copy(base_rouxml, rouxml_working)

    tree, root = load_netxml(netxml_working)
    tlLogics = extract_tlLogic(root)
    num_phases = [len(tl.findall('phase')) for tl in tlLogics]

    # Initialize population
    population = []
    for _ in range(population_size):
        individual = [random_phase_params(n) for n in num_phases]
        population.append(individual)

    all_fitness_records = []  # To store (fitness, individual, gen, idx)
    for gen in range(generations):
        print(f"Generation {gen+1}")
        fitness_scores = []
        for idx, individual in enumerate(population):
            # Apply individual's params to a copy of the netxml
            tree_copy, root_copy = load_netxml(netxml_working)
            for tl, params in zip(extract_tlLogic(root_copy), individual):
                modify_tlLogic(tl, params)
            netxml_out = os.path.join(working_dir, f"ga_net_{gen}_{idx}.net.xml")
            save_netxml(tree_copy, netxml_out)
            emission_file = os.path.join(output_dir, f"genes/emissions_{gen}_{idx}.xml")
            # Evaluate fitness
            fitness = evaluate_fitness(netxml_out, rouxml_working, working_dir, run_sumo_func, emission_file)
            fitness_scores.append((fitness, individual))
            all_fitness_records.append((fitness, individual, gen, idx))
            print(f"  Individual {idx+1}: Fitness = {fitness}")
        # Select elites
        fitness_scores.sort(reverse=True, key=lambda x: x[0])
        elites = [ind for _, ind in fitness_scores[:elite_size]]
        # Generate new population
        new_population = elites.copy()
        while len(new_population) < population_size:
            parents = random.sample(elites, 2)
            child = crossover(parents[0], parents[1])
            child = [mutate(phase, mutation_rate) for phase in child]
            new_population.append(child)
        population = new_population[:population_size]
    print("GA complete.")

    # Output summary CSV of all variants
    import csv
    summary_path = os.path.join(output_dir, "ga_top_variants.csv")
    # Sort all records by fitness (descending, since negative CO2)
    all_fitness_records.sort(reverse=True, key=lambda x: x[0])
    with open(summary_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["Rank", "Generation", "Individual", "Fitness (negative)", "Phase Settings"])
        for rank, (fitness, individual, gen, idx) in enumerate(all_fitness_records, 1):
            # Flatten phase settings for CSV
            phase_strs = []
            for tl_idx, phases in enumerate(individual):
                for phase_idx, phase in enumerate(phases):
                    phase_strs.append(f"TL{tl_idx}_P{phase_idx}:" + ",".join(f"{k}={v}" for k,v in phase.items()))
            writer.writerow([rank, gen+1, idx+1, fitness, " | ".join(phase_strs)])
    print(f"All variants summary written to {summary_path}")

# --- Example usage ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GA for SUMO traffic light optimization.")
    parser.add_argument('--input_dir', required=True, help='Folder containing base .net.xml and .rou.xml')
    parser.add_argument('--output_dir', required=True, help='Output directory for emissions results (genes will be in output_dir/genes)')
    parser.add_argument('--population_size', type=int, default=6)
    parser.add_argument('--generations', type=int, default=3)
    parser.add_argument('--mutation_rate', type=float, default=0.2)
    parser.add_argument('--elite_size', type=int, default=2)
    args = parser.parse_args()

    working_dir = os.path.join(args.output_dir, 'genes')
    sys.path.append(os.path.dirname(__file__))
    from run_sumo import run_sumo
    genetic_algorithm(
        args.input_dir,
        working_dir,
        args.output_dir,
        run_sumo,
        population_size=args.population_size,
        generations=args.generations,
        mutation_rate=args.mutation_rate,
        elite_size=args.elite_size
    )
