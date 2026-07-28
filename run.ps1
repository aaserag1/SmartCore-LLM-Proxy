$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $projectRoot

try {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    $pythonArguments = @()

    if (-not $pythonCommand) {
        $launcher = Join-Path $env:LocalAppData "Programs\Python\Launcher\py.exe"
        if (-not (Test-Path -LiteralPath $launcher)) {
            throw "Python 3.10 or newer was not found."
        }
        $pythonCommand = $launcher
        $pythonArguments = @("-3")
    }

    & $pythonCommand @pythonArguments scripts/start_proxy.py @args
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
