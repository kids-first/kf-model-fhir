#! /bin/bash

set -eo pipefail

echo "*********** START $(basename $0) script ***********"

publisher_opts="${@:2}"
default_ig_control_file="$(pwd)/site_root/ig.json"
ig_control_file="$default_ig_control_file"

# Check if user specified a location for ig control file
if [[ -z $1 ]]; then
    echo "Using default control file for implementation guide: $ig_control_file"
else
    ig_control_file="$1"
    echo "Using user specified control file for implementation guide: $ig_control_file"
fi
echo "Using publisher cmd options: $publisher_opts"

# Check if ig control file exists
if [ ! -f "$ig_control_file" ]; then
    echo "The IG control file '$ig_control_file' does not exist. Please create one" \
         "at the preferred location: $default_ig_control_file"
    exit 1
fi

# Run ig-publisher in a docker container
ig_site_dir=$(dirname "$ig_control_file")
ig_control_file=$(basename "$ig_control_file")
docker run --rm -v "$ig_site_dir":/data -v "$HOME/.fhir/packages":/root/.fhir/packages \
kidsfirstdrc/fhir-ig-publisher:latest -ig "/data/$ig_control_file" $publisher_opts

echo "*********** END $(basename $0) script ***********"
