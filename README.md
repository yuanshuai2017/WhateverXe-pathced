# WhateverXe

[简体中文](README.zh-CN.md) · [日本語](README_ja.md)

WhateverXe is a Lilu plugin, derived from WhateverGreen, that adapts Apple graphics drivers for selected Intel Xe-LP integrated GPUs.
Use the latest releases of [WhateverXe](https://github.com/b00t0x/WhateverXe/releases) and [WhateverXe Graphics](https://github.com/b00t0x/WhateverXe-Graphics/releases) together. See [CHANGELOG](CHANGELOG.md) for release notes.

## TC3 HDMI test branch

This branch is based on WhateverXe 0.8.3. It adds opt-in support for native HDMI wired to DDI 5 (TC3) on a Lenovo Alder Lake-S desktop with a Core i5-12500, UHD 770 (`8086:4690`) and PCI subsystem `17aa:332c`. The firmware must describe a fixed HDMI-D port on DDI 5 with DDC 4. The branch has been tested on macOS Tahoe 26.7.3 with WhateverXe Graphics 0.4.4, using DDI 4 DisplayPort and DDI 5 HDMI at the same time. Coverage includes cold boot, HDMI reconnection, display sleep and short system sleep. Other boards and longer sleep cycles remain unverified.

### Build and install

1. Start with a working [OpenCore setup](#installation) and [WhateverXe Graphics 0.4.4](https://github.com/b00t0x/WhateverXe-Graphics/releases/tag/v0.4.4). Back up the original EFI, `/Library/Extensions/AppleIntelTGLCompat.kext` and `/Library/KernelCollections/AuxiliaryKernelExtensions.kc`. Prepare a bootable USB copy of the EFI for testing.
2. Follow [Build and test](#build-and-test) for dependencies, then run `python3 tools/build.py` from this branch to build the DEBUG pair. Use both `build/WhateverXe.kext` and `build/AppleIntelTGLCompat.kext` from the same build.
3. Sign the new Compat and generate a matching codeless injector using the [AMFIAnchor signing guide](https://github.com/b00t0x/AMFIAnchor/blob/main/Docs/Signing.md). Add this injector after `AMFIAnchor.kext` in the USB OpenCore config and keep the original Graphics injector enabled. Boot the USB EFI with the known-working driver pair first. Use `ioreg -r -c AMFIAnchor -l` to confirm that both anchors appear in `LoadedAnchors`.
4. Replace only `AppleIntelTGLCompat.kext` in `/Library/Extensions` with the signed build and rebuild AuxKC using the [Graphics 0.4.4 AuxKC procedure](https://github.com/b00t0x/WhateverXe-Graphics/blob/v0.4.4/uninstall.sh#L8-L24). The linked script also removes Graphics. Refer to its `update_auxkc` function only. If rebuilding fails, restore the original Compat and AuxKC before restarting.
5. Replace `WhateverXe.kext` in the USB EFI and append `-wex-adls-tc3-hdmi` to the existing OpenCore `boot-args`. Keep your existing required arguments. Boot from the USB EFI with both monitors connected directly. Omitting the TC3 argument leaves the experimental route disabled.

### Verify and roll back

Check that macOS detects both displays and that the test pair is loaded. The build keeps the upstream bundle versions, so compare the loaded UUIDs with `dwarfdump --uuid` on the two built executables.

```sh
kmutil showloaded | grep -E 'org\.b00t0x\.(WhateverXe|AppleIntelTGLCompat)'
ioreg -lw0 -d 1 | grep -E 'ADLSFirmwareRoutes|XELPSharedProbeBound|WEXADLSTC3HDMIClock'
system_profiler SPDisplaysDataType
```

With the HDMI display connected, look for `XELPSharedProbeBound = Yes` and `WEXADLSTC3HDMIClockEnabled = Yes`. Test HDMI unplug/replug while the DP display stays online.

To restore the original setup, first restore the backed-up Compat. Then rebuild AuxKC or restore the matching original AuxKC from the same macOS build. Boot the original EFI afterward. If the desktop is unavailable, use macOS Recovery to restore the two system-side backups on the Data volume. Booting the original EFI alone leaves the replaced Compat and AuxKC on disk.

## Compatibility

| macOS | Required version |
| --- | --- |
| Big Sur | 11.7.11 |
| Monterey | 12.7.6 |
| Ventura | 13.7.8 |
| Sonoma | 14.8.9 |
| Sequoia | 15.8.x |
| Tahoe | 26.7 or newer |

Sequoia and Tahoe accept compatible updates within their OS family. Future Apple changes may require an update to WEX or Graphics.

### Tested on hardware

- Tiger Lake-U: 48- and 80-EU configurations.
- Alder Lake-N: 16- and 24-EU configurations.
- Twin Lake: 32-EU configurations.
- Alder Lake-H: 96-EU configurations, including single-channel operation.
- Alder Lake-S: UHD Graphics 770.
- Raptor Lake-U: 48-EU configurations.

See [tested features and known issues](#tested-features-and-known-issues) for OS coverage and display configurations. PCI IDs are listed in [device selection](docs/device-selection.md).

### Expected to work, not yet tested on hardware

- Other supported Tiger Lake-U/H35 configurations, including 96 EU, and Tiger Lake-H45.
- Other supported Alder Lake-N / Twin Lake configurations.
- Other supported Alder Lake-H/P/U and Raptor Lake-H/P/U configurations.
- Other supported Alder Lake-S/HX and Raptor Lake-S/HX configurations.
- Internal eDP on Alder Lake-N / Twin Lake and Alder Lake-H/P/U / Raptor Lake-H/P/U is implemented but has not been tested on hardware. Brightness supports PCH PWM and standard VESA AUX; panel-specific OLED/Intel HDR brightness remains unqualified.

### Further implementation required

- Rocket Lake-S: display control requires additional support.

### No support planned

- Xe-LPG, including Meteor Lake integrated graphics.
- Xe2 and later graphics architectures.

## Installation

1. Add Lilu 1.7.2 or later and `WhateverXe.kext` from the **RELEASE** ZIP to OpenCore, with WEX after Lilu. Install [AMFIAnchor](https://github.com/b00t0x/AMFIAnchor/releases/latest) and [`AMFIAnchorInjector.kext`](https://github.com/b00t0x/AMFIAnchor/tree/main/Injectors) as described in the [OpenCore instructions](https://github.com/b00t0x/AMFIAnchor/blob/main/README.md#install-with-opencore).
2. Set `csr-active-config=03080000` (`0x803`) and apply the [configuration](#configuration).
3. Boot the target macOS, install the latest [WhateverXe Graphics pkg](https://github.com/b00t0x/WhateverXe-Graphics/releases), then restart. [Package installation and removal](https://github.com/b00t0x/WhateverXe-Graphics#install).

If upgrading from AMFIPass 1.4.1 Mod, remove its OpenCore entry. Keep AMFI enabled. WhateverGreen and WhateverXe must not be enabled together. `amfi=0x80` and `ipc_control_port_options=0` are unnecessary.

Graphics installs under `/Library` and rebuilds AuxKC without patching System files or snapshots. Restore an old Xe System patch before installing. If you use [OCLP](https://github.com/dortania/OpenCore-Legacy-Patcher) for other root patches, load OCLP's AMFIPass after AMFIAnchor and its injector.

## Configuration

### Required boot arguments

Add to OpenCore's `boot-args`:

```text
-allow3d -disablegfxfirmware
```

### DVMT

Set **DVMT Pre-Allocated to 96MB** in BIOS/UEFI where possible.
If it is fixed at **60MB**, also add `-igfxdvmt` and set these iGPU properties under `DeviceProperties > Add` (usually `PciRoot(0x0)/Pci(0x2,0x0)`):

| Property | Type | Value (hex) |
| --- | --- | --- |
| `framebuffer-patch-enable` | Data | `01000000` |
| `framebuffer-stolenmem` | Data | `0000C003` |

These settings are unnecessary at 96MB and do not increase firmware-allocated memory.

### Other settings

- Add `SSDT-PNLF` for internal-display brightness control.
- GPU selection is automatic; a `device-id` override is normally unnecessary.
- Alder Lake-N / Twin Lake and Alder Lake-H/P/U / Raptor Lake-H/P/U select tiling automatically. Do not use `-yTileDisable`; `AAPL,GfxYTile` is unnecessary.

## Tested features and known issues

The common regression checks cover Metal, OpenGL, OpenCL, hardware H.264 encode/decode and HEVC decode. The table summarizes OS coverage and configuration-specific display features.

| Configuration | Verified coverage |
| --- | --- |
| Tiger Lake mini PCs | Big Sur–Tahoe: 80 EU, two 1080p60 displays, display off/on, Safari video and Widevine |
| Tiger Lake laptops | Big Sur–Tahoe: 48 EU, internal eDP and brightness, HDMI/USB-C, up to three displays and display off/on |
| Alder Lake-N mini PCs | Big Sur–Tahoe: 16/24 EU, two 1080p60 HDMI displays and display off/on |
| Alder Lake-N / Twin Lake laptops | MicroPC 2 and MiniBook X N100 on Big Sur/Tahoe: MIPI DSI, brightness, rotation, display off/on and HDMI/USB-C coexistence. MicroPC 2: HiDPI and up to three displays; MiniBook X N100: optional 60 Hz |
| Raptor Lake-U laptop | MiniBook X U300 on Big Sur/Tahoe: internal MIPI DSI, brightness, rotation, HiDPI and up to two USB-C displays. Internal panel: 50 Hz; optional 60 Hz also tested on Big Sur |
| Alder Lake-H | Big Sur–Tahoe: 96 EU, three displays using HDMI and a DP-to-HDMI adapter. Single-channel `4626` graphics acceleration checked on Big Sur |
| Alder Lake-S | Big Sur–Tahoe: UHD 770, HDMI/DP/USB-C and up to three displays; Safari video, with Widevine checked on Big Sur/Tahoe |

MIPI DSI support is **experimental**, limited to the tested GPD MicroPC 2 and CHUWI MiniBook X N100/U300 panels. Do not expect it to work on other devices.

System sleep/wake support is **experimental**. Tested configurations are MiniBook X N100/U300 (MIPI DSI) on Big Sur and Tahoe with model-specific ACPI settings, using the internal display alone or up to two external displays. See the [TC3 HDMI test branch](#tc3-hdmi-test-branch) for the desktop result. Prolonged DarkWake cycles remain unverified.

### Known issues and limits

- DisplayPort reconnection can cause black screens or freezes. Tiger Lake USB-C reconnection is also unreliable; Alder Lake-S DP output/reconnection can be slow.
- Some image-conversion operations can crash applications.
- Safari video may occasionally drop frames. FairPlay-protected playback is unsupported.
- Up to three displays are supported. Resolutions beyond the tested configurations remain unverified.
- Some connector layouts and backlight methods, MST and Thunderbolt-managed outputs are unsupported.

### Roadmap

- Complete DisplayPort, USB-C and internal-display support on Alder Lake-N / Twin Lake and Alder Lake-H/P/U / Raptor Lake-H/P/U.
- Improve display reconnection reliability and extend system sleep/wake coverage.

## Build and test

Requires macOS, Xcode command-line tools, Python 3.9+, MacKernelSDK and Lilu 1.7.2 development headers/library. Place `MacKernelSDK/` and `Lilu.kext/` in the repository root, or pass `--sdk` and `--lilu`.

```sh
python3 tools/build.py --release
python3 tools/test.py
```

Output is under `build/`. AppleIntelTGLCompat is built here and distributed through Graphics. Optional exact-donor tests accept `--donor` and `--accelerator` paths.

## License and credits

WhateverXe retains WhateverGreen's copyright notices and BSD-3-Clause license.
See [LICENSE.txt](LICENSE.txt). Lilu and MacKernelSDK are separate dependencies.

Thanks to [JulioNectar/XPS13Plus](https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe) for sharing its Xe graphics work. Its compiler adapter and LLVM bridge informed the OS-native AIR conversion used in WhateverXe Graphics.

Internal-panel work also draws on [WhateverXe-RaptorLakeP](https://github.com/samranahmad09/WhateverXe-RaptorLakeP), [X1Carbon-G11](https://github.com/dssoftx/Hackintosh-X1Carbon-G11-IrisXe-Tahoe), XPS13Plus and the [Linux i915 display sources](https://github.com/torvalds/linux/tree/v6.12/drivers/gpu/drm/i915/display) for hardware behavior and implementation comparisons.

eDP boot-handoff and startup corrections also reference the reports and patches from [ann0see](https://github.com/ann0see/WhateverXe/tree/522c0a1bd60b9beac66e00dfd7414823680639dd), [belugaa-01](https://github.com/belugaa-01/WhateverXe-Patched), [Thatisjigen](https://github.com/Thatisjigen/WhateverXe), and [zsz-of](https://github.com/zsz-of/WhateverXe).

The optional MiniBook X 60 Hz panel timing also draws on the [minibookx-ctl display guide](https://github.com/ishad0w/minibookx-ctl/blob/main/docs/guide/display.md).

Display wake rearming and GGTT restoration were informed by [jkbuha/WhateverXe](https://github.com/jkbuha/WhateverXe). The AUX brightness investigation also referenced [JulioNectar](https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe); the VESA implementation uses protocol facts from Linux DRM, without copying NootedGreen code.
