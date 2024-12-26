#!/bin/bash

operation="$1"
token="$2"

if [ $operation == "start" ]; then
  echo [INFO] Operation: $operation
  curl -X 'POST' https://b274c3f6-95b2-4e94-a872-7314dc5d95b9.webhook.eus.azure-automation.net/webhooks?token=$token -d '{"TAGKEY":"stop-non-working-hours","RESOURCEGROUP":"aks-cloudplatform-rg","OPERATION": "start"}' --insecure
fi

if [ $operation == "stop" ]; then
  echo [INFO] Operation: $operation
  curl -X 'POST' https://b274c3f6-95b2-4e94-a872-7314dc5d95b9.webhook.eus.azure-automation.net/webhooks?token=$token -d '{"TAGKEY":"stop-non-working-hours","RESOURCEGROUP":"aks-cloudplatform-rg","OPERATION": "stop"}' --insecure
fi

