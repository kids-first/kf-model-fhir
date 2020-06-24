#!/usr/bin/env bash
set -euo pipefail

VERSION="$1"

pip install .
fhirutil validate --publisher_opts="-tx n/a" --clear_output site_root/ig.ini

# replace gh-pages root ig directory with site_root/output
git checkout gh-pages
git rm -rf --ignore-unmatch ig
mv -f site_root/output ig
mkdir -p not_needed_for_ig_site
mv ig/*.zip not_needed_for_ig_site
mv ig/*.tgz not_needed_for_ig_site
mv ig/*.pack not_needed_for_ig_site
git add ig
git commit -m "Update IG for release ${VERSION}"
if [ $? -ne 0 ]; then
    echo "nothing to commit"
    exit 0
fi
git push -fq "https://${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" gh-pages
