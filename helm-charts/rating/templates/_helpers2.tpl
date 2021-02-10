{{/* vim: set filetype=mustache: */}}

{{/*
Names for the pods and other stuff.
Truncating to 63 here is messy. If names are too long, consider fullnameOverride.
*/}}

{{- define "rating.operator.api.fullname" -}}
{{ template "rating.fullname" . }}-{{ .Values.api.name }}
{{- end -}}

{{- define "rating.operator.manager.fullname" -}}
{{ template "rating.fullname" . }}-{{ .Values.manager.name }}
{{- end -}}

{{- define "rating.operator.engine.fullname" -}}
{{ template "rating.fullname" . }}-{{ .Values.engine.name }}
{{- end -}}

{{/*
Names for the pull secrets.
*/}}

{{- define "rating.operator.api.pullSecretName" -}}
{{ template "rating.fullname" . }}-{{ .Values.api.name }}-pull
{{- end -}}

{{- define "rating.operator.engine.pullSecretName" -}}
{{ template "rating.fullname" . }}-{{ .Values.engine.name }}-pull
{{- end -}}