from argparse import ArgumentParser
from logging import getLogger, StreamHandler, DEBUG, ERROR
import os
import subprocess
from subprocess import PIPE
from typing import Set

logger = getLogger(__name__)


def get_remote_branches() -> Set[str]:
    proc = subprocess.run(
        "git branch -r", shell=True, stdout=PIPE, stderr=PIPE, text=True
    )
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
        proc = subprocess.run(
            f"git branch {remove_option} {branch}",
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
        )
        if proc.returncode != 0:
            # Occurs when unmerged branches are removed.
            logger.info(f"error: The branch '{branch}' is not fully merged.")
        else:
            logger.info("removed " + branch)


def get_option() -> None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "-ro",
        "--remove-option",
        type=str,
        choices=["-d", "-D"],
        dest="rm_opt",
        default="-d",
        help="Options for removing a branch. The default is '-d'.",
    )
    arg_parser.add_argument("-q", "--quiet", action="store_true", help="No output.")

    return arg_parser.parse_args()


def main():
    local_branch: Set[str] = get_local_branches()
    remote_branch: Set[str] = get_remote_branches()

    opt = get_option()

    # setting log level
    log_level = DEBUG
    if opt.quiet:
        log_level = ERROR

    handler = StreamHandler()
    handler.setLevel(log_level)
    logger.setLevel(log_level)
    logger.addHandler(handler)
    logger.propagate = False

    if not opt.quiet and opt.rm_opt == "-D":
        q = input(
            "Is it ok if the branches that have not been merged are also deleted? (y/n)[y] >"
        )
        # If only Enter is used, allow it.
        if q not in ["y", "Y", ""]:
            os.exit(0)
            
    remove_local_branches(local_branch - remote_branch, opt.rm_opt)


if __name__ == "__main__":
    main()
