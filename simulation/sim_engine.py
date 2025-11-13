# simulation/sim_engine.py
import simpy
import random
import statistics

class Machine:
    def __init__(self, env, name, mttf, mttr):
        self.env = env
        self.name = name
        self.mttf = mttf
        self.mttr = mttr
        self.resource = simpy.Resource(env, capacity=1)
        self.busy_time = 0.0
        self.downtime = 0.0
        self.failed = False
        self.schedule_next_failure()

    def schedule_next_failure(self):
        ttf = random.expovariate(1.0 / max(0.1, self.mttf))
        self.next_failure_time = self.env.now + max(0.0001, ttf)

    def fail_and_repair(self):
        self.failed = True
        down_start = self.env.now
        repair_time = random.expovariate(1.0 / max(0.1, self.mttr))
        yield self.env.timeout(repair_time)
        self.failed = False
        self.downtime += self.env.now - down_start
        self.schedule_next_failure()

def machine_failure_monitor(env, machine):
    while True:
        yield env.timeout(max(0.0, machine.next_failure_time - env.now))
        yield env.process(machine.fail_and_repair())

def job_process(env, job_id, machines, process_times, stats, defect_rate):
    arrival = env.now
    for i, machine in enumerate(machines):
        proc_time = max(0.01, process_times[i]())
        with machine.resource.request() as req:
            yield req
            remaining = proc_time
            while remaining > 1e-6:
                if machine.failed:
                    yield env.timeout(0.1)
                    continue
                t_until_fail = machine.next_failure_time - env.now
                if t_until_fail <= 0:
                    yield env.timeout(0.0)
                    continue
                step = min(remaining, t_until_fail)
                yield env.timeout(step)
                remaining -= step
            machine.busy_time += proc_time
    # finished
    finish_time = env.now
    stats['completed_times'].append(finish_time - arrival)
    stats['completion_times'].append(finish_time)
    stats['defects'].append(1 if random.random() < defect_rate else 0)

def job_generator(env, arrival_rate_per_min, machines, process_times, sim_time, stats, defect_rate):
    job_id = 0
    while env.now < sim_time:
        inter = random.expovariate(arrival_rate_per_min)
        yield env.timeout(inter)
        job_id += 1
        env.process(job_process(env, job_id, machines, process_times, stats, defect_rate))
        stats['generated'] += 1

def run_simulation_once(params, sim_time_minutes=8*60, seed=None):
    if seed is not None:
        random.seed(seed)
    env = simpy.Environment()
    machine_names = ['CNC', 'Finish', 'Assembly']
    machines = []
    for i, name in enumerate(machine_names):
        mac = Machine(env, name, params['mttf'][i], params['mttr'][i])
        machines.append(mac)
        env.process(machine_failure_monitor(env, mac))

    process_times = params['process_times']  # list of callables returning minutes
    arrival_rate_per_min = params['arrival_rate_per_min']  # e.g., 1/20 => 1 job every 20 minutes
    defect_rate = params.get('defect_rate', 0.05)

    stats = {'generated':0, 'completed_times':[], 'completion_times':[], 'defects':[]}
    env.process(job_generator(env, arrival_rate_per_min, machines, process_times, sim_time_minutes, stats, defect_rate))
    env.run(until=sim_time_minutes)

    throughput_per_hr = len(stats['completion_times']) / (sim_time_minutes / 60.0)
    avg_lead_time_min = statistics.mean(stats['completed_times']) if stats['completed_times'] else None
    total_down = sum(m.downtime for m in machines)
    utilization = {m.name: m.busy_time / sim_time_minutes for m in machines}
    quality_rate = 1.0 - (sum(stats['defects']) / len(stats['defects'])) if stats['defects'] else 1.0

    return {
        'throughput_per_hr': throughput_per_hr,
        'avg_lead_time_min': avg_lead_time_min,
        'generated': stats['generated'],
        'completed': len(stats['completion_times']),
        'downtime_total_min': total_down,
        'machine_utilization': utilization,
        'quality_rate': quality_rate
    }
