from logging import getLogger, StreamHandler, DEBUG
import os
import subprocess
from subprocess import PIPE
from typing import Set

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False


def get_remote_branches() -> Set[str]:
    proc = subprocess.run("git branch -r", shell=True, stdout=PIPE, stderr=PIPE, text=True)
    branch_list = proc.stdout.strip("*").split()
    
    # The name of the retrieved branch contains "origin/", so remove it.
    formatted_branch_list = [branch.lstrip("origin/") for branch in branch_list]

    return set(formatted_branch_list)


def get_local_branches() -> Set[str]:
    proc = subprocess.run("git branch", shell=True, stdout=PIPE, stderr=PIPE, text=True)
    branch_list = proc.stdout.strip("*").split()

    return set(branch_list)


def remove_local_branches(branches: Set[str], remove_option="-d") -> None:
    for branch in branches:
        proc = subprocess.run(f"git branch {remove_option} {branch}", shell=True, stdout=PIPE, stderr=PIPE, text=True)
        if proc.returncode != 0:
            # Occurs when unmerged branches are removed.
            logger.info(f"error: The branch '{branch}' is not fully merged.")
        else:
            logger.info("removed " + branch)


def main():
    local_branch: Set[str] = get_local_branches()
    remote_branch: Set[str] = get_remote_branches()
    
    remove_local_branches(local_branch - remote_branch)



if __name__ == "__main__":
    main()
