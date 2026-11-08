# Dell Inspiron 13 5330 — upstream Xe build workspace

复用现有开源项目构建 Intel Iris Xe 实验性内核组件，不重写或修改上游显卡驱动源码。

上游：[JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe](https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe)。固定版本和依赖见 `UPSTREAM.lock.json`。

GitHub Actions 在 `macos-15-intel` 上调用上游现有脚本，构建 `NootedGreen.kext` 和 `HookCase.kext`，检查 x86_64 Mach-O 内核类型、bundle 标识及 ad-hoc 签名，最后保存产物和日志。构建不会加载驱动、安装 macOS 或测试 GPU。

## 测试目标与范围

计划测试 Dell Inspiron 13 5330 / i5-1340P / Iris Xe。上游已记录相同 CPU 的 80 EU 修正参数：

```text
ngreen-eu=80 ngreen-l3=6
```

这些是上游已有功能，本仓库不再增加机型封装。参数依据见[上游安装说明](https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe/blob/24450b476d7ca025b83c85d7b8362caf3234d2f2/docs/INSTALL.md)与 [issue 3](https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe/issues/3)。本机尚未验证图形加速、内屏、背光、视频或睡眠。

这两个 kext 只是完整加速栈的一部分。还需要上游匹配的 Tiger Lake 图形驱动、Metal 用户态适配层、Lilu、正确的本机 OpenCore 配置等。仅安装本仓库产物不会自动获得图形加速。其他机型的 EFI 不能直接作为本机配置。

## 构建

推送配置后自动触发，也可在 Actions 中手动运行。产物保存 7 天。

在 Intel macOS 构建机上可运行：

```sh
bash build-upstream.sh
python3 tools/verify-and-package.py
```

输出：`build/dell5330-upstream-kexts.tar.gz`、`build/artifact-manifest.json`。

## 来源与许可证

此仓库只保存构建配置，不保存本机采集报告、凭据、SMBIOS 标识或 Apple 图形驱动二进制。

下载的上游源码及构建出的组件保留其原始版权和许可证：NootedGreen 使用上游 `src/LICENSE-NootedGreen`；HookCase 使用 `src/LICENSE-HookCase`。产物附带两份许可证与对应源码提交。新增构建配置可按 MIT License 使用。
