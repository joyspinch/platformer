# 素材生成脚本（入库）：逐张调用 image2 生成 1024x1024 原图。
#
# 原图落在 build/raw/（gitignore，不入库）；后处理脚本 client/tools/make_assets.py
# 把原图抠底/裁边/缩放/镜像成入库素材（client/assets/）。
#
# 用法：
#   pwsh -File client/tools/gen_assets.ps1
#   python client/tools/make_assets.py
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$out = Join-Path (Split-Path -Parent $project) 'build/raw'
New-Item -ItemType Directory -Force $out | Out-Null
$script = "$HOME\.codex\skills\local-image2\scripts\image2.ps1"

$items = @(
    @{ name = 'bg_far'; prompt = 'Wide panoramic distant mountain range at dusk, layered violet and blue peaks fading into atmospheric haze, deep indigo sky above, flat 2D side-scrolling game parallax background, painterly stylized art, no characters, no creatures, no text, no UI, no foreground objects, no border, no frame' },
    @{ name = 'bg_mid'; prompt = 'Mid ground parallax layer for a 2D side-scrolling platformer game: a row of rolling grassy hills with dark pine trees and a few boulders along the bottom edge, empty transparent sky above, stylized flat illustration, sharp clean silhouettes, the landscape occupies only the lower third of the frame, isolated on a solid pure black background, no characters, no text, no UI, no border' },
    @{ name = 'bg_near'; prompt = 'Foreground parallax layer for a 2D side-scrolling platformer game: a horizontal strip of dark bushes, ferns and small rocks along the very bottom of the frame, upper two thirds completely empty, stylized flat illustration, sharp clean silhouettes, isolated on a solid pure black background, no characters, no text, no UI, no border' },
    @{ name = 'player'; prompt = 'Cute chunky pixel-art robot explorer character, full body, standing side view facing right, teal and orange jumpsuit with a glowing visor, simple readable silhouette, single character centered, isolated on a solid pure black background, no ground, no shadow, no text, no border' },
    @{ name = 'drone'; prompt = 'Hostile flying patrol drone enemy for a 2D platformer game, small round metal body with a single glowing red eye and two little thruster wings, hovering side view, simple readable silhouette, single object centered, isolated on a solid pure black background, no ground, no shadow, no text, no border' },
    @{ name = 'shard'; prompt = 'Glowing cyan crystal shard collectible pickup for a 2D platformer game, faceted gemstone with bright inner light, simple readable silhouette, single object centered, isolated on a solid pure black background, no ground, no shadow, no text, no border' },
    @{ name = 'tile_ground'; prompt = 'Seamless tileable stone brick platform block for a 2D platformer game, mossy grass on the top edge, warm grey stone bricks below, flat straight-on view, sharp edges, single square block filling the frame, isolated on a solid pure black background, no characters, no text, no border, no frame' },
    @{ name = 'flag'; prompt = 'Exit goal flag for a 2D platformer game: a glowing golden banner on a slim metal pole planted in a small stone base, cheerful and readable, single object centered, isolated on a solid pure black background, no ground shadow, no text, no border' }
)

foreach ($it in $items) {
    $path = Join-Path $out ($it.name + '.png')
    Write-Host "=== generating $($it.name) ==="
    & $script generate --model gpt-image-2.5 --prompt $it.prompt --size 1024x1024 --quality high --output-format png --out $path --force
    if ($LASTEXITCODE -ne 0) { throw "generate failed: $($it.name)" }
}
Write-Host "ALL_DONE"
