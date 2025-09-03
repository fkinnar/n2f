# Script PowerShell pour corriger les listes ordonnées dans les fichiers Markdown
# Corrige les erreurs MD029/ol-prefix

param(
    [string]$FilePath
)

function Fix-OrderedLists {
    param([string]$filePath)
    
    Write-Host "Correction des listes ordonnees dans $filePath..."
    
    try {
        $content = Get-Content $filePath -Raw
        $lines = $content -split "`n"
        $fixedLines = @()
        
        for ($i = 0; $i -lt $lines.Length; $i++) {
            $line = $lines[$i]
            
            # Détecter si c'est une ligne de liste ordonnée
            if ($line -match '^(\s*)\d+\.\s+(.+)$') {
                $indent = $matches[1]
                $content = $matches[2]
                
                # Chercher la liste complète qui suit
                $listItems = @()
                $j = $i
                
                # Collecter tous les éléments de la liste consécutifs
                while ($j -lt $lines.Length -and $lines[$j] -match '^(\s*)\d+\.\s+(.+)$') {
                    $listItems += $lines[$j]
                    $j++
                }
                
                # Corriger la numérotation de cette liste
                for ($k = 0; $k -lt $listItems.Count; $k++) {
                    $item = $listItems[$k]
                    if ($item -match '^(\s*)\d+\.\s+(.+)$') {
                        $itemIndent = $matches[1]
                        $itemContent = $matches[2]
                        $correctedItem = "$itemIndent$($k + 1). $itemContent"
                        $fixedLines += $correctedItem
                    } else {
                        $fixedLines += $item
                    }
                }
                
                # Sauter les lignes déjà traitées
                $i = $j - 1
            } else {
                $fixedLines += $line
            }
        }
        
        # Écrire le fichier corrigé
        $fixedLines -join "`n" | Set-Content $filePath -Encoding UTF8
        Write-Host "OK: $filePath corrige avec succes"
        return $true
        
    } catch {
        Write-Host "Erreur lors de la correction de $filePath : $($_.Exception.Message)"
        return $false
    }
}

# Traitement principal
if ($FilePath) {
    # Traiter un fichier spécifique
    Fix-OrderedLists $FilePath
} else {
    # Traiter tous les fichiers Markdown du projet
    Write-Host "Script de correction des listes ordonnees Markdown"
    Write-Host "============================================================"
    
    $projectRoot = Split-Path $PSScriptRoot -Parent
    $markdownFiles = Get-ChildItem -Path $projectRoot -Filter "*.md" -Recurse | Where-Object {
        $_.FullName -notmatch "\\env\\|\\venv\\|\\__pycache__\\"
    }
    
    Write-Host "$($markdownFiles.Count) fichiers Markdown trouves"
    Write-Host ""
    
    $successCount = 0
    foreach ($file in $markdownFiles) {
        if (Fix-OrderedLists $file.FullName) {
            $successCount++
        }
    }
    
    Write-Host ""
    Write-Host "Resume : $successCount/$($markdownFiles.Count) fichiers corriges avec succes"
    Write-Host "============================================================"
    Write-Host "Script termine !"
}
