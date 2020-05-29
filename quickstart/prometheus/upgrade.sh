#!/bin/sh

helm upgrade --install prometheus --values ./values.yaml --namespace monitoring stable/prometheus-operator

