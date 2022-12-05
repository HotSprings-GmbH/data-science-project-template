#! /bin/bash

# exit on non-zero return value
set -e

# helper function for command line argument(s)
argument_helper()
{
  echo ""
  echo "Usage: ${0} -c commit_branch -m main_branch"
  echo -e "\t-c Name of the branch with the new commits to be included (e.g., 1-new-feature)."
  echo -e "\t-m Name of the branch onto which the branch will be merged (e.g., remotes/origin/main). Used to get a list of new commits."
  exit 1
}

# read command line argument(s)
while getopts "c:m:" opt
do
  case "${opt}" in
    c ) commit_branch="${OPTARG}" ;;
    m ) main_branch="${OPTARG}" ;;
    ? ) argument_helper ;;
  esac
done

# print helpFunction in case one of the parameter(s) is/are empty
if [ -z "${commit_branch}" ] || [ -z "${main_branch}" ]
then
  echo "Not all required parameters have been set or are empty."
  argument_helper
fi

# verify that the branch names are not identical
if [ "${commit_branch}" == "${main_branch}" ]
then
  echo "commit_branch: ${commit_branch}"
  echo "main_branch: ${main_branch}"
  echo "The branch names are identical. Will not check any messages."
  exit 0
fi

# create list of commit messages to check
echo "Getting new commits from ${commit_branch} w.r.t. ${main_branch}"
merge_base=$(git merge-base ${commit_branch} ${main_branch})
rev_list=$(git rev-list --ancestry-path ${merge_base}..${commit_branch})

# check commit messages
if [ -n "${rev_list}" ]
then
  if [ -f ".tmp_commit_msg_storage" ]
  then
    echo "ERROR: .tmp_commit_msg_storage already exists and would be overwritten."
    exit 1
  fi
  # loop over commits to check
  for commit_hash in ${rev_list}
  do
    # read the commit message and store it in a temporary file
    git log --format=%B --max-count=1 ${commit_hash} > .tmp_commit_msg_storage
    echo "Now analyzing commit message of ${commit_hash}:"
    echo "-----------"
    cat .tmp_commit_msg_storage
    echo "-----------"
    # run pre-commit hook for commit message
    pre-commit run --hook-stage commit-msg --commit-msg-filename ".tmp_commit_msg_storage"
  done
  rm .tmp_commit_msg_storage
else
  # no commits to check
  echo "Did not find any commits to check..."
fi
echo "Sucessfully finished checking commit messages."
