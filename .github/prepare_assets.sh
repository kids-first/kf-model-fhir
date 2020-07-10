#!/usr/bin/env bash
set -euo pipefail

VERSION="$1"

pip install .
fhirutil validate --publisher_opts="-tx n/a" --clear_output site_root/ig.ini

# replace gh-pages root ig directory with site_root/output
git remote set-branches origin '*'
git fetch origin gh-pages
git checkout -f gh-pages
git rm -rf --ignore-unmatch ig
sudo mv -f site_root/output ig
sudo mkdir -p not_needed_for_ig_site
sudo mv ig/*.zip not_needed_for_ig_site
sudo mv ig/*.tgz not_needed_for_ig_site
sudo mv ig/*.pack not_needed_for_ig_site
git add ig
git config --global user.email "no_email"
git config --global user.name "gh_action_bot"
git commit -m "Update IG for release ${VERSION}"
if [ $? -ne 0 ]; then
    echo "nothing to commit"
    exit 0
fi
git push -fq "https://${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" gh-pages
