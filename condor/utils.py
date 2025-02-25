import os
import json
import subprocess
from pathlib import Path


def move_X509() -> str:
    """move x509 proxy file from /tmp to /afs/private. Returns the afs path"""
    try:
        x509_localpath = (
            [
                line
                for line in os.popen("voms-proxy-info").read().split("\n")
                if line.startswith("path")
            ][0]
            .split(":")[-1]
            .strip()
        )
    except Exception as err:
        raise RuntimeError(
            "x509 proxy could not be parsed, try creating it with 'voms-proxy-init --voms cms'"
        ) from err
    x509_path = f"{Path.home()}/private/{x509_localpath.split('/')[-1]}"
    subprocess.run(["cp", x509_localpath, x509_path])
    return x509_path


def get_command(args: dict) -> str:
    """return command to submit jobs at coffea-casa or lxplus"""
    cmd = f"python submit.py"
    for arg in args:
        if args[arg]:
            if arg in ["dataset", "nsample", "label"]:
                continue
            elif arg == "partition_fileset":
                partition_fileset = args["partition_fileset"]
                cmd += f" --partition_fileset '{json.dumps(partition_fileset)}' "
            elif arg in ["flow", "systematics"]:
                cmd += f" --{arg}"
            else:
                cmd += f" --{arg} {args[arg]}"
    return cmd


def get_jobpath(args: dict) -> str:
    path = args["processor"]
    path += f'/{args["label"]}'
    path += f'/{args["year"]}'
    path += f'/{args["dataset"]}'
    return path


def get_jobname(args: dict) -> str:
    jobname = args["processor"]
    jobname += f'_{args["dataset"]}'
    if "nsample" in args:
        jobname += f'_{args["nsample"]}'
    return jobname


def submit_condor(args: dict, submit: bool) -> None:
    """build condor and executable files, and submit condor job"""
    main_dir = Path.cwd()
    condor_dir = Path(f"{main_dir}/condor")

    # set path and jobname
    jobpath = get_jobpath(args)
    jobname = get_jobname(args)
    print(f"creating condor files {jobname}")

    # create logs and condor directories
    log_dir = Path(f"{str(condor_dir)}/logs/{jobpath}")
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
    local_condor_path = Path(f"{condor_dir}/{jobpath}/")
    if not local_condor_path.exists():
        local_condor_path.mkdir(parents=True)
    local_condor = f"{local_condor_path}/{jobname}.sub"

    # make condor file
    condor_template_file = open(f"{condor_dir}/submit.sub")
    condor_file = open(local_condor, "w")
    for line in condor_template_file:
        line = line.replace("DIRECTORY", str(condor_dir))
        line = line.replace("JOBPATH", jobpath)
        line = line.replace("JOBNAME", jobname)
        line = line.replace("PROCESSOR", args["processor"])
        line = line.replace("YEAR", args["year"])
        line = line.replace("JOBFLAVOR", f'"longlunch"')
        condor_file.write(line)
    condor_file.close()
    condor_template_file.close()

    # make executable file
    x509_path = move_X509()
    sh_template_file = open(f"{condor_dir}/submit.sh")
    local_sh = f"{local_condor_path}/{jobname}.sh"
    sh_file = open(local_sh, "w")
    for line in sh_template_file:
        line = line.replace("MAINDIRECTORY", str(main_dir))
        line = line.replace("COMMAND", get_command(args))
        line = line.replace("X509PATH", x509_path)
        sh_file.write(line)
    sh_file.close()
    sh_template_file.close()

    if submit:
        print(f"submitting condor job")
        subprocess.run(["condor_submit", local_condor])
