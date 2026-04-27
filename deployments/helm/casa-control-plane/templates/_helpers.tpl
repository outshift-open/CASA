{{/*
Expand to "release-chart" (trimmed to 63 chars, no trailing dash).
*/}}
{{- define "casa-control-plane.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels applied to every resource.
*/}}
{{- define "casa-control-plane.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels — used in matchLabels / pod template labels.
Requires a "component" value passed via the caller's context.
Usage: {{ include "casa-control-plane.selectorLabels" (dict "Release" .Release "Chart" .Chart "component" "auth-service") }}
*/}}
{{- define "casa-control-plane.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
Internal service name for PostgreSQL backing the auth-service.
*/}}
{{- define "casa-control-plane.postgresAuthHost" -}}
{{- printf "%s-postgres-auth" .Release.Name }}
{{- end }}

{{/*
Internal service name for PostgreSQL backing Keycloak.
*/}}
{{- define "casa-control-plane.postgresKeycloakHost" -}}
{{- printf "%s-postgres-keycloak" .Release.Name }}
{{- end }}

{{/*
Internal Keycloak URL (used by auth-service as IDP_SERVER_URL).
*/}}
{{- define "casa-control-plane.keycloakUrl" -}}
{{- printf "http://%s-keycloak:%d/" .Release.Name (.Values.keycloak.service.port | int) }}
{{- end }}

{{/*
Internal auth-service URL (used by auth-service as AUTH_SERVER_URL and by the UI nginx proxy).
*/}}
{{- define "casa-control-plane.authServiceUrl" -}}
{{- printf "http://%s-auth-service:%d" .Release.Name (.Values.authService.service.port | int) }}
{{- end }}

{{/*
Effective Keycloak hostname for KC_HOSTNAME.
When keycloak.ingress.enabled is true, derived from "<domainPrefix>.<apiDomainName>".
Falls back to keycloak.hostname otherwise.
*/}}
{{- define "casa-control-plane.keycloakEffectiveHostname" -}}
{{- if and .Values.keycloak.ingress.enabled .Values.keycloak.ingress.apiDomainName }}
{{- printf "%s.%s" .Values.keycloak.ingress.domainPrefix .Values.keycloak.ingress.apiDomainName }}
{{- else }}
{{- .Values.keycloak.hostname }}
{{- end }}
{{- end }}
