#!/usr/bin/env bash

set -Eeuo pipefail
IFS=$'\n\t'

ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../.env"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Arquivo .env não encontrado: $ENV_FILE"
    exit 1
fi

set -a
source "$ENV_FILE"
set +a

required_vars=(DB_DATABASE DB_USERNAME DB_PASSWORD DB_HOST DB_PORT)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "Variável obrigatória não definida: $var"
    exit 1
  fi
done

readonly BACKUP_ROOT="/var/backups/postgresql"
readonly RETENTION_DAYS=7
readonly LOCK_FILE="/var/run/pg_backup.lock"

readonly TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
readonly BACKUP_FILE="${BACKUP_ROOT}/${DB_DATABASE}_${TIMESTAMP}.dump"
readonly LOG_FILE="${BACKUP_ROOT}/backup.log"

export PGPASSWORD=$DB_PASSWORD

log() {
    local level="$1"
    local message="$2"
    printf "[%s] [%s] %s\n" "$(date +'%Y-%m-%d %H:%M:%S')" "$level" "$message" | tee -a "$LOG_FILE"
}

error_handler() {
    local exit_code=$?
    log "ERROR" "Erro inesperado na linha ${BASH_LINENO[0]} (exit code: ${exit_code})"
    exit "$exit_code"
}

cleanup() {
    rm -f "$LOCK_FILE"
}

check_dependencies() {
    local deps=("pg_dump" "find" "flock")
    for cmd in "${deps[@]}"; do
        command -v "$cmd" >/dev/null 2>&1 || {
            log "ERROR" "Dependência ausente: $cmd"
            exit 1
        }
    done
}

create_backup_dir() {
    mkdir -p "$BACKUP_ROOT"
    chmod 700 "$BACKUP_ROOT"
}

perform_backup() {
    log "INFO" "Iniciando backup do banco ${DB_DATABASE}"

    pg_dump \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        --username="$DB_USERNAME" \
        --dbname="$DB_DATABASE" \
        --format=custom \
        --compress=9 \
        --no-owner \
        --no-privileges \
        --file="$BACKUP_FILE"

    chmod 600 "$BACKUP_FILE"

    log "INFO" "Backup concluído com sucesso: $BACKUP_FILE"
}

cleanup_old_backups() {
    log "INFO" "Removendo backups com mais de ${RETENTION_DAYS} dias"

    find "$BACKUP_ROOT" \
        -type f \
        -name "${DB_DATABASE}_*.dump" \
        -mtime +"$RETENTION_DAYS" \
        -print -delete >>"$LOG_FILE" 2>&1 || true
}

trap error_handler ERR
trap cleanup EXIT

exec 200>"$LOCK_FILE"
flock -n 200 || {
    log "WARN" "Outro processo de backup já está em execução."
    exit 1
}

check_dependencies
create_backup_dir
perform_backup
cleanup_old_backups

log "INFO" "Rotina finalizada com sucesso."
