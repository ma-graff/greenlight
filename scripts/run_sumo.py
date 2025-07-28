import subprocess
import sys

def run_sumo(sumocfg_path, sumo_binary='sumo'):
    """
    Runs SUMO with the given configuration file.
    Args:
        sumocfg_path (str): Path to the .sumocfg file.
        sumo_binary (str): SUMO binary to use ('sumo' or 'sumo-gui').
    Returns:
        int: Return code from the SUMO process.
    """
    cmd = [sumo_binary, '-c', sumocfg_path]
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_sumo.py <path_to_sumocfg> [sumo_binary]")
        sys.exit(1)
    sumocfg_path = sys.argv[1]
    sumo_binary = sys.argv[2] if len(sys.argv) > 2 else 'sumo'
    ret_code = run_sumo(sumocfg_path, sumo_binary)
    print(f"SUMO exited with code {ret_code}")
