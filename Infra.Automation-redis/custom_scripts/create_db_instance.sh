#!/bin/bash

curl -X 'PUT' 'https://aggregator-dbaas.qa-kubernetes.openshift.sdntest.qubership.org/api/v3/dbaas/redis/databases' -H 'accept: */*' -H 'Content-Type: application/json' -u cluster-dba:'' -d '{"classifier":{"microserviceName":"test-service10","namespace":"redis","scope":"service"},"type":"redis","originService":"test-service10"}' --insecure
