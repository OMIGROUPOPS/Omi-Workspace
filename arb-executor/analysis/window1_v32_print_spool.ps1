param(
    [Parameter(Mandatory=$true)][string]$Prints,
    [Parameter(Mandatory=$true)][string]$Sources,
    [Parameter(Mandatory=$true)][string]$Spool,
    [Parameter(Mandatory=$true)][string]$Receipt,
    [Parameter(Mandatory=$true)][string]$SourceCode
)
$ErrorActionPreference = "Stop"
Add-Type -LiteralPath $SourceCode
[Window1V32PrintSpool]::Run($Prints, $Sources, $Spool, $Receipt)
