"""Proposed bounded nstep=0 check. Requires later explicit approval and systemd limits.

Never use this for an SCF; input must equal the sealed first pilot plus nstep=0.
All partial files are retained. An initialization return code is not SCF success.
"""
import json
import os
from pathlib import Path
import re
import signal
import shutil
import subprocess
import time

from qe75_fedora_v1 import ROOT, resolve, sha, software, verify_package, runtime_environment


def main():
    config = json.loads((ROOT / 'configs/qe75-fedora-v1.json').read_text())
    if config.get('initialization_execution_approved') is not True:
        raise ValueError('Initialization is not approved; no process launched')
    if config.get('scientific_execution_approved') is not False:
        raise ValueError('This runner is only for non-SCF initialization')
    if (config['ranks'], config['threads'], config['memory_max_GiB'],
            config['smoke_wall_seconds']) != (4, 1, 8, 600):
        raise ValueError('Changed v1 resource layout requires a new revision')
    verify_package(config)
    if not config['pw_sha256'] or not config['mpi_sha256']:
        raise ValueError('Reviewed executable pins required')
    software(config)
    cg = Path('/sys/fs/cgroup') / Path('/proc/self/cgroup').read_text().strip().split('::')[1].lstrip('/')
    if int((cg / 'memory.max').read_text()) != 8 * 2**30 or int((cg / 'memory.swap.max').read_text()) != 0:
        raise ValueError('Expected hard cgroup memory cap 8 GiB and zero swap')
    properties = subprocess.check_output(['systemctl', '--user', 'show', 'qe75-init01.service',
                                         '-p', 'RuntimeMaxUSec', '-p', 'KillMode', '-p', 'ControlGroup',
                                         '-p', 'TimeoutStopUSec', '-p', 'SendSIGKILL'], text=True)
    props = dict(line.split('=', 1) for line in properties.splitlines())
    if (props.get('RuntimeMaxUSec') != '9min 45s' or props.get('KillMode') != 'control-group'
            or props.get('TimeoutStopUSec') != '15s' or props.get('SendSIGKILL') != 'yes'
            or Path('/sys/fs/cgroup' + props.get('ControlGroup', '')) != cg):
        raise ValueError('Required systemd wall/termination limits not verified')
    available = int(re.search(r'MemAvailable:\s+(\d+)', Path('/proc/meminfo').read_text())[1]) * 1024
    if available < 10 * 2**30 or shutil.disk_usage(ROOT).free < 30 * 2**30:
        raise ValueError('Need 10 GiB available physical RAM and 30 GiB persistent disk')
    work = resolve(config['smoke_root'])
    if not work.is_relative_to(ROOT / 'local'):
        raise ValueError('Persistent local storage required')
    staging = json.loads((work / 'staging.json').read_text())
    original = (resolve(config['package']) / 'inputs/uio66_110111_H2O_s28_f0.010_complex__baseline.in').read_text()
    expected = re.sub(r'(&CONTROL\b)', r'\1\n  nstep=0,', original, count=1, flags=re.I)
    if (work / 'input.in').read_text() != expected or sha(work / 'input.in') != staging['input_sha256']:
        raise ValueError('Staged initialization input differs')
    for pp in (resolve(config['package']) / 'pseudo').iterdir():
        if pp.is_file() and sha(work / 'pseudo' / pp.name) != sha(pp):
            raise ValueError('Staged potential differs')
    # Refuse reuse even after a failed or interrupted attempt.
    with (work / 'execution-started.json').open('x') as f:
        json.dump({'time_unix': time.time(), 'config': config, 'systemd': props}, f, indent=2)
    command = [str(resolve(config['mpi_executable'])), *config['mpi_arguments'],
               str(resolve(config['pw_executable'])), '-in', 'input.in']
    start = time.monotonic()
    result = {'command': command, 'scientific_result': False, 'status': 'initializing'}
    proc = None
    try:
        with (work / 'stdout.log').open('x') as out, (work / 'stderr.log').open('x') as err, (work / 'resources.jsonl').open('x') as log:
            proc = subprocess.Popen(command, cwd=work, stdout=out, stderr=err, start_new_session=True,
                                    env=runtime_environment(config))
            while proc.poll() is None:
                elapsed = time.monotonic() - start
                size = sum(p.stat().st_size for p in work.rglob('*') if p.is_file())
                free = shutil.disk_usage(work).free
                log.write(json.dumps({'elapsed': elapsed, 'work_bytes': size, 'free_bytes': free,
                                      'memory_current': (cg / 'memory.current').read_text().strip()}) + '\n')
                log.flush()
                if elapsed >= 570 or size >= 10 * 2**30 or free < 20 * 2**30:
                    raise RuntimeError('Time/storage stop condition reached')
                time.sleep(1)
        result.update(returncode=proc.returncode, status='initialization_finished_REVIEW_REQUIRED')
    finally:
        if proc is not None and proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
            result['status'] = 'stopped_incomplete'
        result.update(elapsed_seconds=time.monotonic() - start,
                      memory_peak=(cg / 'memory.peak').read_text(),
                      memory_events=(cg / 'memory.events').read_text())
        (work / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    # Do not classify 255 as success; review expected dry-run status and logs.
    return 0 if proc.returncode in (0, 255) else 1


if __name__ == '__main__':
    raise SystemExit(main())
