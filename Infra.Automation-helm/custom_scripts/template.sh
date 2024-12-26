#!/bin/bash

# Check if an argument is provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <path_to_cloud_specific_file> <path_to_quickstart_sample_yaml_file>"
    exit 1
fi

variables_file="$1"
yaml_file="$2"

# Check if the files exist
if [ ! -f "$variables_file" ]; then
    echo "Error: File '$variables_file' not found."
    exit 1
fi

if [ ! -f "$yaml_file" ]; then
    echo "Error: File '$yaml_file' not found."
    exit 1
fi

# Source the variables file
source "$variables_file"

# Update the YAML file using sed
sed -i 's,{{env_pipe_domain_name}},'${domain_name}',' "$yaml_file"
sed -i 's,{{env_pipe_cluster_issuer_name}},'${clusterIssuerName}',' "$yaml_file"
sed -i 's,{{env_pipe_storage_class}},'${storage_class}',' "$yaml_file"
sed -i 's,{{env_pipe_dbaas_aggregator_registration_address}},'${dbaas_aggregator_registration_address}',' "$yaml_file"
sed -i 's,{{env_pipe_s3_minio}},'${s3_minio}',' "$yaml_file"
sed -i 's,{{env_pipe_s3_keyId}},'${s3_keyId}',' "$yaml_file"
sed -i 's,{{env_pipe_s3_keySecret}},'${s3_keySecret}',' "$yaml_file"
sed -i 's,{{env_pipe_public_cloud_name}},'${publicCloudName}',' "$yaml_file"
sed -i 's,{{env_pipe_tls_enabled}},'${tls_enabled}',' "$yaml_file"

echo "YAML file '$yaml_file' updated."
