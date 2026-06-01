param(
  [string]$JenkinsUrl = 'http://localhost:8080/',
  [string]$CliJar = 'C:\Users\admin\Downloads\jenkins-cli (1).jar',
  [string]$Auth = 'pluto:1130efd5ebc387d250de34966042dbce90'
)

function Normalize-JenkinsUrl {
  param([string]$Url)
  return $Url.TrimEnd('/')
}

function Get-JenkinsAuthHeaders {
  $parts = $Auth.Split(':', 2)
  $token = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("$($parts[0]):$($parts[1])"))
  return @{ Authorization = "Basic $token" }
}

function Get-JenkinsCrumb {
  param([string]$Url)
  $baseUrl = Normalize-JenkinsUrl $Url
  $crumbUrl = "$baseUrl/crumbIssuer/api/json"
  try {
    $headers = Get-JenkinsAuthHeaders
    $response = Invoke-RestMethod -Uri $crumbUrl -Headers $headers -UseBasicParsing -ErrorAction Stop
    return $response
  } catch {
    Write-Host "Failed to get crumb from $crumbUrl. Jenkins may already allow anonymous POST or auth is incorrect." -ForegroundColor Yellow
    return $null
  }
}

function Invoke-JenkinsRest {
  param(
    [string]$Method,
    [string]$Uri,
    $Body = $null,
    $Headers = $null,
    [string]$ContentType = $null
  )
  $headers = @{ }
  $authHeader = Get-JenkinsAuthHeaders
  foreach ($key in $authHeader.Keys) { $headers[$key] = $authHeader[$key] }
  if ($Headers) {
    foreach ($pair in $Headers.GetEnumerator()) { $headers[$pair.Key] = $pair.Value }
  }

  $params = @{
    Method = $Method
    Uri = $Uri
    Headers = $headers
    UseBasicParsing = $true
    ErrorAction = 'Stop'
  }
  if ($Body) { $params.Body = $Body }
  if ($ContentType) { $params.ContentType = $ContentType }
  return Invoke-RestMethod @params
}

function Test-JobExists {
  param([string]$JobName)
  try {
    Invoke-JenkinsRest -Method Get -Uri "$JenkinsUrl/job/$JobName/api/json" | Out-Null
    return $true
  } catch {
    return $false
  }
}

function Create-JobIfMissing {
  param([string]$JobName, [string]$JobXmlPath)
  if (-not (Test-JobExists -JobName $JobName)) {
    Write-Host "Creating Jenkins job $JobName..."
    $baseUrl = Normalize-JenkinsUrl $JenkinsUrl
    $headers = @{ }
    $crumb = Get-JenkinsCrumb -Url $JenkinsUrl
    if ($crumb) { $headers[$crumb.crumbRequestField] = $crumb.crumb }
    $xmlBody = Get-Content -Path $JobXmlPath -Raw
    try {
      Invoke-JenkinsRest -Method Post -Uri "$baseUrl/createItem?name=$JobName" -Headers $headers -Body $xmlBody -ContentType 'application/xml'
      Write-Host "Created Jenkins job $JobName."
    } catch {
      Write-Host ('Failed to create job {0}: ' -f $JobName) -NoNewline
      Write-Host $_ -ForegroundColor Red
      throw
    }
  } else {
    Write-Host "Job $JobName already exists."
  }
}

function Trigger-Build {
  param([string]$JobName)
  $baseUrl = Normalize-JenkinsUrl $JenkinsUrl
  $headers = @{ }
  $crumb = Get-JenkinsCrumb -Url $JenkinsUrl
  if ($crumb) { $headers[$crumb.crumbRequestField] = $crumb.crumb }
  $jobInfo = Invoke-JenkinsRest -Method Get -Uri "$baseUrl/job/$JobName/api/json" -Headers $headers
  $buildNumber = $jobInfo.nextBuildNumber
  Write-Host "Starting build #$buildNumber for job $JobName..."
  Invoke-JenkinsRest -Method Post -Uri "$baseUrl/job/$JobName/build" -Headers $headers
  return $buildNumber
}

function Watch-Build {
  param([string]$JobName, [int]$BuildNumber)
  $baseUrl = Normalize-JenkinsUrl $JenkinsUrl
  $statusUri = "$baseUrl/job/$JobName/$BuildNumber/api/json"
  $headers = @{ }
  $crumb = Get-JenkinsCrumb -Url $JenkinsUrl
  if ($crumb) { $headers[$crumb.crumbRequestField] = $crumb.crumb }
  Write-Host "Watching build #$BuildNumber for job $JobName..."

  while ($true) {
    try {
      $buildInfo = Invoke-JenkinsRest -Method Get -Uri $statusUri -Headers $headers
      $building = $buildInfo.building
      $result = $buildInfo.result
    } catch {
      Write-Host "Waiting for build details to appear..." -ForegroundColor Yellow
      Start-Sleep -Seconds 5
      continue
    }

    Write-Host "Build status: building=$building, result=$result"

    if ($building -eq $false -and $result) {
      Write-Host "Build completed with result: $result" -ForegroundColor Cyan
      $consoleUri = "$baseUrl/job/$JobName/$BuildNumber/consoleText"
      Write-Host "Fetching final console output..."
      Invoke-JenkinsRest -Method Get -Uri $consoleUri | Write-Output
      return $result
    }

    Start-Sleep -Seconds 10
  }
}

$jobs = @(
  @{ Name = 'carml-full-pipeline'; Xml = 'jenkins-job-carml-full.xml' },
  @{ Name = 'carml-no-docker-push'; Xml = 'jenkins-job-carml-no-docker-push.xml' }
)

foreach ($job in $jobs) {
  $xmlPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) $job.Xml
  if (-not (Test-Path $xmlPath)) {
    Write-Error "Job XML not found: $xmlPath"
    exit 1
  }
  Create-JobIfMissing -JobName $job.Name -JobXmlPath $xmlPath
  $buildNumber = Trigger-Build -JobName $job.Name
  $result = Watch-Build -JobName $job.Name -BuildNumber $buildNumber
  Write-Host "Job $($job.Name) finished with result $result" -ForegroundColor Green
}
