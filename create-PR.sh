#!/bin/bash
set -e

# Check if a file name was provided
if [ -z "$1" ]; then
    echo "Error: No file name provided."
    echo "Usage: $0 <file_path>"
    exit 1
fi

# Variables
file_path="$1"
file_name=$(basename "$file_path")
branch_name="create-page-$file_name"
PR_title="Create page $file_name in torus"

git config --global user.name "QBL bot"
git config --global user.email "qblbot@example.com"

git pull
git checkout -b $branch_name
git add $file_path
git commit -m "Create $file_name"
git push -u origin $branch_name
gh pr create --title $PR_title --body ""

echo "Pull request successfully created with title: $PR_title"

git checkout main