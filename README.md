# qubership-test-pipelines

This repository automates the end-to-end testing qubership services in a Kubernetes cluster using Kind.
It implements a complete CI/CD lifecycle from infrastructure provisioning to post-deployment verification.

## Repository Structure
```
qubership-test-pipelines/
├── .github/                         # GitHub configurations and automation
│   ├── workflows/                   # Service-specific test workflows
│   └── actions/                     # Custom GitHub Actions
│       ├── shared/                  # Shared actions for all services
│       │   ├── create_cluster
│       │   ├── create_ingress
│       │   ├── create_restricted_resources
│       │   ├── get_certs
│       │   ├── get_crds
│       │   ├── helm_deploy
│       │   ├── verify_installation
|       |   └── collect_diag_info
│       └── [service-name]/          # Service-specific actions
├── docs/                            # Project documentation
├── kind-configs/                    # Kind cluster configurations
├── resources/                       # Additional resources
├── restricted/                      # Resources for restricted installation
├── scripts/                         # Helper scripts
├── templates/                       # Service configuration templates
│   └── [service-name]/
│       └── [config-name].yml
└── workflow-config/                 # Workflow configurations
```
## Development

### Pre-commit hooks

This repository uses [pre-commit](https://pre-commit.com/) to enforce code quality.

#### Installation

```bash
pip install pre-commit
pre-commit install
```

#### Run against all files

```bash
pre-commit run --all-files
```

## Workflows list
Added workflow for the following services:
- [Qubership Consul](https://github.com/Netcracker/qubership-consul)
- [Qubership ZooKeeper Service](https://github.com/Netcracker/qubership-zookeeper)
- [Qubership OpenSearch](https://github.com/Netcracker/qubership-opensearch)
- [Qubership Kafka Service](https://github.com/Netcracker/qubership-kafka)
- [Qubership RabbitMQ Service](https://github.com/Netcracker/qubership-rabbitmq)
- [Qubership PGgskipper Operator](https://github.com/Netcracker/pgskipper-operator)
- [Qubership Monitoring Operator](https://github.com/Netcracker/qubership-monitoring-operator)
