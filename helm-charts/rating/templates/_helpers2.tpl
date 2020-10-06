{{/* vim: set filetype=mustache: */}}

{{/*
Names for the pods and other stuff.
Truncating to 63 here is messy. If names are too long, consider fullnameOverride.
*/}}

{{- define "rating.api.fullname" -}}
{{ template "rating.fullname" . }}-{{ .Values.api.name }}
{{- end -}}

{{- define "rating.processing.fullname" -}}
{{ template "rating.fullname" . }}-{{ .Values.processing.name }}
{{- end -}}

{{- define "reactive.operator.fullname" -}}
{{ template "rating.fullname" . }}-{{ .Values.reactive.name }}
{{- end -}}

{{- define "rating.frontend.fullname" -}}
{{ template "rating.fullname" . }}-{{ .Values.frontend.name }}
{{- end -}}

{{/*
Names for the pull secrets.
*/}}

{{- define "rating.api.pullSecretName" -}}
{{ template "rating.fullname" . }}-{{ .Values.api.name }}-pull
{{- end -}}

{{- define "reactive.operator.pullSecretName" -}}
{{ template "rating.fullname" . }}-{{ .Values.reactive.name }}-pull
{{- end -}}

{{- define "rating.frontend.pullSecretName" -}}
{{ template "rating.fullname" . }}-{{ .Values.frontend.name }}-pull
{{- end -}}