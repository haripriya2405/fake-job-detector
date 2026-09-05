# ==============================================================================
# SentinelJob AI — PostgreSQL Automated Database Backup Script (PowerShell)
# ==============================================================================
param (
    [string]$BackupDir = "./backups",
    [string]$ContainerName = "sentineljob-postgres",
    [string]$DbName = "fake_job_detector",
    [string]$DbUser = "postgres"
)

$ErrorActionPreference = "Stop"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupDir "${DbName}_backup_${Timestamp}.sql"

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host "[INFO] Starting database backup for '$DbName'..."

if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker exec -t $ContainerName pg_dump -U $DbUser -d $DbName --clean --if-exists --no-owner | Out-File -Encoding utf8 $BackupFile
} else {
    pg_dump -U $DbUser -d $DbName --clean --if-exists --no-owner | Out-File -Encoding utf8 $BackupFile
}

if ((Test-Path $BackupFile) -and ((Get-Item $BackupFile).Length -gt 0)) {
    $SizeKB = [math]::Round(((Get-Item $BackupFile).Length / 1KB), 2)
    Write-Host "[SUCCESS] Backup completed: $BackupFile ($SizeKB KB)"
} else {
    Write-Error "[ERROR] Backup failed or file is empty."
}
