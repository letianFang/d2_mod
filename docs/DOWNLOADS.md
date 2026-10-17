# FarmHub 下载与安装指南

适配基线：国服《暗黑破坏神 II：狱火重生》build **93854**，用于离线角色。历史包没有验证后续客户端版本；遇到版本不匹配时，请按仓库 README 的维护步骤处理。

## 先按需求选一个完整包

| 你的需求 | 下载选择 | 需要了解的限制 |
| --- | --- | --- |
| 想用目前历史压缩包中功能最多的版本 | **[v1.4.0：传送＋崔凡克视野＋快速操作＋导航＋大符文音效](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.4.0.zip)** | 26–33 号符文专用掉落音效尚待游戏内回归；不含后来新增的挖尸消失、面板去边框 |
| 想要入口和尼拉塞克方向提示，不要专用符文音效 | **[v1.3.1：导航版](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.3.1.zip)** | 保留快速操作；已取消崔凡克到憎恨囚牢的入口高亮 |
| 不要入口导航和符文音效，只要传送、崔凡克视野及快速操作 | **[v1.2.3：刷议会基础版](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.2.3.zip)** | 人物点击开局修复后尚待游戏内回归 |
| 只需要第四幕刷宝传送菜单和其他幕返回入口 | **[v1.0.4：仅传送版](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.0.4.zip)** | 不含崔凡克场景、人物点击开局、暂停菜单快速退出、导航和专用音效 |
| 想要挖尸后消失、去面板边框，以及国服尸体显示的启动说明 | 查看 [main 分支的当前工程](https://github.com/letianFang/d2_mod/tree/main) | **这 18 个历史 ZIP 均不含新尸体/边框资源。** 新改动已通过静态检查，游戏内效果仍待测试；不要把 v1.4.0 当作当前工程的完整打包版本 |

每个发布包都是一个完整版本，只选一个安装，不要叠加多个版本。功能是累积的，“导航版”也包含此前的传送、场景与快速操作，不是只包含导航的插件。

“快速操作”指：点击人物模型尝试直接进入地狱难度，以及在暂停菜单按钮外点击保存退出。前者要求角色已解锁地狱；后者不再二次确认，容易误点。

## 所有历史发布包的功能说明

下表用于查看版本演进和回退。除特别说明外，各版本继承前一版功能；早期问题版本不作为新用户的默认选择。

| 压缩包 | 包含功能或本版变化 | 选择提示 |
| --- | --- | --- |
| [FarmHub-v1.0.0.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.0.0.zip) | 第四幕刷宝传送菜单、其他幕返回第四幕入口 | 最早版本；使用独立存档目录，未带数据版本标记；仅供历史留档 |
| [FarmHub-v1.0.1.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.0.1.zip) | 传送功能；改为沿用原版存档、设置和键位 | 未带数据版本标记；仅供历史留档 |
| [FarmHub-v1.0.2.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.0.2.zip) | 传送功能；加入 build 93854 版本标记 | 标记末尾含换行，存在版本检测问题；不建议选用 |
| [FarmHub-v1.0.3.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.0.3.zip) | 传送功能；修正版本标记末尾换行 | 后续 v1.0.4 的文档更完整 |
| [FarmHub-v1.0.4.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.0.4.zip) | 仅传送功能；补充版本格式、客户端更新维护说明 | 需要最少功能时选它 |
| [FarmHub-v1.1.0.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.1.0.zip) | 增加崔凡克高清通透场景、人物模型点击进入地狱 | 早期人物入口存在多余控件/文字问题 |
| [FarmHub-v1.1.1.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.1.1.zip) | 删除多余人物快速开始控件 | 当时仍有贴图文字残留 |
| [FarmHub-v1.2.0.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.2.0.zip) | 增加原版暂停菜单外点击保存退出 | 尚未补齐扩展暂停布局 |
| [FarmHub-v1.2.1.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.2.1.zip) | 补齐扩展暂停布局的快速退出 | 用户确认快速退出可用；人物贴图问题尚未最终修复 |
| [FarmHub-v1.2.2.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.2.2.zip) | 尝试去除人物按钮贴图以隐藏文字 | 用户反馈人物点击开局失效；不建议选用 |
| [FarmHub-v1.2.3.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.2.3.zip) | 保留传送、崔凡克通透场景、快速退出；恢复人物按钮结构并使用透明贴图 | 人物点击修复已静态校验，游戏内仍待回归；不含导航和专用符文音效 |
| [FarmHub-v1.3.0.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.3.0.zip) | 增加下层入口光柱/光圈、瓦特之厅四种布局的尼拉塞克方向箭头 | 用户反馈导航正常；此版包含崔凡克入口高亮，后续应用户要求取消 |
| [FarmHub-v1.3.1.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.3.1.zip) | 保留导航；取消崔凡克通往憎恨囚牢的入口高亮 | 不需要专用符文音效时选它；取消高亮后的显示待游戏内确认 |
| [FarmHub-v1.4.0.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-v1.4.0.zip) | v1.3.1 全部功能，加 26 Vex 至 33 Zod 的专用符文掉落音效 | 历史打包功能最全；音效游戏内待回归，不含新尸体/边框资源 |

## 回退备份：通常不需要下载

`before-X` 表示“升级到 X **之前**保存的版本”，不是 X 本身。已逐文件核对：以下备份的有效 Mod 资源分别与表中版本一致，另外多了两个旧配置备份文件。它们只有 `FarmHub/` 目录，没有发布包中的 README 和安装脚本。

| 备份文件 | 实际保存的功能版本 | 用途 |
| --- | --- | --- |
| [FarmHub-before-v1.3.0-20260918-112705.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-before-v1.3.0-20260918-112705.zip) | v1.2.3：传送、崔凡克通透场景、快速操作；没有导航 | 回退到加入导航之前 |
| [FarmHub-before-v1.3.1-20260918-212658.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-before-v1.3.1-20260918-212658.zip) | v1.3.0：包含导航和崔凡克入口高亮 | 回退到取消崔凡克入口高亮之前 |
| [FarmHub-before-v1.4.0-20260918-214706.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-before-v1.4.0-20260918-214706.zip) | v1.3.1：有导航，已取消崔凡克入口高亮；没有专用符文音效 | 回退到加入符文音效之前 |
| [FarmHub-before-visibility-20261017-135634.zip](https://github.com/letianFang/d2_mod/releases/download/archive-2026-10-17/FarmHub-before-visibility-20261017-135634.zip) | v1.4.0：包含导航和专用符文音效；没有新尸体/边框资源 | 回退到本次尸体与边框修改之前 |

## 下载后自己安装

1. 下载上表中的一个 **FarmHub 附件 ZIP**。GitHub 页面自动生成的 `Source code (zip)` / `Source code (tar.gz)` 是源码快照，不是这张表里的安装包。
2. 完全关闭游戏。若已安装旧版，先把游戏目录下的 `mods\FarmHub` 移到游戏目录以外保存，再安装所选完整版本，避免旧资源残留。
3. 解压发布包，把里面的 `mods\FarmHub` 复制到游戏安装目录的 `mods` 中。例如最终应存在：

   ```text
   E:\Diablo II Resurrected\mods\FarmHub\FarmHub.mpq\modinfo.json
   ```

   如果下载的是回退备份，解压出来直接是 `FarmHub`，将它放进游戏目录的 `mods`；不要多套一层 `FarmHub` 文件夹。
4. 在战网的游戏设置中填写启动参数：

   ```text
   -mod FarmHub -txt
   ```

   国服要尝试将死亡墓碑恢复为尸体，可追加参数：

   ```text
   -mod FarmHub -txt -assettestmode 1
   ```

   该参数独立于历史压缩包；它本身不会加入“挖尸后隐藏已使用尸体”和“移除面板边框”资源。
5. 启动后选择离线角色。传送菜单只允许使用角色在当前难度已解锁的传送点；人物模型点击进入地狱也不会解锁难度。

安装脚本及更详细的兼容、存档和操作说明，见 [仓库 README](https://github.com/letianFang/d2_mod#readme)。历史 ZIP 内的 README 保持当时版本，下载选择以本页说明为准。
