"""Guarded Linux, single-node QE pilot. Default preflight never performs SCF.

No scheduler submission, retries, deletion, ionic relaxation or automatic next stage.
Stdlib only. Actual Linux/QE integration remains unverified until an installation exists.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import time
import xml.etree.ElementTree as ET

# QE 7.5 Modules/constants.f90 constants, not a transfer of a VASP cutoff.
RY_EV = 4.3597447222071e-18 / 1.602176634e-19 / 2
BOHR_A = 0.529177210903


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


def dump(path, obj):
    Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')


def verify_package(package):
    hashes=json.loads((package/'file_hashes.json').read_text())
    for name, digest in hashes.items():
        p=(package/name).resolve()
        if not p.is_relative_to(package.resolve()) or sha(p)!=digest:
            raise ValueError('Package checksum mismatch: '+name)
    return len(hashes)


def verify_retained(evidence, scratch):
    """Verify downloaded evidence AND restart trees, including failed jobs."""
    counts={}
    for directory,filename in ((evidence,'evidence_hashes.json'),(scratch,'scratch_hashes.json')):
        manifest=json.loads((evidence/filename).read_text())
        for name,expected in manifest.items():
            path=(directory/name).resolve()
            if not path.is_relative_to(directory.resolve()) or sha(path)!=expected:
                raise ValueError('Retained artifact mismatch: '+name)
        counts[filename]=len(manifest)
    states=json.loads((evidence/'states.json').read_text())
    return {'verified_files':counts,'states':states,
            'two_complete':len(states)==2 and all(s['status']=='SCF_complete_pending_numerical_review' for s in states),
            'caution':'Hash verification does not establish numerical convergence or chemical accuracy.'}


def parse_result(stdout, xml_path, geometry, electrons, ranks):
    """Require completed, one-step SCF plus matching high-precision XML geometry.

    XML uses Hartree atomic units; stdout uses Ry and Ry/bohr. Never double-add D3.
    Synthetic format tests are not a substitute for validating the first real QE output.
    """
    if 'JOB DONE.' not in stdout or 'convergence has been achieved' not in stdout:
        raise ValueError('Incomplete or unconverged SCF')
    if 'convergence NOT achieved' in stdout or 'Error in routine' in stdout:
        raise ValueError('QE reported failure')
    if not re.search(r'Program PWSCF\s+v\.7\.5\b',stdout):
        raise ValueError('Unexpected QE version')
    energies=re.findall(r'!\s+total energy\s*=\s*([-+\d.EeDd]+)\s+Ry',stdout)
    if len(energies)!=1:
        raise ValueError('Expected exactly one converged SCF energy')
    root=ET.parse(xml_path).getroot()
    if root.attrib.get('Units')!='Hartree atomic units':
        raise ValueError('Unrecognized XML units')
    # Strip namespaces without altering archived XML.
    for node in root.iter(): node.tag=node.tag.split('}')[-1]
    def get(path):
        element=root.find(path)
        if element is None or element.text is None:raise ValueError('Missing XML field '+path)
        return element.text.strip()
    if get('exit_status')!='0' or get('input/control_variables/calculation')!='scf':
        raise ValueError('Failed or non-SCF XML')
    if get('output/convergence_info/scf_conv/convergence_achieved').lower()!='true':
        raise ValueError('XML SCF convergence absent')
    if int(get('parallel_info/nprocs'))!=ranks or int(get('parallel_info/nthreads'))!=1:
        raise ValueError('Actual MPI/thread allocation differs')
    if abs(float(get('output/band_structure/nelec'))-electrons)>1e-8:
        raise ValueError('Output electron count differs')
    creator=root.find('general_info/creator')
    if creator is None or creator.attrib.get('VERSION')!='7.5':
        raise ValueError('XML code version differs')
    structure=root.find('output/atomic_structure')
    atoms=structure.findall('atomic_positions/atom') if structure is not None else []
    from_symbols=geometry['symbols']
    if [a.attrib.get('name') for a in atoms]!=from_symbols:
        raise ValueError('Output atom identities/order differ')
    coords=[[float(v)*BOHR_A for v in a.text.split()] for a in atoms]
    cell=[[float(v)*BOHR_A for v in structure.find('cell/'+k).text.split()] for k in ('a1','a2','a3')]
    for actual,expected in ((coords,geometry['positions_A']),(cell,geometry['cell_A'])):
        if len(actual)!=len(expected) or any(len(a)!=3 or any(not math.isfinite(x) or abs(x-y)>2e-8 for x,y in zip(a,b)) for a,b in zip(actual,expected)):
            raise ValueError('Output geometry changed beyond unit/serialization precision')
    e=float(energies[0].replace('D','E').replace('d','e'))
    xml_e=float(get('output/total_energy/etot'))*2
    if not math.isfinite(e) or abs(e-xml_e)>2e-7:
        raise ValueError('Text/XML total energies disagree')
    forces=[]
    for line in get('output/forces').splitlines():
        values=[float(v)*2*RY_EV/BOHR_A for v in line.split()]
        if values:forces.append(values)
    if len(forces)!=len(atoms) or any(len(f)!=3 or not all(math.isfinite(v) for v in f) for f in forces):
        raise ValueError('Missing/nonfinite/wrong-shaped forces')
    return {'energy_eV':e*RY_EV,'forces_eV_A':forces,'electronic_converged':True,'ionic_steps':0,
            'charge':0,'spin':'nonmagnetic','code_version':'QE 7.5',
            'energy_convention':'converged total SCF energy including pairwise D3(BJ), no extra addition',
            'energy_uncertainty_eV':None,'actual_MPI_ranks':ranks,'actual_threads':1,
            'SCF_iterations':int(get('output/convergence_info/scf_conv/n_scf_steps')),
            'geometry_check_tolerance_A':2e-8,'note':'Numerical convergence and physical accuracy not established'}


def directory_bytes(path):
    total=0
    for p in path.rglob('*'):
        try:
            if p.is_file():total+=p.stat().st_size
        except FileNotFoundError:pass
    return total


def session_rss(sid):
    """Sample sum of rank RSS; includes shared pages repeatedly, not true node peak."""
    total=0
    for p in Path('/proc').glob('[0-9]*'):
        try:
            if os.getsid(int(p.name))==sid:
                total+=int(re.search(r'^VmRSS:\s+(\d+)',(p/'status').read_text(),re.M)[1])*1024
        except (OSError,TypeError,ProcessLookupError):pass
    return total


def stop_group(proc):
    if proc.poll() is None:
        os.killpg(proc.pid,signal.SIGTERM)
        try:proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=15)


def validate_slurm(config, environment, job_text):
    """Cluster revision: validate a real one-node allocation, never infer it from login."""
    if config.get('runtime_mode')=='cse_slurm_v1' and re.search(r'gres[/:]gpu',job_text,re.I):
        raise ValueError('CSE water pilot is CPU-only; GPU allocation rejected')
    job={k:v for k,v in re.findall(r'(\w+)=([^\s]+)',job_text)}
    if not config.get('site_layout_verified') or not config.get('allocation_charge_reviewed'):
        raise ValueError('Site MPI layout and allocation charge review required')
    ranks=config.get('ranks')
    if not isinstance(ranks,int) or ranks<1 or config.get('threads')!=1:
        raise ValueError('Expected verified MPI rank count and one thread per rank')
    expected={'JobId':environment.get('SLURM_JOB_ID'),'JobState':'RUNNING','NumNodes':'1',
              'NumCPUs':str(ranks),'NumTasks':str(ranks),'CPUs/Task':'1',
              'TimeLimit':'04:00:00','Account':config.get('slurm_account'),
              'Partition':config.get('slurm_partition')}
    # slash-containing Slurm field is not captured by the generic identifier regex.
    task_cpu=re.search(r'\bCPUs/Task=(\S+)',job_text)
    if task_cpu:job['CPUs/Task']=task_cpu[1]
    if config.get('slurm_qos'):expected['QOS']=config['slurm_qos']
    if any(not v or job.get(k)!=v for k,v in expected.items()):
        raise ValueError('Live Slurm job differs from reviewed account/resources: '+str(expected))
    if environment.get('SLURM_NTASKS')!=str(ranks) or environment.get('SLURM_JOB_NUM_NODES')!='1':
        raise ValueError('Slurm task/node environment differs')
    mem=re.search(r'\bMinMemoryNode=(\S+)',job_text)
    if not mem or mem[1] not in ('64G','65536M','65536'):
        raise ValueError('Expected scheduler request of 64 GiB per node')
    return job


def preflight(package, config):
    if sha(package/'file_hashes.json')!=config.get('package_hash_manifest_sha256'):
        raise ValueError('Pin hash-manifest SHA256 from reviewed release receipt')
    count=verify_package(package)
    if platform.system()!='Linux':raise ValueError('Linux required; no system installation attempted')
    if not config.get('allocation_confirmed') or not config.get('approval_reference'):
        raise ValueError('Actual allocation and approval must be recorded first')
    scheduler=None
    if config.get('runtime_mode') in ('param_shakti_slurm_v1','cse_slurm_v1'):
        jobid=os.environ.get('SLURM_JOB_ID','')
        if not re.fullmatch(r'\d+',jobid):raise ValueError('Compute allocation required; refuse login-node execution')
        text=subprocess.check_output(['scontrol','show','job','-o',jobid],text=True,timeout=15)
        scheduler=validate_slurm(config,os.environ,text)
    elif config.get('ranks')!=32 or config.get('threads')!=1:
        raise ValueError('Resource layout changed: revise package before adapting')
    if config.get('allocated_memory_GiB')!=64 or config.get('allocated_scratch_GiB')!=100:
        raise ValueError('Confirm registered memory/scratch allocation; revise before adapting')
    executable=Path(config['pw_executable']).resolve(strict=True)
    if sha(executable)!=config['pw_sha256'] or not os.access(executable,os.X_OK):
        raise ValueError('Executable hash/access mismatch')
    if not config.get('build_description') or not config.get('mpi_build_description'):
        raise ValueError('Build and MPI provenance required')
    mpi=config['mpi_argv']
    if not isinstance(mpi,list) or not mpi or any(not isinstance(x,str) or not x or '__' in x for x in mpi):
        raise ValueError('Explicit verified single-node MPI argv required, no shell string')
    launcher=Path(mpi[0]).resolve(strict=True)
    if sha(launcher)!=config['mpi_sha256']:raise ValueError('MPI launcher hash mismatch')
    if not config.get('single_node_launch_verified'):raise ValueError('Single-node launcher/binding unverified')
    affinity=os.sched_getaffinity(0)
    topology=subprocess.check_output(['lscpu','-p=CPU,CORE,SOCKET'],text=True)
    cores={tuple(line.split(',')[1:]) for line in topology.splitlines() if not line.startswith('#') and int(line.split(',')[0]) in affinity}
    if len(cores)<config['ranks']:raise ValueError('Fewer physical cores in affinity than registered ranks')
    scratch=Path(config['scratch_root']).resolve(strict=True)
    if shutil.disk_usage(scratch).free<100*2**30:raise ValueError('Insufficient free scratch for two retained jobs')
    if int(re.search(r'MemTotal:\s+(\d+)',Path('/proc/meminfo').read_text())[1])*1024<63*2**30:
        raise ValueError('Host has less memory than requested (allow OS reporting overhead)')
    if not config.get('external_memory_limit_verified') or not config.get('external_wall_limit_verified'):
        raise ValueError('Institution must verify hard memory/time enforcement; monitor alone is insufficient')
    if not config.get('scratch_retention_confirmed') or not config.get('evidence_retention_confirmed'):
        raise ValueError('Persistent evidence and failed/partial scratch retention must be confirmed')
    if not Path('/usr/bin/time').is_file():raise ValueError('GNU /usr/bin/time required for accounting')
    help_run=subprocess.run([str(executable),'-h'],capture_output=True,text=True,timeout=30)
    if help_run.returncode!=0 or not re.search(r'v\.7\.5\b',help_run.stdout+help_run.stderr):
        raise ValueError('pw.x help did not confirm QE 7.5')
    return {'verified_package_files':count,'pw_executable':str(executable),'pw_sha256':sha(executable),
            'pw_help':help_run.stdout+help_run.stderr,'physical_cores_in_affinity':len(cores),
            'lscpu':topology,'platform':platform.platform(),'hostname':platform.node(),
            'affinity_logical_CPU_ids':sorted(affinity),'config':config,'verified_slurm_job':scheduler,
            'scheduler_identifiers':{k:os.environ.get(k) for k in ('SLURM_JOB_ID','SLURM_JOB_NODELIST','PBS_JOBID','PBS_NODEFILE') if os.environ.get(k)},
            'mpi_library_links':subprocess.run(['ldd',str(executable)],capture_output=True,text=True).stdout,
            'meminfo':Path('/proc/meminfo').read_text(),'cgroup':Path('/proc/self/cgroup').read_text(),
            'scratch_free_bytes':shutil.disk_usage(scratch).free,'calculation_launched':False}


def execute(package, config, evidence, receipt, pilot_index=None):
    if not config.get('execute_approved'):raise ValueError('Execution approval remains false')
    plan=json.loads((package/'pilot_plan.json').read_text());manifest=json.loads((package/'manifest.json').read_text())
    if config.get('runtime_mode') in ('param_shakti_slurm_v1','cse_slurm_v1') and pilot_index not in (0,1):
        raise ValueError('Slurm revision runs exactly one frozen complex per four-hour job')
    selected=plan['pilot'] if pilot_index is None else [plan['pilot'][pilot_index]]
    if pilot_index==1:
        if not config.get('first_output_independently_reviewed'):
            raise ValueError('Independently inspect first real QE output before second job')
        predecessor=Path(config['first_evidence']).resolve()
        prior=verify_retained(predecessor,Path(config['first_scratch']))
        states=prior['states'];first=plan['pilot'][0]
        if len(states)!=1 or states[0].get('job')!=first or states[0].get('status')!='SCF_complete_pending_numerical_review':
            raise ValueError('First pilot job failed or incomplete')
    pseudo=json.loads((package/'pseudopotentials.json').read_text())
    start=time.monotonic();results={};states=[]
    evidence.mkdir(parents=True,exist_ok=False)
    dump(evidence/'preflight.json',receipt);dump(evidence/'configuration.json',config)
    scratch=Path(config['scratch_root'])/('uio66_qe_v2_'+evidence.name)
    scratch.mkdir(exist_ok=False)
    def interrupted(signum, frame):
        raise RuntimeError('External termination signal '+str(signum))
    signal.signal(signal.SIGTERM,interrupted)
    if hasattr(signal,'SIGUSR1'):signal.signal(signal.SIGUSR1,interrupted)
    env=os.environ.copy();env.update({'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
    for key in selected:
        spec=plan['inputs'][key];jobstart=time.monotonic()
        if jobstart-start>plan['whole_pilot_wall_seconds']-60:
            states.append({'job':key,'status':'not_started_whole_budget'});break
        work=evidence/key;work.mkdir();job_scratch=scratch/key;job_scratch.mkdir()
        (work/'scratch').symlink_to(job_scratch,target_is_directory=True)
        shutil.copytree(package/'pseudo',work/'pseudo')
        shutil.copyfile(package/spec['input'],work/'input.in')
        component=manifest['components'][spec['component']]
        geometry=json.loads((package/component['geometry_file']).read_text())
        pose=next(p for p in manifest['poses'] if p['id']==component['pose'])
        geometry['symbols']=pose['atom_symbols']
        command=['/usr/bin/time','-v','-o',str(work/'time.txt'),*config['mpi_argv'],config['pw_executable'],'-in','input.in']
        dump(work/'command.json',command)
        state={'job':key,'status':'running','command':command,'scratch':str(job_scratch),'sampled_peak_RSS_sum_bytes':0,'sampled_peak_scratch_bytes':0}
        dump(work/'state.json',state);proc=None
        try:
            with (work/'stdout.log').open('w') as out,(work/'stderr.log').open('w') as err,(work/'samples.jsonl').open('w') as samples:
                proc=subprocess.Popen(command,cwd=work,env=env,stdout=out,stderr=err,start_new_session=True)
                while proc.poll() is None:
                    elapsed=time.monotonic()-jobstart;rss=session_rss(proc.pid);disk=directory_bytes(scratch)
                    state['sampled_peak_RSS_sum_bytes']=max(rss,state['sampled_peak_RSS_sum_bytes'])
                    state['sampled_peak_scratch_bytes']=max(disk,state['sampled_peak_scratch_bytes'])
                    samples.write(json.dumps({'elapsed_s':elapsed,'RSS_sum_bytes':rss,'all_pilot_scratch_bytes':disk})+'\n');samples.flush()
                    if elapsed>=14370 or time.monotonic()-start>=28770 or rss>64*2**30 or disk>100*2**30 or shutil.disk_usage(scratch).free<2**30:
                        raise TimeoutError('Registered time, memory or scratch limit reached')
                    time.sleep(2)
            if proc.returncode!=0:raise ValueError('Nonzero process exit: '+str(proc.returncode))
            if time.monotonic()-jobstart>=14400 or time.monotonic()-start>=28800:
                raise TimeoutError('Completion beyond registered deadline is not accepted')
            xml=job_scratch/(spec['component']+'.save')/'data-file-schema.xml'
            shutil.copyfile(xml,work/'data-file-schema.xml')
            result=parse_result((work/'stdout.log').read_text(),xml,geometry,spec['electrons'],config['ranks'])
            result.update({'geometry_sha256':component['geometry_sha256'],
                'method_id':'QE7.5_PBE_D3BJ_2body_SSSP1.3.0precision_80_600_Gamma_1e-8Ry',
                'pseudopotential_hashes':{e:v['sha256'] for e,v in pseudo['potentials'].items()},
                'raw_output':str(work/'stdout.log'),'raw_output_sha256':sha(work/'stdout.log'),
                'raw_xml':str(work/'data-file-schema.xml'),'raw_xml_sha256':sha(work/'data-file-schema.xml')})
            results[spec['component']]=result;state['status']='SCF_complete_pending_numerical_review'
        except BaseException as exc:
            if proc is not None:stop_group(proc)
            state['status']='failed_or_incomplete';state['reason']=str(exc)
        finally:
            state['elapsed_seconds']=time.monotonic()-jobstart
            state['returncode']=proc.returncode if proc is not None else None
            dump(work/'state.json',state);states.append(state)
            dump(evidence/'records.json',results);dump(evidence/'states.json',states)
            # Manifest all partial/restart files in place. No cleanup or successful-only archive.
            dump(evidence/'scratch_hashes.json',{str(p.relative_to(scratch)):sha(p) for p in scratch.rglob('*') if p.is_file()})
            dump(evidence/'evidence_hashes.json',{str(p.relative_to(evidence)):sha(p) for p in evidence.rglob('*') if p.is_file() and p.name!='evidence_hashes.json' and 'scratch' not in p.relative_to(evidence).parts})
        if state['status']=='failed_or_incomplete':break
    dump(evidence/'retention.json',{'scratch_root':str(scratch),'keep_all':True,
        'copy_before_allocation_expires':'Copy entire evidence AND scratch trees, verify both hash manifests.',
        'not_started':[k for k in plan['pilot'] if k not in [s['job'] for s in states]],
        'two_complete':len(results)==2,'further_stage_authorized':False})
    dump(evidence/'evidence_hashes.json',{str(p.relative_to(evidence)):sha(p) for p in evidence.rglob('*') if p.is_file() and p.name!='evidence_hashes.json' and 'scratch' not in p.relative_to(evidence).parts})
    return len(results)==len(selected)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path)
    p.add_argument('--environment',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--verify-evidence',type=Path);p.add_argument('--scratch',type=Path)
    p.add_argument('--pilot-index',type=int,choices=(0,1))
    p.add_argument('--execute',action='store_true');args=p.parse_args()
    if args.verify_evidence:
        if not args.scratch or args.execute:p.error('Retention verification needs --scratch and cannot execute')
        print(json.dumps(verify_retained(args.verify_evidence,args.scratch),indent=2));raise SystemExit(0)
    if not all((args.package,args.environment,args.output)):p.error('Provide --package, --environment, --output')
    config=json.loads(args.environment.read_text());package=args.package.resolve();output=args.output.resolve()
    receipt=preflight(package,config)
    if args.execute:
        if not execute(package,config,output,receipt,args.pilot_index):raise SystemExit(1)
    else:
        if output.exists():raise FileExistsError('Preserve prior preflight')
        dump(output,receipt);print('Preflight complete. No SCF launched.')
