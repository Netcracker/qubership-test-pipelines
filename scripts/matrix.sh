#! /bin/bash
# This script generates a matrix for GitHub Actions based on a versions file and a workflow configuration file.
set -e
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <versions_file> <workflow_config> <service_branch>"
    exit 1
fi
export GITHUB_OUTPUT=${GITHUB_OUTPUT:-./github_output.txt}
export VERSIONS_FILE=$1
export WORKFLOW_CONFIG=$2
export service_branch=$3
sudo tee /etc/dpkg/dpkg.cfg.d/01_nodoc > /dev/null << 'EOF'
path-exclude /usr/share/doc/*
path-exclude /usr/share/man/*
path-exclude /usr/share/info/*
EOF
sudo apt install -y dos2unix
echo "::group::Process versions file"
versions_json=$(cat "$VERSIONS_FILE" | dos2unix | grep -v '^$' | jq -R -s -c 'split("\n")')
echo "versions=$versions_json" >> $GITHUB_OUTPUT
echo "versions=$versions_json"
export previous_version=$(echo "$versions_json" | jq -r '.[-1]')
echo "previous_version=$previous_version" >> $GITHUB_OUTPUT
echo "previous_version=$previous_version"
echo "::endgroup::"
echo "::group::Generate matrix from workflow-config"
# Remove automation jobs from the main matrix
matrix_json=$(yq -o=json "." "${WORKFLOW_CONFIG}" | jq -c '.jobs -= [ .jobs[] | select(.purpose == "automation") ]' | envsubst )
echo "===================================================="
echo "matrix_json=$matrix_json"
echo "===================================================="
# Extract automation part separately if exists
auto_matrix_json=$(yq -o=json "." "${WORKFLOW_CONFIG}" | jq -c '.jobs[] | select(.purpose == "automation")')
echo "===================================================="
echo "auto_matrix_json=$auto_matrix_json"
echo "===================================================="
# If automation part exists, generate section for each version from versions and append it to the main matrix
if [ -n "$auto_matrix_json" ]; then
    for version in $(echo "$versions_json" | jq -c -r '.[]'); do
        echo "Processing version: $version"
        export release_version=$version
        echo "===================================================="
        auto_part=$(echo "${auto_matrix_json}" | envsubst)
        echo "auto_part=${auto_part}"
        echo "===================================================="
        matrix_json=$(echo "$matrix_json" | jq -c --argjson new_job "$auto_part" '.jobs += [ $new_job ]')
    done
fi
matrix=$(echo ${matrix_json} | jq -c '.jobs')
echo "matrix=$matrix" >> $GITHUB_OUTPUT
echo "matrix=$matrix"
echo "::endgroup::"
