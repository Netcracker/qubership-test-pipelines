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

## Workflows list

Added workflow for the following services:

- [Qubership Consul](https://github.com/Netcracker/qubership-consul)
- [Qubership ZooKeeper Service](https://github.com/Netcracker/qubership-zookeeper)
- [Qubership OpenSearch](https://github.com/Netcracker/qubership-opensearch)
- [Qubership Kafka Service](https://github.com/Netcracker/qubership-kafka)
- [Qubership RabbitMQ Service](https://github.com/Netcracker/qubership-rabbitmq)
- [Qubership PGgskipper Operator](https://github.com/Netcracker/pgskipper-operator)
- [Qubership Monitoring Operator](https://github.com/Netcracker/qubership-monitoring-operator)

## Pre-commit Hooks

It is recommended to install local pre-commit hooks. The same checks are run in GitHub Actions, and failing checks block merging changes.

Install and enable local hooks:

```bash
pip install pre-commit
pre-commit install
```

Run hooks for all files:

```bash
pre-commit run --all-files
```

## GitHub Actions: Pre-commit on MR (PR)

Pre-commit checks are configured in `.github/workflows/lint.yml`.

The workflow runs on:

- every `pull_request` to the `main` branch (MR equivalent in GitHub)
- every `push` to the `main` branch
