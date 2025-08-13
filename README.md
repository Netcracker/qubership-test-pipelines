# qubership-test-pipelines

This repository automates the end-to-end testing qubership services in a Kubernetes cluster using Kind. 
It implements a complete CI/CD lifecycle from infrastructure provisioning to post-deployment verification.

## Repository Structure
```
.github/
├── workflows/                              # Service-specific test workflows
├── actions/                                # Custom GitHub Actions
    ├── shared/                             # Shared actions for all services
        ├── create_cluster
        ├── create_restricted_resources
        ├── helm_deploy
        └── verify_installation
    └── [service]/
        └── helm_deploy_[service]/           # Reuse of shared actions with service specifics   
├── kind-configs/                            # Kind cluster configurations
├── python/                                  # Helper scripts
├── restricted/                              # Resources for restricted installation
└── templates/                               # Service configuration templates
    └── [service]/
        └── [config].yml
```
## Workflows list
Added workflow for the following services:
- [Consul](https://github.com/Netcracker/qubership-test-pipelines/blob/main/.github/workflows/consul.yaml)
- [Zookeeper](https://github.com/Netcracker/qubership-test-pipelines/blob/main/.github/workflows/zookeeper.yaml)
- [Opensearch](https://github.com/Netcracker/qubership-test-pipelines/blob/main/.github/workflows/opensearch.yaml)
