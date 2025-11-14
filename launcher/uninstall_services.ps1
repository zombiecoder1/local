<#
Uninstall the SimpleCursor Windows services created by install_services.ps1
Run as Administrator.
#>

$ErrorActionPreference = 'Stop'
Write-Output "[uninstall-services] Stopping and removing services..."

foreach ($name in @('SimpleCursorProxy','SimpleCursorShim')) {
    try {
        sc.exe stop $name | Out-Null
    } catch {}
    Start-Sleep -Milliseconds 500
    try {
        sc.exe delete $name | Out-Null
        Write-Output "[uninstall-services] Deleted $name"
    } catch {
        $msg = $_.Exception.Message
        Write-Output "[uninstall-services] Could not delete $name: $msg"
    }
}

Write-Output "[uninstall-services] Done."
