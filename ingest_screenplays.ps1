$sourceDir = "C:\Users\navka\navakanth001\raw_screenplays"
$targetDir = "C:\Users\navka\navakanth001\memory_os\long_term_knowledge"

# Create target dir if it doesn't exist
if (!(Test-Path -Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir
}

# Max size 50MB (52428800 bytes)
$maxSize = 52428800

$files = Get-ChildItem -Path $sourceDir -Filter *.pdf
foreach ($file in $files) {
    if ($file.Length -gt $maxSize) {
        Write-Host "Skipping $($file.Name) because it exceeds 50MB limit."
        continue
    }

    $targetFile = Join-Path -Path $targetDir -ChildPath "$($file.BaseName).md"
    if (Test-Path -Path $targetFile) {
        Write-Host "Skipping $($file.Name) because it's already parsed."
        continue
    }

    Write-Host "Parsing $($file.Name)..."
    npx firecrawl parse "$($file.FullName)" -o "$targetFile"
}
Write-Host "Ingestion complete."
