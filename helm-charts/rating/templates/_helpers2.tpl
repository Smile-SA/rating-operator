{{/* vim: set filetype=mustache: */}}

{{/*
Names for the pods and other stuff.
Truncating to 63 here is messy. If names are too long, consider fullnameOverride.
*/}}

{{- define "rating.api.fullname" -}}
{{ template "rating.fullname" . }}-{{ .Values.api.name }}
{{- end -}}

{{- define "rating.frontend.fullname" -}}
{{ template "rating.fullname" . }}-{{ .Values.frontend.name }}
{{- end -}}

{{- define "rating.processor.fullname" -}}
{{ template "rating.fullname" . }}-{{ .Values.processor.name }}
{{- end -}}

{{/*
Names for the pull secrets.
*/}}

{{- define "rating.api.pullSecretName" -}}
{{ template "rating.fullname" . }}-{{ .Values.api.name }}-pull
{{- end -}}

{{- define "rating.frontend.pullSecretName" -}}
{{ template "rating.fullname" . }}-{{ .Values.frontend.name }}-pull
{{- end -}}

{{- define "rating.processor.pullSecretName" -}}
{{ template "rating.fullname" . }}-{{ .Values.processor.name }}-pull
{{- end -}}


