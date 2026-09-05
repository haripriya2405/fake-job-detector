# ==============================================================================
# SentinelJob AI — PostgreSQL Automated Database Restore Script (PowerShell)
# ==============================================================================
param (
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    [string]$ContainerName = "sentineljob-postgres",
    [string]$DbName = "fake_job_detector",
    [string]$DbUser = "postgres"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupFile)) {
    Write-Error "[ERROR] Backup file not found: $BackupFile"
    exit 1
}

Write-Host "[INFO] Restoring database '$DbName' from $BackupFile..."

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Get-Content $BackupFile | docker exec -i $ContainerName psql -U $DbUser -d $DbName
} else {
    Get-Content $BackupFile | psql -U $DbUser -d $DbName
}

Write-Host "[SUCCESS] Database restoration completed."
