# FjBa Basic Scale Grid Generator

**Version:** 1.1.3  
**Edition:** Basic  
**Minimum QGIS version:** 3.28  
**Platform:** Windows, Linux and macOS  
**Language:** Python 3  
**Interface:** QGIS PyQt

---

## Overview

FjBa Basic Scale Grid Generator is a QGIS plugin designed to create scale-based rectangular and square map frames directly on the map canvas.

The plugin provides an interactive placement workflow, configurable paper dimensions, frame styling and a grid manager for managing created frames.

It is designed for cartographic layouts, map preparation and spatial project organization.

## Features

### Paper formats
- A0, A1, A2, A3 and A4.
- Portrait and landscape orientation.
- Configurable page margins.

### Grid generation
- Scale-based frame dimensions.
- Rectangular and square frames.
- Interactive click-to-place workflow.
- Real-time map canvas preview.
- Projected coordinate reference system support.

### Frame appearance
- Customizable outline colours.
- Adjustable outline width.
- Configurable fill transparency.
- Optional grid labels.

### Grid management
- Automatic grid numbering.
- Grid identification and selection.
- Rename existing grids.
- Delete selected grids.
- Save configurations to JSON.
- Load saved JSON configurations.

## Installation

### Installation through QGIS

1. Open QGIS.
2. Navigate to **Plugins → Manage and Install Plugins**.
3. Search for `FjBa Basic Scale Grid Generator`.
4. Select the plugin.
5. Click Install.

### Installation from ZIP

1. Download the plugin ZIP package.
2. Open QGIS.
3. Navigate to **Plugins → Manage and Install Plugins**.
4. Select the **Install from ZIP** tab.
5. Browse to the downloaded ZIP file.
6. Click Install Plugin.

## How to use

1. Open your QGIS project.
2. Launch FjBa Basic Scale Grid Generator from the Plugins menu or toolbar.
3. Select a paper format (A0–A4).
4. Choose portrait or landscape orientation.
5. Enter the desired map scale.
6. Set the page margin.
7. Select rectangular or square geometry.
8. Configure the frame appearance.
9. Enable or disable grid labels and automatic numbering.
10. Click **Start placement**.
11. Move the mouse over the map to preview the frame.
12. Left-click to create a grid frame.
13. Right-click to stop placement.

Created frames are managed through the Grid Manager panel.

## Saving and loading configurations

Use **Save configuration** to export grid records into a JSON file.

Use **Load configuration** to import previously saved configurations.

The JSON configuration stores grid identifiers, names, scales, paper formats, orientations and geometries.

## Requirements

- QGIS 3.28 or later, within the supported QGIS 3.x compatibility range.
- Python 3.
- PyQGIS.
- PyQt provided by QGIS.

No additional third-party Python packages are required by the current implementation.

## Coordinate reference systems

The plugin calculates frame dimensions using the current project's map units.

A suitable projected coordinate reference system is recommended for reliable scale-based dimensions.

Supported map units in the current implementation:
- Metres.
- Kilometres.
- International feet.
- US survey feet.

Geographic coordinate systems are not supported for scale-based frame calculations.

## Output

Generated frames are stored in a polygon memory layer named:

`FjBa Basic Grid Frames`

The layer is added to the current QGIS project.

**Note:** A memory layer is temporary. Save or export the layer separately if you want to preserve the generated polygon features permanently.

## Compatibility

| Component | Compatibility |
|---|---|
| QGIS | 3.28 and later QGIS 3.x releases, subject to testing |
| Python | Python 3 |
| Qt interface | QGIS PyQt |
| QGIS 4 | Not currently supported |

QGIS 4 compatibility will be evaluated in a future release.

## License

This project is intended to be distributed under the GNU General Public License v2.0 or later (GPL-2.0-or-later).

See the `LICENSE` file for licensing information.

## Author

**FjBa**

Project: FjBa Basic Scale Grid Generator  
Edition: Basic

## Version history

### Version 1.1.0

- Basic scale-based grid generation.
- A0–A4 paper formats.
- Portrait and landscape orientation.
- Rectangular and square frames.
- Interactive map placement.
- Real-time grid preview.
- Customizable frame appearance.
- Grid manager.
- Rename and delete functionality.
- JSON configuration saving and loading.
- FjBa emerald and gold interface branding.

## Feedback and bug reports

Please report bugs, compatibility issues and suggestions through the project's issue tracker.

Project repository: To be added.  
Issue tracker: To be added.

---

**FjBa Basic Scale Grid Generator**  
*Simple and reliable map frame creation.*
