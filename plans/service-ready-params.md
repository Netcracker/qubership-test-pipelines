# Анализ: вынос service_ready параметров в вызываемый workflow

## Текущая ситуация

Сейчас `service_ready_max_retries` и `service_ready_retry_interval` заданы **внутри** каждого reusable workflow (kafka.yaml, consul.yaml и т.д.) в секции `env:` для каждого job'а. Внешний caller workflow не может их контролировать.

## Варианты реализации

### Вариант 1: Два параметра во внешнем интерфейсе

Добавить в `workflow_call.inputs`:
```yaml
service_ready_timeout:
  description: "Максимальное время ожидания готовности сервиса (в минутах)"
  required: false
  type: number
  default: 20  # 20 минут
```

Внутри вычислять:
```yaml
env:
  service_ready_max_retries: ${{ (inputs.service_ready_timeout * 60) / 10 }}
  service_ready_retry_interval: 10s
```

**Плюсы:** Простой интерфейс для пользователя
**Минусы:** Нужно вычислять retries (целое число), сложнее для multi-phase сервисов

### Вариант 2: Один параметр — таймаут всего пайплайна

```yaml
pipeline_timeout_minutes:
  description: "Таймаут на весь тестовый пайплайн (в минутах)"
  required: false
  type: number
  default: 25
```

Внутри разбивать на фазы. Для Kafka (core + service install + upgrade):
- Если таймаут 25 минут:
  - install core: 30% = 7.5 мин → ~45 retries × 10s
  - install service: 25% = 6.25 мин → ~37 retries × 10s
  - upgrade core: 25% = 6.25 мин → ~37 retries × 10s
  - upgrade service: 20% = 5 мин → ~30 retries × 10s

**Плюсы:** Максимально просто для пользователя
**Минусы:** Сложная логика распределения, жесткие процентные соотношения

### Вариант 3: Параметр на фазу (рекомендуемый)

Для сервисов с одной фазой (install):
```yaml
service_ready_timeout:
  description: "Максимальное время ожидания (в минутах)"
  required: false
  type: number
  default: 20
```

Для Kafka (core + service):
```yaml
service_ready_timeout:
  description: "Максимальное время ожидания установки core-компонента (в минутах)"  
  required: false
  type: number
  default: 10
service_ready_service_timeout:
  description: "Максимальное время ожидания установки service-компонента (в минутах)"
  required: false
  type: number  
  default: 10
```

Внутри:
```yaml
env:
  kfk_max_attempts: ${{ (inputs.service_ready_timeout * 60) / 10 }}
  kfk_srvc_max_attempts: ${{ (inputs.service_ready_service_timeout * 60) / 10 }}
  kfk_timeout: "10s"
```

## Рекомендация

**Вариант 3** — оптимальный баланс простоты и гибкости. 

Для однофазных сервисов (consul, opensearch, rabbitmq, monitoring, pgskipper):
- один параметр `service_ready_timeout`

Для Kafka:
- `service_ready_timeout` — для kafka core
- `service_ready_service_timeout` — для kafka service (опционально, по умолчанию равен `service_ready_timeout`)

Для Zookeeper:
- `service_ready_timeout` — для install
- Если нужно отдельно для upgrade — `service_ready_upgrade_timeout`

### Пример для consul:

```yaml
# Вызывающий workflow (в репозитории consul)
jobs:
  Nightly-Consul-Pipeline:
    uses: Netcracker/qubership-test-pipelines/.github/workflows/consul.yaml@v1.8.0
    with:
      service_branch: main
      pipeline_branch: v1.8.0
      scope: nightly
      service_ready_timeout: 15  # макс 15 минут
    secrets:
      AWS_S3_ACCESS_KEY_ID: ${{ secrets.AWS_S3_ACCESS_KEY_ID }}
      AWS_S3_ACCESS_KEY_SECRET: ${{ secrets.AWS_S3_ACCESS_KEY_SECRET }}
```

### Внутри reusable workflow:

```yaml
on:
  workflow_call:
    inputs:
      service_ready_timeout:
        description: "Maximum time to wait for service readiness (in minutes)"
        required: false
        type: number
        default: 20
    # ... остальные inputs

env:
  TIMEOUT_SECONDS: ${{ inputs.service_ready_timeout * 60 }}
  RETRY_INTERVAL: 10

jobs:
  prepare:
    # ...
  
  Consul-Test-Cases:
    env:
      SERVICE_READY_MAX_RETRIES: ${{ env.TIMEOUT_SECONDS / env.RETRY_INTERVAL }}
      SERVICE_READY_RETRY_INTERVAL: ${{ env.RETRY_INTERVAL }}s
      TEST_COMPLETION_MAX_RETRIES: 1
      TEST_COMPLETION_RETRY_INTERVAL: 10s
```

Обратите внимание: `env` в GitHub Actions не поддерживает арифметику напрямую. Поэтому retries нужно вычислять через шаг:

```yaml
- name: Calculate retry parameters
  run: |
    TIMEOUT_SECONDS=$(( ${{ inputs.service_ready_timeout }} * 60 ))
    RETRY_INTERVAL=10
    echo "SERVICE_READY_MAX_RETRIES=$((TIMEOUT_SECONDS / RETRY_INTERVAL))" >> $GITHUB_ENV
    echo "SERVICE_READY_RETRY_INTERVAL=${RETRY_INTERVAL}s" >> $GITHUB_ENV
```

### Для Kafka:

```yaml
on:
  workflow_call:
    inputs:
      service_ready_timeout:
        description: "Max wait for Kafka core readiness (minutes)"
        required: false
        type: number
        default: 10
      service_ready_service_timeout:
        description: "Max wait for Kafka service readiness (minutes)"
        required: false
        type: number
        default: 10
```

И вычислить в prepare job:
```yaml
- name: Calculate timeout parameters
  run: |
    echo "kfk_max_attempts=$(( ${{ inputs.service_ready_timeout }} * 60 / 10 ))" >> $GITHUB_ENV
    echo "kfk_srvc_max_attempts=$(( ${{ inputs.service_ready_service_timeout }} * 60 / 10 ))" >> $GITHUB_ENV
    echo "kfk_timeout=10s" >> $GITHUB_ENV
    echo "kfk_srvc_timeout=10s" >> $GITHUB_ENV
```

Это позволит:
1. Внешним пользователям задавать только таймаут в минутах (интуитивно понятно)
2. Внутри вычислять retries с фиксированным интервалом 10s
3. Для multi-phase сервисов (kafka) разделять таймауты на компоненты
