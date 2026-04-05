#!/usr/bin/env pwsh
# Create feature branches from main, each with complete files
$ErrorActionPreference = "Stop"

$origBranch = (git branch --show-current)
git checkout main -q

function create_branch($name, $files) {
    Write-Host "`n=== $name ===" -ForegroundColor Green
    git checkout main -b $name 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { git checkout main -b $name -f 2>$null | Out-Null }
    
    $addedFiles = @()
    foreach ($file in $files) {
        if (Test-Path $file) {
            git add $file
            $addedFiles += $file
            Write-Host "  + $file"
        }
    }
    
    if ($addedFiles.Count -gt 0) {
        $slug = ($name -replace 'feat/', '' -replace '[-]', ' ')
        git commit -m "feat: add $slug" -q
        git push -u origin $name --force -q 2>$null
        Write-Host "  -> pushed" -ForegroundColor Cyan
    } else {
        Write-Host "  -> no files to commit" -ForegroundColor Yellow
        git checkout main -q
        return
    }
    
    git checkout main -q
}

function cleanup($name) {
    git branch -D $name 2>$null | Out-Null
    git push origin --delete $name 2>$null | Out-Null
}

# Server branches
cleanup("feat/server-transforms"); create_branch "feat/server-transforms" @("server/app/transforms.py")
cleanup("feat/server-models"); create_branch "feat/server-models" @("server/app/models.py")
cleanup("feat/server-faiss"); create_branch "feat/server-faiss" @("server/app/faiss_index.py")
cleanup("feat/server-faiss-build"); create_branch "feat/server-faiss-build" @("server/build_faiss.py")
cleanup("feat/server-requirements"); create_branch "feat/server-requirements" @("server/requirements.txt")
cleanup("feat/server-policy"); create_branch "feat/server-policy" @("server/app/policy.py")
cleanup("feat/server-main"); create_branch "feat/server-main" @("server/main.py")

# Test branches
cleanup("feat/tests-fixtures"); create_branch "feat/tests-fixtures" @("tests/fixtures/__init__.py","tests/fixtures/applicants.py","tests/fixtures/endpoints.py")
cleanup("feat/tests-validators"); create_branch "feat/tests-validators" @("tests/validators/__init__.py","tests/validators/explanation_validator.py","tests/validators/human_explanation.py")
cleanup("feat/tests-endpoints-validation"); create_branch "feat/tests-endpoints-validation" @("tests/test_endpoints_validation.py")
cleanup("feat/tests-human-explanations"); create_branch "feat/tests-human-explanations" @("tests/test_human_explanations.py")

# Client branches
cleanup("feat/client-api"); create_branch "feat/client-api" @("client/src/lib/api.ts")
cleanup("feat/client-types"); create_branch "feat/client-types" @("client/src/lib/types.ts")
cleanup("feat/client-landing"); create_branch "feat/client-landing" @("client/src/app/page.tsx","client/src/components/landing/landing-components.tsx")
cleanup("feat/client-dashboard-page"); create_branch "feat/client-dashboard-page" @("client/src/app/dashboard/page.tsx")
cleanup("feat/client-dashboard-header"); create_branch "feat/client-dashboard-header" @("client/src/components/dashboard/dashboard-header.tsx")
cleanup("feat/client-dashboard-input-form"); create_branch "feat/client-dashboard-input-form" @("client/src/components/dashboard/input-form.tsx")
cleanup("feat/client-dashboard-results"); create_branch "feat/client-dashboard-results" @("client/src/components/dashboard/results.tsx")
cleanup("feat/client-docs-page"); create_branch "feat/client-docs-page" @("client/src/app/docs/page.tsx")
cleanup("feat/client-docs-content"); create_branch "feat/client-docs-content" @("client/src/components/docs/docs-content.tsx")
cleanup("feat/client-styles"); create_branch "feat/client-styles" @("client/src/app/globals.css")
cleanup("feat/client-layout"); create_branch "feat/client-layout" @("client/src/app/layout.tsx")

# Config branches
cleanup("feat/gitignore"); create_branch "feat/gitignore" @(".gitignore")

# Return to original branch
git checkout $origBranch -q

$branches = git branch -r | Select-String "origin/feat/" | ForEach-Object { $_.ToString().Trim() -replace 'origin/', '' }
Write-Host "`n=== CREATED $($branches.Count) BRANCHES ===" -ForegroundColor Green
$branches | ForEach-Object { Write-Host "  - $_" }