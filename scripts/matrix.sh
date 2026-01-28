#! /bin/bash
# This script generates a matrix for GitHub Actions based on latest tag and workflow configuration file.
set -e
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <latest_tag> <workflow_config> <service_branch>"
    exit 1
fi
export GITHUB_OUTPUT=${GITHUB_OUTPUT:-./github_output.txt}
export LATEST_TAG=$1
export WORKFLOW_CONFIG=$2
export service_branch=$3
sudo tee /etc/dpkg/dpkg.cfg.d/01_nodoc > /dev/null << 'EOF'
path-exclude /usr/share/doc/*
path-exclude /usr/share/man/*
path-exclude /usr/share/info/*
EOF
sudo apt install -y dos2unix

echo "::group::Generate matrix from workflow-config"
# Remove automation jobs from the main matrix
matrix_json=$(yq -o=json "." "${WORKFLOW_CONFIG}" | jq -c '.jobs -= [ .jobs[] | select(.purpose == "automation") ]' | envsubst )
echo "===================================================="
echo "matrix_json=$matrix_json"
echo "===================================================="
# Extract automation part separately if exists
auto_matrix_json=$(yq -o=json "." "${WORKFLOW_CONFIG}" | jq -c '.auto_jobs = [.jobs[] | select(.purpose == "automation")]' )
echo "===================================================="
echo "auto_matrix_json=$auto_matrix_json"
echo "===================================================="

# If automation part exists, generate section for the latest tag and append it to the main matrix
if [ -n "$auto_matrix_json" ]; then
    echo "Automation part exists"
    while IFS= read -r job; do
        echo "#######################################################################"
        echo "Automation job: $job"
        echo "#######################################################################"
        echo "Processing version: $LATEST_TAG"
        export release_version=$LATEST_TAG
        echo "===================================================="
        auto_part=$(echo "${job}" | envsubst)
        echo "auto_part=${auto_part}"
        echo "===================================================="
        matrix_json=$(echo "$matrix_json" | jq -c --argjson new_job "$auto_part" '.jobs += [ $new_job ]')
    done < <(echo "$auto_matrix_json" | jq -c '.auto_jobs[]')
fi
matrix=$(echo ${matrix_json} | jq -c '.jobs')
echo "matrix=$matrix" >> $GITHUB_OUTPUT
echo "matrix=$matrix"
echo "::endgroup::"
