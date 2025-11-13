# simulation/runner.py
import os, csv, random
from simulation.sim_engine import run_simulation_once

OUTDIR = 'simulation/precomputed_results'
os.makedirs(OUTDIR, exist_ok=True)

def baseline_params():
    def p1(): return max(0.1, random.normalvariate(10,1.5))
    def p2(): return max(0.1, random.normalvariate(8,1.0))
    def p3(): return max(0.1, random.normalvariate(6,0.7))
    return {'arrival_rate_per_min': 1/20.0, 'mttf':[200,300,400], 'mttr':[40,30,30], 'process_times':[p1,p2,p3], 'defect_rate':0.08}

def connected_params():
    def p1(): return max(0.1, random.normalvariate(9,1.2))
    def p2(): return max(0.1, random.normalvariate(7.5,0.9))
    def p3(): return max(0.1, random.normalvariate(5.5,0.6))
    return {'arrival_rate_per_min': 1/18.0, 'mttf':[300,450,600], 'mttr':[30,20,20], 'process_times':[p1,p2,p3], 'defect_rate':0.05}

def predictive_params():
    def p1(): return max(0.1, random.normalvariate(8.5,1.0))
    def p2(): return max(0.1, random.normalvariate(7.0,0.8))
    def p3(): return max(0.1, random.normalvariate(5.0,0.4))
    return {'arrival_rate_per_min': 1/16.0, 'mttf':[600,900,1200], 'mttr':[15,12,10], 'process_times':[p1,p2,p3], 'defect_rate':0.02}

SCENARIOS = {
    'baseline': baseline_params,
    'connected': connected_params,
    'predictive': predictive_params
}

def run_and_save(n_rep=30, sim_time_min=8*60):
    for name, fn in SCENARIOS.items():
        csvf = os.path.join(OUTDIR, f'{name}.csv')
        with open(csvf, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['rep','throughput_per_hr','avg_lead_time_min','generated','completed','downtime_total_min','quality_rate'])
            for rep in range(1, n_rep+1):
                seed = rep * 100 + 11
                random.seed(seed)
                params = fn()
                res = run_simulation_once(params, sim_time_minutes=sim_time_min, seed=seed)
                w.writerow([rep, res['throughput_per_hr'], res['avg_lead_time_min'], res['generated'], res['completed'], res['downtime_total_min'], res['quality_rate']])
        print('Wrote', csvf)

if __name__ == '__main__':
    run_and_save()
