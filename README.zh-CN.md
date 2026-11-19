# WhateverXe · TC3 HDMI 测试分支

[English](README.md) · [日本語](README_ja.md)

本分支基于 WhateverXe 0.8.3，为指定的联想 Alder Lake-S 台式机增加 **DDI 5（TC3）原生 HDMI** 的实验支持。功能默认关闭，使用 `-wex-adls-tc3-hdmi` 启用。

## 适用范围

- 实测设备为联想台式机，Core i5-12500、UHD 770（`8086:4690`），PCI 子系统 ID 为 `17aa:332c`。
- 主板固件需将 HDMI-D 报在 DDI 5，并使用 DDC 4。
- 实测环境为 macOS Tahoe 26.7.3 和 WhateverXe Graphics 0.4.4。DDI 4 的 DP 主屏与 DDI 5 的 HDMI 副屏同时直连，已验证冷启动、HDMI 拔插、屏幕休眠和短时整机睡眠唤醒。其他主板和长时间睡眠尚未验证。

## 编译和安装

1. 准备一套能正常启动的 [OpenCore 配置](README.md#installation)和 [WhateverXe Graphics 0.4.4](https://github.com/b00t0x/WhateverXe-Graphics/releases/tag/v0.4.4)。备份原 EFI、`/Library/Extensions/AppleIntelTGLCompat.kext` 和 `/Library/KernelCollections/AuxiliaryKernelExtensions.kc`。用原 EFI 制作一份可启动的 U 盘测试配置。
2. 用下面的命令获取本分支。按[编译依赖说明](README.md#build-and-test)准备 Xcode 命令行工具、Python、MacKernelSDK 和 Lilu 开发文件后，再运行编译命令。从同一次编译中取出 `build/WhateverXe.kext` 和 `build/AppleIntelTGLCompat.kext`。

   ```sh
   git clone --branch tc3-hdmi-0.8.3 https://github.com/yuanshuai2017/WhateverXe-pathced.git
   cd WhateverXe-pathced
   # 准备编译依赖后执行
   python3 tools/build.py
   ```

3. 按 [AMFIAnchor 签名指南](https://github.com/b00t0x/AMFIAnchor/blob/main/Docs/Signing.md)给新 Compat 签名，并生成配套的无可执行文件注入器。把它加入 U 盘 OpenCore 的 `Kernel → Add`，放在 AMFIAnchor 后面，`ExecutablePath` 留空。保留原 Graphics 注入器。先用原驱动从 U 盘启动，运行 `ioreg -r -c AMFIAnchor -l`，确认 `LoadedAnchors` 同时列出了原证书和测试证书。
4. 用签名版替换 `/Library/Extensions` 中的 `AppleIntelTGLCompat.kext`，然后重建 AuxKC。参考 [Graphics 0.4.4 的 `update_auxkc` 函数](https://github.com/b00t0x/WhateverXe-Graphics/blob/v0.4.4/uninstall.sh#L8-L24)。链接里的完整脚本会卸载 Graphics，请只参考该函数。如果重建失败，先恢复原 Compat 和 AuxKC，再重启。
5. 把新版 `WhateverXe.kext` 放进 U 盘 EFI，替换 U 盘上的同名文件。保留已有启动参数，在 OpenCore 的 `boot-args` 末尾追加 `-wex-adls-tc3-hdmi`。两台显示器保持直连，从 U 盘 EFI 启动。

## 验证和回退

运行以下命令，确认两个测试版 kext 已加载、系统识别到两台显示器，同时看到 `XELPSharedProbeBound = Yes` 和 `WEXADLSTC3HDMIClockEnabled = Yes`。测试版沿用上游版本号，可用 `dwarfdump --uuid` 读取两个编译产物的 UUID，再与加载列表核对。

```sh
kmutil showloaded | grep -E 'org\.b00t0x\.(WhateverXe|AppleIntelTGLCompat)'
ioreg -lw0 -d 1 | grep -E 'ADLSFirmwareRoutes|XELPSharedProbeBound|WEXADLSTC3HDMIClock'
system_profiler SPDisplaysDataType
```

启动后可以再测试 HDMI 拔插，观察副屏是否恢复、DP 主屏是否一直在线。

如需回退，先还原备份的原 Compat，再重建 AuxKC，或还原同一 macOS 构建上的原 AuxKC，之后从原 EFI 启动。仅切回原 EFI 无法恢复磁盘里的 Compat 和 AuxKC。如果进不了桌面，可从 macOS 恢复环境在 Data 卷上还原这两份系统侧备份。

其他机型的通用设置、兼容范围和许可请看 [English README](README.md)。
