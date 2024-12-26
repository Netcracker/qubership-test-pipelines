#!/bin/bash

curl -u cluster-dba:'' -X 'DELETE' 'https://aggregator-dbaas.platcert01.kubernetes.sdntest.qubership.org/api/v3/dbaas/airflow-helm/databases/postgresql' -H 'accept: */*' -H 'Content-Type: application/json' -d '{"classifier": {"scope": "service", "namespace": "airflow-helm", "isServiceDb": "true", "microserviceName": "airflow"},"originService": "airflow"}' --insecure
curl -u cluster-dba:'' -X 'DELETE' 'https://aggregator-dbaas.platcert01.kubernetes.sdntest.qubership.org/api/v3/dbaas/airflow-helm/databases/redis' -H 'accept: */*' -H 'Content-Type: application/json' -d '{"classifier": {"scope": "service", "namespace": "airflow-helm", "isServiceDb": "true", "microserviceName": "airflowdbaas"},"originService": "airflowdbaas"}' --insecure
