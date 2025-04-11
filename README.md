# qubership-test-pipelines

This repository automates the end-to-end testing Netcracker services in a Kubernetes cluster using Kind. 
It implements a complete CI/CD lifecycle from infrastructure provisioning to post-deployment verification.

- [Repository Structure](#repository-structure)
- [Consul](#consul)

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
## Job Structure Overview

Step 1: Cluster Creation 
Step 2: Monitoring Installation (for alert tests)
Step 3: Service clean installation
Step 4: Validation (logs, events, tests)
Step 5: Service upgrade
Step 6: Validation


## Consul

### Jobs list
....

