# Master Node

N-panel that binds to a category master node and exposes its parameters.

**Status:** framework public / presets paid / Blender 4.2+ / tests: pytest without Blender.

This is the **material-system product**, not a preset pack. The framework is public. Presets are paid.

Artists install the add-on and look-dev in the 3D Viewport. They do not need Cursor.

```
active material  →  category master (node group)  →  N-panel RNA sliders
```

[Plygon-mcp](https://github.com/Plygonality/Plygon-mcp) is how an agent installs this, tweaks a slider, and screenshots the viewport. It is not the product.

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-ff6a1a?style=flat-square" alt="MIT"></a>
  <a href="master_node/"><img src="https://img.shields.io/badge/Blender-4.2%2B-orange?style=flat-square&logo=blender&logoColor=white" alt="Blender 4.2+"></a>
  <img src="https://img.shields.io/badge/presets-paid-111111?style=flat-square" alt="Presets paid">
</p>

## Why this repo exists

A material library that ships a hundred `.blend` looks is a pack. The pack goes stale the moment you need a value that is not on the card.

A **category master** is the opposite. Metal is one node group. Glass is one node group. The N-panel binds to whichever master the active material uses and draws that group's sockets through RNA. You change Roughness in the sidebar. The graph does not change.

| Role | Job |
|---|---|
| **This add-on** | Protocol, category masters, bind, N-panel |
| **Presets** | Value packs against those masters. Paid. |
| **Plygon-mcp** | Live loop: install → set a socket → screenshot |
| **The `.blend`** | Working cache, never the source of truth |

## Install

First-time install is a zip of the **`master_node/`** folder, not the repository root. Blender needs `master_node/__init__.py` inside the zip. A GitHub "Download ZIP" of the whole repo will not install.

```bash
python scripts/package_zip.py   # writes dist/master_node.zip
```

Then **Blender → Preferences → Add-ons → Install** and pick that zip.

If you already have a clone and a local Blender add-ons folder, this copies `master_node/` there instead of making a zip:

```bash
python scripts/install_addon.py
```

Enable **Material: Master Node**. 3D Viewport → `N` → **Master Node**.

Blender 4.2+. The add-on also lives in the Shader Editor sidebar.

## Use

1. Select an object.
2. Pick a category (`Surface`, `Metal`, `Dielectric`, `Glass`, `Fabric`, `Emissive`, `Layered`).
3. **Create Master**. The material gets that category's node group.
4. Tweak the sliders. They *are* the group inputs — `layout.prop(socket, "default_value")`.

Bind a group you already built: select it in the Shader Editor and **Bind Selected Group**. The panel will pick it up as the category master.

## Screenshots

Panel capture is TODO. This repo does not ship screenshots yet.

## Protocol

A node group is a master when it carries ID properties:

| Key | Meaning |
|---|---|
| `mn.is_master` | This group is a category master |
| `mn.category` | `surface` `metal` `dielectric` `glass` `fabric` `emissive` `layered` |
| `mn.version` | Interface version |
| `mn.origin` | `framework` or `user` |

A material points at its master with `mn.master` (group name). If that marker is missing, the panel walks the shader tree and binds the first marked group.

The catalog in `master_node/core/catalog.py` is the source of truth for framework masters. `masters.py` only instantiates them as `ShaderNodeTree` datablocks.

## Presets

Free looks ship with the framework so a new file is usable. Paid looks are a pack: JSON value maps against the same sockets.

| Tier | Where | Gate |
|---|---|---|
| Free | `master_node/data/presets/free/` | None |
| Paid | Add-on Preferences → paid pack folder | License key |

Without a key, paid names still appear in the panel, locked. `MN-DEV-UNLOCK` unlocks them for tests and the agent loop. It is not a store license.

```json
{
  "format": "master-node-preset",
  "version": 1,
  "id": "metal.chrome",
  "name": "Chrome",
  "category": "metal",
  "tier": "free",
  "values": { "Color": [0.95, 0.95, 0.97, 1.0], "Roughness": 0.02 }
}
```

## Cursor / live loop

The product is an add-on artists use without Cursor. The agent loop is optional.

```python
from master_node.live import bind_category, set_param

bind_category("metal")
set_param("Roughness", 0.12)   # RNA default_value on the bound group
```

Or run the self-contained script through Plygon-mcp:

```
execute_blender_code(scripts/live_loop.py)
get_viewport_screenshot()
```

Headless smoke, if you have Blender on PATH:

```bash
blender --background --python scripts/smoke_blender.py
```

## Tests

No Blender required for the protocol, catalog, bind resolver, or paid gate.

```bash
pip install -e ".[dev]"
pytest -q
```

```bash
UPDATE_GOLDENS=1 pytest tests/test_golden.py   # rewrite category interface fixtures
```

## Repo map

| Path | What |
|---|---|
| `master_node/core/` | bpy-free protocol, catalog, presets, license |
| `master_node/panel.py` | N-panel (View3D + Shader Editor) |
| `master_node/rna_draw.py` | Draw / set sockets through RNA |
| `master_node/masters.py` | Build framework category groups |
| `master_node/data/presets/` | Free looks + paid name catalog |
| `scripts/live_loop.py` | Agent: bind, tweak, dump |
| `tests/goldens/` | Category interface fixtures |

## Why not MCP

MCP is a bridge for Cursor. This is a panel for artists. If the only way to change Roughness is a tool call, the product failed.

[github.com/Plygonality/Master-Node](https://github.com/Plygonality/Master-Node)
