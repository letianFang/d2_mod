$ErrorActionPreference = 'Stop'

$tablePath = Join-Path $PSScriptRoot 'mods\FarmHub\FarmHub.mpq\data\global\excel\actinfo.txt'
$manifestPath = Join-Path $PSScriptRoot 'mods\FarmHub\FarmHub.mpq\modinfo.json'
$dataVersionPath = Join-Path $PSScriptRoot 'mods\FarmHub\FarmHub.mpq\data\global\DataVersionBuild.txt'
$mainMenuPath = Join-Path $PSScriptRoot 'mods\FarmHub\FarmHub.mpq\data\global\ui\layouts\mainmenupanelhd.json'
$travincalPath = Join-Path $PSScriptRoot 'mods\FarmHub\FarmHub.mpq\data\hd\env\preset\act3\travincal\travn.json'
$quickStartSpritePath = Join-Path $PSScriptRoot 'mods\FarmHub\FarmHub.mpq\data\hd\global\ui\panel\message\QuickStart.sprite'
$quickStartLowEndSpritePath = Join-Path $PSScriptRoot 'mods\FarmHub\FarmHub.mpq\data\hd\global\ui\panel\message\QuickStart.lowend.sprite'
$pauseMenuPath = Join-Path $PSScriptRoot 'mods\FarmHub\FarmHub.mpq\data\global\ui\layouts\pauselayouthd.json'
$gardenPauseMenuPath = Join-Path $PSScriptRoot 'mods\FarmHub\FarmHub.mpq\data\global\ui\layouts\pauselayoutgardenhd.json'

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.name -ne 'FarmHub' -or $manifest.savepath -ne '../') {
    throw 'modinfo.json does not contain the expected values.'
}

$dataVersionBytes = [System.IO.File]::ReadAllBytes($dataVersionPath)
$expectedDataVersionBytes = [System.Text.Encoding]::ASCII.GetBytes('93854')
if ($dataVersionBytes.Length -ne $expectedDataVersionBytes.Length -or
    (Compare-Object $dataVersionBytes $expectedDataVersionBytes -SyncWindow 0)) {
    throw 'DataVersionBuild.txt must be exactly five ASCII bytes: 93854 (no BOM or newline).'
}

$rows = @(Import-Csv -LiteralPath $tablePath -Delimiter "`t")
if ($rows.Count -ne 5) {
    throw "actinfo.txt must contain 5 data rows; found $($rows.Count)."
}

$headers = @((Get-Content -LiteralPath $tablePath -TotalCount 1) -split "`t")
if ($headers.Count -ne 21) {
    throw "actinfo.txt must contain 21 columns; found $($headers.Count)."
}

foreach ($row in $rows) {
    foreach ($column in $headers) {
        if ($null -eq $row.$column) {
            throw "Act $($row.act) is missing column: $column"
        }
    }
}

$act4 = $rows | Where-Object act -eq '4'
$expectedFarmTargets = @(
    'Act 1 - Wilderness 5',
    'Act 1 - Catacombs 2',
    'Act 2 - Arcane',
    'Act 3 - Travincal',
    'Act 3 - Mephisto 2',
    'Act 5 - Baal Temple 2'
)
$actualFarmTargets = 4..9 | ForEach-Object { $act4."waypoint$_" }
if (Compare-Object $expectedFarmTargets $actualFarmTargets) {
    throw 'The Act IV farming destination mapping is incorrect.'
}

$returnActs = @('1', '2', '3', '5')
foreach ($act in $returnActs) {
    $row = $rows | Where-Object act -eq $act
    $hasReturn = 1..9 | Where-Object { $row."waypoint$_" -eq 'Act 4 - Town' }
    if (-not $hasReturn) {
        throw "Act $act has no return slot pointing to the Act IV town."
    }
}

$mainMenuText = Get-Content -LiteralPath $mainMenuPath -Raw
if ($mainMenuText -notmatch 'CharacterSelect:LoadCharacter:2' -or
    $mainMenuText -notmatch '"name"\s*:\s*"InvisibleHellStart"' -or
    $mainMenuText -notmatch 'PANEL\\\\message\\\\QuickStart') {
    throw 'The character-select quick Hell configuration is missing or incorrect.'
}
$quickHellMatches = [regex]::Matches($mainMenuText, 'CharacterSelect:LoadCharacter:2')
if ($quickHellMatches.Count -ne 1 -or
    $mainMenuText -match '点击角色快速开始|点击角色快速开房|focusIndicatorFilename') {
    throw 'The character-select layout must contain one invisible Hell shortcut and no visible quick-start label.'
}

$expectedTransparentSpriteHashes = @{
    $quickStartSpritePath = '6239C8950ACE6EBBA481A662175BD121222B2ED3069E95A0CD009078769D2917'
    $quickStartLowEndSpritePath = 'A40B272002F7FE18B91C9EB841DF5C100B321DE5651AABF9394EFE37D9E2D12E'
}
foreach ($spritePath in $expectedTransparentSpriteHashes.Keys) {
    $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $spritePath).Hash
    if ($actualHash -ne $expectedTransparentSpriteHashes[$spritePath]) {
        throw "The quick-start sprite is not the expected fully transparent image: $spritePath"
    }
}

foreach ($currentPauseMenuPath in @($pauseMenuPath, $gardenPauseMenuPath)) {
    $pauseMenuText = Get-Content -LiteralPath $currentPauseMenuPath -Raw
    if ($pauseMenuText -notmatch '"type"\s*:\s*"ButtonWidget"\s*,\s*"name"\s*:\s*"FastExitBackground"' -or
        $pauseMenuText -notmatch '(?s)"name"\s*:\s*"FastExitBackground".*?"fitToParent"\s*:\s*true.*?"onClickMessage"\s*:\s*"PausePanelMessage:ExitGame"') {
        throw "The pause-menu background quick-exit configuration is missing or incorrect: $currentPauseMenuPath"
    }
}

$travincalInfo = Get-Item -LiteralPath $travincalPath
if ($travincalInfo.Length -lt 1000000) {
    throw 'The Travincal open-layout file is missing or unexpectedly small.'
}

$navigation = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'navigation-assets.json') -Raw | ConvertFrom-Json
$modRoot = Join-Path $PSScriptRoot 'mods\FarmHub\FarmHub.mpq'
foreach ($removedFile in $navigation.removedFiles) {
    if (Test-Path -LiteralPath (Join-Path $modRoot $removedFile)) {
        throw "Removed navigation override still exists: $removedFile"
    }
}
foreach ($file in $navigation.files.PSObject.Properties) {
    $assetPath = Join-Path $modRoot $file.Name
    if ((Get-FileHash -LiteralPath $assetPath -Algorithm SHA256).Hash -ne $file.Value) {
        throw "Navigation asset hash mismatch: $($file.Name)"
    }
}
foreach ($tile in $navigation.entranceTiles) {
    $scene = Get-Content -LiteralPath (Join-Path $modRoot "data/hd/roomtiles/$tile.json") -Raw | ConvertFrom-Json
    $beam = @($scene.entities | Where-Object name -eq 'FarmHubEntranceBeam')
    if ($beam.Count -ne 1 -or $beam[0].components.filename -notcontains 'data/hd/vfx/particles/overlays/object/horadric_light/fx_horadric_light.particles') {
        throw "Entrance beam missing: $tile"
    }
    if ($scene.entities.components.prefab -notcontains 'data/hd/env/porory/beacon/pf_beacon_downstairs.json') {
        throw "Entrance beacon missing: $tile"
    }
}
foreach ($direction in $navigation.directionAngles.PSObject.Properties) {
    $scene = Get-Content -LiteralPath (Join-Path $modRoot "data/hd/env/preset/expansion/wildtemple/nihl$($direction.Name).json") -Raw | ConvertFrom-Json
    $arrows = @($scene.entities | Where-Object name -like 'FarmHubNihlathakArrow*')
    $particle = "data/hd/directionarrows/particles/directionarrows_$($direction.Value).particles"
    if ($arrows.Count -ne 11 -or @($arrows.id | Select-Object -Unique).Count -ne 11) {
        throw "Nihlathak arrows are missing or have duplicate IDs: $($direction.Name)"
    }
    foreach ($arrow in $arrows) {
        if ($arrow.components.filename -notcontains $particle) {
            throw "Incorrect Nihlathak direction: $($direction.Name)"
        }
    }
    if ($scene.dependencies.particles.path -notcontains $particle) {
        throw "Nihlathak particle dependency missing: $($direction.Name)"
    }
}
$runeAudio = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'rune-audio-assets.json') -Raw | ConvertFrom-Json
foreach ($file in $runeAudio.files.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $modRoot $file.Name)).Hash -ne $file.Value) {
        throw "Rune audio asset hash mismatch: $($file.Name)"
    }
}
$misc = @(Import-Csv -LiteralPath (Join-Path $modRoot 'data/global/excel/misc.txt') -Delimiter "`t")
$sounds = @(Import-Csv -LiteralPath (Join-Path $modRoot 'data/global/excel/sounds.txt') -Delimiter "`t")
if ($misc.Count -ne $runeAudio.miscRows -or $sounds.Count -ne $runeAudio.soundRows) {
    throw 'Rune audio table row counts are incorrect.'
}
foreach ($rune in $runeAudio.runes) {
    $item = @($misc | Where-Object code -eq $rune.code)
    $sound = @($sounds | Where-Object Sound -eq $rune.sound)
    if ($item.Count -ne 1 -or $item[0].dropsound -ne $rune.sound -or $item[0].usesound -ne 'item_rune') {
        throw "Rune drop/use sound mapping incorrect: $($rune.code)"
    }
    if ($sound.Count -ne 1 -or $sound[0].FileName -ne "item\$($rune.sound).flac" -or
        $sound[0].Channel -ne 'sfx/items_hd' -or $sound[0].Loop -ne '0' -or $sound[0].Redirect -ne '') {
        throw "Rune sound definition incorrect: $($rune.sound)"
    }
    $soundId = $sound[0].'*Index'
    if (@($sounds | Where-Object { $_.'*Index' -eq $soundId }).Count -ne 1) {
        throw "Rune audio sound ID collision: $soundId"
    }
}
foreach ($item in $misc) {
    if ($item.code -match '^r(0[1-9]|1[0-9]|2[0-5])$' -and $item.dropsound -ne 'item_rune') {
        throw "Low rune sound was unexpectedly changed: $($item.code)"
    }
}
$visibility = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'farming-visibility-assets.json') -Raw | ConvertFrom-Json
foreach ($file in $visibility.files.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $modRoot $file.Name)).Hash -ne $file.Value) {
        throw "Farming visibility asset hash mismatch: $($file.Name)"
    }
}
$states = @(Import-Csv -LiteralPath (Join-Path $modRoot 'data/global/excel/states.txt') -Delimiter "`t")
$usedCorpse = @($states | Where-Object state -eq 'corpse_noselect')
if ($usedCorpse.Count -ne 1 -or $usedCorpse[0].'*ID' -ne '118' -or $usedCorpse[0].hide -ne '1') {
    throw 'Used corpse visibility state is incorrect.'
}
$borders = Get-Content -LiteralPath (Join-Path $modRoot 'data/global/ui/layouts/panelborderspanelhd.json') -Raw | ConvertFrom-Json
if ($borders.type -ne 'BordersPanel' -or $borders.children.Count -ne 2 -or
    @($borders.children | Where-Object { $_.children.Count -ne 0 }).Count -ne 0 -or
    $borders.children[0].name -ne 'LeftAnchor' -or $borders.children[1].name -ne 'RightAnchor') {
    throw 'Panel borders or mouse click catchers are still present.'
}
$stashMerge = [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot 'stash-merge-assets.json'), [System.Text.Encoding]::UTF8) | ConvertFrom-Json
foreach ($file in $stashMerge.files.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $modRoot $file.Name)).Hash -ne $file.Value) {
        throw "Stash merge asset hash mismatch: $($file.Name)"
    }
}
foreach ($removedFile in $stashMerge.removedFiles) {
    if (Test-Path -LiteralPath (Join-Path $modRoot $removedFile)) {
        throw "Retired stash resource still exists: $removedFile"
    }
}
$bank = [System.IO.File]::ReadAllText((Join-Path $modRoot 'data/global/ui/layouts/bankexpansionlayouthd.json'), [System.Text.Encoding]::UTF8) | ConvertFrom-Json
$bankGroup = { param($name) @($bank.children | Where-Object name -eq $name) }
$bankTabs = @(& $bankGroup 'BankTabs')
if ($bankTabs.Count -ne 1 -or $bankTabs[0].fields.tabCount -ne 3 -or $bankTabs[0].fields.textStrings[2] -ne $stashMerge.tabLabel) {
    throw 'The merged stash tab bar is incorrect.'
}
$stashGrid = @((& $bankGroup 'basicstash_container')[0].children | Where-Object name -eq 'grid')
if ($stashGrid.Count -ne 1 -or $stashGrid[0].fields.cellCount.x -ne 10 -or $stashGrid[0].fields.cellCount.y -ne 10) {
    throw 'The personal and shared stash grid must stay 10x10.'
}
foreach ($emptyGroup in @('advancedstash_materials', 'advancedstash_runes')) {
    if (@((& $bankGroup $emptyGroup)[0].children).Count -ne 0) {
        throw "Merged stash source group must stay empty: $emptyGroup"
    }
}
$slotCodes = @((& $bankGroup 'advancedstash_gems')[0].children | ForEach-Object { $_.fields.itemCode })
$stackableCodes = @($misc | Where-Object AdvancedStashStackable -eq '1' | ForEach-Object code)
if ($slotCodes.Count -ne $stashMerge.slotCount -or @($slotCodes | Select-Object -Unique).Count -ne $slotCodes.Count -or
    (Compare-Object $slotCodes $stackableCodes)) {
    throw 'The merged stash slots do not match the stackable items in misc.txt.'
}
$cubeWidgets = @((& $bankGroup 'advancedstash_horadriccube')[0].children)
$autoTransmute = @($cubeWidgets | Where-Object name -eq 'auto_convert_container')
if ($autoTransmute.Count -ne 1 -or $autoTransmute[0].children[0].fields.onClickMessage -ne 'PanelManager:TogglePanel:CALL/mymodConvertAutoStart') {
    throw 'The auto-transmute toggle is missing or incorrect.'
}
$autoStart = Get-Content -LiteralPath (Join-Path $modRoot 'data/global/ui/layouts/CALL/mymodConvertAutoStarthd.json') -Raw | ConvertFrom-Json
$autoStep = Get-Content -LiteralPath (Join-Path $modRoot 'data/global/ui/layouts/CALL/mymodConverthd.json') -Raw | ConvertFrom-Json
if ($autoStart.name -ne 'CALL/mymodConvertAutoStart' -or $autoStep.name -ne 'CALL/mymodConvert' -or
    @($autoStep.children | Where-Object { $_.fields.message -eq 'BankPanelMessage:Convert' -and $_.fields.time -eq $stashMerge.transmuteIntervalSeconds }).Count -ne 1) {
    throw 'The auto-transmute timer panels are incorrect.'
}
$buffLabels = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'buff-labels-assets.json') -Raw | ConvertFrom-Json
foreach ($file in $buffLabels.originalSha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot ".original-build-93854/$($file.Name)")).Hash -ne $file.Value) {
        throw "Buff overlay baseline mismatch: $($file.Name)"
    }
}
foreach ($removedFile in $buffLabels.removedFiles) {
    if (Test-Path -LiteralPath (Join-Path $modRoot $removedFile)) {
        throw "Retired buff label still exists: $removedFile"
    }
}
foreach ($file in $buffLabels.files.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $modRoot $file.Name)).Hash -ne $file.Value) {
        throw "Buff label asset hash mismatch: $($file.Name)"
    }
}
foreach ($label in $buffLabels.labels.PSObject.Properties) {
    $warcry = @($states | Where-Object state -eq $label.Name)
    if ($warcry.Count -ne 1 -or $warcry[0].overlay1 -ne $label.Name) {
        throw "Buff label state no longer uses its vanilla overlay: $($label.Name)"
    }
    $overlay = Get-Content -LiteralPath (Join-Path $modRoot $label.Value.overlay) -Raw | ConvertFrom-Json
    $particle = @($overlay.entities.components | Where-Object type -eq 'VfxDefinitionComponent')
    if ($overlay.type -ne 'OverlayDefinition' -or $particle.Count -ne 1 -or
        $particle[0].filename -ne $label.Value.particle -or -not $particle[0].hardKillOnDestroy -or
        $overlay.dependencies.particles.path -notcontains $particle[0].filename -or
        -not (Test-Path -LiteralPath (Join-Path $modRoot $particle[0].filename) -PathType Leaf)) {
        throw "Buff label overlay is incorrect: $($label.Name)"
    }
    $transform = @($overlay.entities.components | Where-Object type -eq 'TransformDefinitionComponent')
    if ($transform.Count -ne 1 -or $transform[0].position.x -ne 122 -or
        $transform[0].position.y -ne 95 -or $transform[0].position.z -ne 116 -or
        $transform[0].scale.x -ne 1 -or $transform[0].scale.y -ne 1 -or $transform[0].scale.z -ne 1 -or
        -not $transform[0].inheritOnlyPosition -or
        $overlay.dependencies.textures.path -notcontains $label.Value.texture) {
        throw "MDM3C buff transform/texture mismatch: $($label.Name)"
    }
    foreach ($asset in @($label.Value.particle, $label.Value.texture)) {
        if ((Get-FileHash -LiteralPath (Join-Path $modRoot $asset)).Hash -ne $buffLabels.sourceSha256.$asset) {
            throw "MDM3C source asset is not byte-identical: $asset"
        }
    }
    $particleBytes = [IO.File]::ReadAllBytes((Join-Path $modRoot $label.Value.particle))
    if (-not [Text.Encoding]::ASCII.GetString($particleBytes).Contains("__sampler_0=$($label.Value.texture)")) {
        throw "MDM3C buff texture sampler mismatch: $($label.Name)"
    }
}
$itemLabelsPath = Join-Path $PSScriptRoot 'item-labels-assets.json'
if (Test-Path -LiteralPath $itemLabelsPath -PathType Leaf) {
    $itemLabels = [System.IO.File]::ReadAllText($itemLabelsPath, [System.Text.Encoding]::UTF8) | ConvertFrom-Json
    foreach ($file in $itemLabels.files.PSObject.Properties) {
        if ((Get-FileHash -LiteralPath (Join-Path $modRoot $file.Name)).Hash -ne $file.Value) {
            throw "Item label strings hash mismatch: $($file.Name)"
        }
    }
}
$hydraHide = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'hydra-display-assets.json') -Raw | ConvertFrom-Json
foreach ($file in $hydraHide.files.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $modRoot $file.Name)).Hash -ne $file.Value) {
        throw "Hydra hide asset hash mismatch: $($file.Name)"
    }
}
$hdMissiles = [System.IO.File]::ReadAllText((Join-Path $modRoot 'data/hd/missiles/missiles.json'), [System.Text.Encoding]::UTF8) | ConvertFrom-Json
if ($hdMissiles.hydra -ne 'icebolt' -or $hdMissiles.firebolt -ne 'firebolt' -or $hdMissiles.icebolt -ne 'icebolt') {
    throw 'Only the hydra missile may use the Ice Bolt look; Fire Bolt and Ice Bolt must keep their models.'
}
foreach ($hydraFile in $hydraHide.removedEntities.PSObject.Properties.Name) {
    $hydraUnit = [System.IO.File]::ReadAllText((Join-Path $modRoot $hydraFile), [System.Text.Encoding]::UTF8) | ConvertFrom-Json
    if (@($hydraUnit.entities).Count -ne 1 -or $hydraUnit.entities[0].name -ne 'entity_root') {
        throw "Hydra unit must keep only entity_root: $hydraFile"
    }
}
Write-Host 'Verification passed: existing FarmHub features, navigation, high-rune audio, used corpse visibility, borderless panels, merged stash tab, Battle Orders/Command labels, hidden hydras with cyan bolts, item tiers, and asset hashes.'
