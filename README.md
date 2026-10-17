# FarmHub：第四幕刷宝传送枢纽

### 当前工程快照（2026-10-17）

本次快照在 v1.4.0 基础上增加以下改动，已同步到本机 `E:\Diablo II Resurrected\mods\FarmHub`，尚待游戏内测试：

- 国服恢复怪物尸体显示：启动参数使用 `-mod FarmHub -txt -assettestmode 1`。墓碑恢复依赖该参数，不是新增模型替换文件；参数说明参考 [JCY Mod](https://github.com/jcymeow/jcy#使用)。
- 寻找物品/药水后隐藏已使用尸体：仅将当前客户端 `states.txt` 中 `corpse_noselect`（ID 118）的 `hide` 改为 `1`。按用户确认，全地图生效；其他触发相同状态的已使用尸体也会隐藏。未使用尸体的显示状态保留原版。
- 去除高清键鼠面板外侧边框及对应鼠标拦截区，保留面板锚点。装备、属性面板外侧露出的区域可用于观察和点击场景；传送距离与实际点击效果仍待游戏内确认。

新增 `build-farming-visibility.py` 和 `farming-visibility-assets.json` 记录构建方式、原文件及输出哈希。`verify.ps1` 已包含新资源的静态校验；静态通过不代表已完成游戏内验证。下文 `FarmHub-v1.4.0.zip` 是历史发布包，不包含这次新增功能；当前完整资源以 `mods/FarmHub` 为准。

仓库保留已有发布 ZIP、`backups/` 历史备份和 `.original-build-93854/` 构建基线；不收录本机 `.tools/` 工具及 `.reference-*` 第三方参考检出。后续日常修改使用 Git 提交记录，不再每次新增 ZIP 备份。游戏存档不纳入此仓库。

这是一个用于《暗黑破坏神 II：狱火重生》（D2R）离线模式的数据模组。它补满第四幕传送点菜单的 9 个固定槽位，并在其他各幕保留一条返回第四幕城镇（群魔堡垒）的通路。

此外，模组提供以下刷宝便利功能：

- 崔凡克议会建筑采用更通透的高清场景布局，减少柱子和屋顶造成的视野遮挡，方便确认剩余怪物。
- 在离线人物选择页直接点击人物模型，可跳过难度选择窗口并以地狱难度创建游戏。
- 游戏中按下 `Esc` 打开暂停菜单后，点击菜单按钮以外的空白区域，可直接保存并退出当前游戏。
- 关键下层入口持续显示光柱和地面光圈，覆盖憎恨囚牢、世界之石要塞、尼拉塞克神殿、地下墓穴、塔内下层入口；崔凡克通往憎恨囚牢的入口保持原版显示。
- 瓦特之厅四种尼拉塞克布局分别加载对应方向的箭头，减少辨认缺角的操作。
- 26号 Vex 至33号 Zod 掉落时播放磨刀门 Mod 对应的专用提示音，其他符文使用原版声音。

### 大号符文掉落音效（v1.4.0）

音效提取自本机 `E:\磨刀门MOD\MDM\MDM\MDM.mpq\Data\HD\Global\sfx\item\high_rune_26.flac` 至 `high_rune_33.flac`，逐文件保留原音频。默认范围为 26 Vex、27 Ohm、28 Lo、29 Sur、30 Ber、31 Jah、32 Cham、33 Zod；Ist/Gul 及以下仍为原版掉落声音。各音频长度不同，Ber 提示约6.6秒。

从当前国服 build 93854 客户端 CASC 中提取原版 `misc.txt`、`sounds.txt`，只修改八个符文的 `dropsound`，并在原声音表末尾追加八行专用音效记录及不冲突的 ID。拾取/使用声音 `usesound` 保留原版。没有导入磨刀门的符文模型、光柱、其他物品规则或完整数据表，不修改掉率。声音由游戏原生掉落音效机制触发，无内存读取或 DLL 注入。

`rune-audio-assets.json` 记录音频和表哈希、符文范围、原表哈希及音频时长；`build-rune-audio.py` 可用提取后的当前客户端原表和 MDM 资源重建。本功能已通过合并差异检查、音效映射与 ID 校验，游戏内触发仍需回归。完全退出游戏后重启，确保音效音量开启；可将已有大号符文从背包丢到地上确认音效，再检查实际怪物掉落。提示遵守游戏的声音距离与播放限制，不能保证所有远处掉落都听得到。

本功能完整覆盖 `misc.txt` 和 `sounds.txt`，更新客户端后需重新提取原表合并；与修改这两张表的其他 Mod 需要手工合并。

### 新增导航功能（v1.3.0）

入口提示和方向箭头仅作用于高清游戏画面，不会在小地图绘制箭头，也不会揭开未探索地图。进入瓦特之厅后查看场景箭头，按箭头指示选择尼拉塞克所在支路。

入口使用共享的下层楼梯资源，因此憎恨囚牢第二层通往第三层、世界之石要塞第三层通往毁灭王座及采用相同资源的其他下层楼梯都会显示提示；提示本身不区分楼层号码，不会改变入口点击范围或传送目标。

用户已反馈 v1.3.0 新导航功能游戏内测试正常。v1.3.1 取消崔凡克通往憎恨囚牢的入口高亮，避免干扰蛮子刷议会；保留其他导航资源。此次移除通过静态校验和安装一致性检查，移除后的显示待游戏内确认。

箭头是静态高清场景资源：在 `nihln.json`、`nihle.json`、`nihls.json`、`nihlw.json` 四种地图布局中分别放置对应方向的粒子实体，游戏加载本局布局时自然加载对应箭头。FarmHub 没有读取游戏进程内存、注入 DLL 或外部运行时程序；构建与安装脚本只处理磁盘文件。这个实现说明不等于对战网使用或账号处罚作出保证，本项目仅用于离线角色。

资源参考自 [lukezord/d2r-advanced](https://github.com/lukezord/d2r-advanced)，固定提交与文件哈希记录在 `navigation-assets.json`。`build-navigation.py` 可从工程内 `.reference-d2r-advanced` 重建资源；发布包使用已生成资源，无需 Python 即可安装。参考场景不是从当前客户端重新提取的原文件，客户端更新后应提取新版四种场景并只迁移 `FarmHubNihlathakArrow*` 实体及其依赖。

新增维护文件：`data/hd/roomtiles/*.json`（入口光柱和光圈）、`data/hd/env/porory/beacon/`（光圈与纹理）、`data/hd/env/preset/expansion/wildtemple/nihl{n,e,s,w}.json`（四种布局）、`data/hd/directionarrows/`（箭头粒子与纹理）、两张 `data/hd/nickname/textures/graphic/` 兼容纹理（补齐粒子中残留的材质引用）。这些资源与修改同名场景的其他 Mod 需要合并。

> [!IMPORTANT]
> 项目当前记录的适配基线为国服客户端 build `93854`，代码发布包为 `FarmHub-v1.4.0.zip`。这不代表已验证后续客户端更新。暴雪更新游戏后，请先阅读下方“游戏更新后的必要维护”，不要直接忽略版本不匹配警告。

## 日常使用细则

1. 使用 `-mod FarmHub -txt` 启动游戏，选择离线角色。
2. 已解锁地狱难度的角色，在人物选择页点击中间的角色模型，即可尝试直接创建地狱游戏。不是点击右侧角色列表，也不需要寻找额外按钮；点击区域不显示文字提示。
3. 本功能固定选择地狱，不会自动判断“角色目前解锁的最高难度”，也不会解锁难度。未解锁地狱或需要普通/噩梦时，使用原“开始游戏”按钮。
4. 进入群魔堡垒，使用第四幕传送点菜单选择已解锁的刷宝目的地。其他幕的返回槽位见下表。
5. 刷完后按 `Esc`，点击暂停菜单按钮外的空白区域，执行保存并退出当前游戏，返回人物选择页；不是关闭 D2R 程序。
6. 重复点击人物模型开启下一局。需要继续当前游戏时，请点“返回游戏”，不要点菜单外空白处。

快速退出无需二次确认，容易误点。该功能只在暂停菜单打开时生效，并非正常游戏画面中的任意点击都退出。修改界面资源后请完全退出 D2R 再启动，不要仅返回人物选择页。

### 当前验证状态

- 用户已反馈传送功能、崔凡克显示改善和暂停菜单外点击退出可用。
- 人物点击功能经历过文字残留与透明点击区失效；`v1.2.3` 已恢复原按钮贴图结构并使用全透明像素，静态校验与安装目录一致性检查已通过，但该版本的游戏内人物点击结果仍需回归确认。

## 第四幕传送点菜单

| 槽位 | 目的地 | 用途 |
| --- | --- | --- |
| 1 | 群魔堡垒 | 第四幕城镇 |
| 2 | 绝望平原 | 衣卒尔 |
| 3 | 火焰之河 | 海法斯特、迪亚波罗路线 |
| 4 | 黑色荒地 | 女伯爵钥匙/符文 |
| 5 | 地下墓穴第二层 | 安达利尔 |
| 6 | 神秘避难所 | 召唤者钥匙 |
| 7 | 崔凡克 | 议会成员 |
| 8 | 憎恨囚牢第二层 | 墨菲斯托 |
| 9 | 世界之石要塞第二层 | 巴尔路线 |

新增目的地仍沿用原版传送点的解锁状态；角色必须在当前难度中取得对应传送点后才能点击它。

## 跨幕返回映射

为了从其他幕的列表直接返回第四幕城镇，以下低价值槽位被替换：

| 幕 | 被替换的原传送点 | 新目的地 |
| --- | --- | --- |
| 第一幕 | 监牢第一层 | 群魔堡垒 |
| 第二幕 | 皇宫监牢第一层 | 群魔堡垒 |
| 第三幕 | 庞大湿地 | 群魔堡垒 |
| 第五幕 | 冰冻苔原 | 群魔堡垒 |

原场景里的传送点物件没有被删除，仍可用于离开该场景；只是它不再出现在城镇传送点菜单中，因而不能从城镇直接返回。

## 安装

复制前完全关闭 D2R，并备份角色存档和已有的 `mods\FarmHub`。本机安装路径为 `E:\Diablo II Resurrected`；模组资源位于 `E:\Diablo II Resurrected\mods\FarmHub\FarmHub.mpq`。

方法一（自动复制）：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -D2RPath "C:\你的路径\Diablo II Resurrected"
```

方法二（手动复制）：把本工程中的 `mods\FarmHub` 整个复制到 D2R 安装目录，使最终路径为：

```text
Diablo II Resurrected\mods\FarmHub\FarmHub.mpq\modinfo.json
Diablo II Resurrected\mods\FarmHub\FarmHub.mpq\data\global\DataVersionBuild.txt
Diablo II Resurrected\mods\FarmHub\FarmHub.mpq\data\global\excel\actinfo.txt
Diablo II Resurrected\mods\FarmHub\FarmHub.mpq\data\global\ui\layouts\mainmenupanelhd.json
Diablo II Resurrected\mods\FarmHub\FarmHub.mpq\data\global\ui\layouts\pauselayouthd.json
Diablo II Resurrected\mods\FarmHub\FarmHub.mpq\data\global\ui\layouts\pauselayoutgardenhd.json
Diablo II Resurrected\mods\FarmHub\FarmHub.mpq\data\hd\env\preset\act3\travincal\travn.json
Diablo II Resurrected\mods\FarmHub\FarmHub.mpq\data\hd\global\ui\panel\message\QuickStart.sprite
Diablo II Resurrected\mods\FarmHub\FarmHub.mpq\data\hd\global\ui\panel\message\QuickStart.lowend.sprite
```

然后给 Battle.net 或游戏快捷方式添加启动参数：

```text
-mod FarmHub -txt
```

## 游戏更新后的必要维护

暴雪更新 D2R 后，本模组也需要同步检查。不要仅仅点击版本警告中的“继续”，因为客户端数据表结构或内容可能已经改变。

每次游戏更新后应执行以下操作：

1. 启动一次未加载模组的游戏，确认客户端已完成更新。
2. 记录客户端显示的新数据版本号。
3. 从当前客户端重新提取最新版 `data\global\DataVersionBuild.txt`、`data\global\excel\actinfo.txt`、`mainmenupanelhd.json`、`pauselayouthd.json`、`pauselayoutgardenhd.json` 和崔凡克 `travn.json`。
4. 以新版 `actinfo.txt` 为基础，重新应用 FarmHub 的传送点映射；不要用旧表覆盖新版表。
5. 以新版界面和场景文件为基础，重新合并人物点击进入地狱与崔凡克通透布局；不要长期沿用旧版本的完整资源文件。
6. 确认 `DataVersionBuild.txt` 与客户端版本完全一致。
7. 运行 `verify.ps1`，通过后再启动模组，测试传送点、人物快速进入和崔凡克显示。

`DataVersionBuild.txt` 有严格格式要求：内容只能是版本号本身，必须使用纯 ASCII、无 BOM，并且末尾不能有空格或换行。例如 build 93854 的正确文件恰好是以下 5 个字节：

```text
39 33 38 35 34
```

如果弹窗中的“当前数据版本”和“检测到的数据版本”看起来相同，但仍提示不匹配，通常就是版本文件包含了隐藏的 BOM、回车或换行。弹窗句号被挤到下一行也是末尾换行的明显特征。

仅修改版本号只能消除版本检测警告，不能证明旧数据表、界面布局或场景资源与新客户端兼容。若暴雪更新了这些文件，必须以新版原文件为基础重新合并对应改动。

## 存档、设置与联机注意事项

- 仅用于离线模式，不要带着数据模组进入战网角色。
- `modinfo.json` 使用 `savepath: "../"`，直接沿用原版角色、`Settings.json` 和 `Custom.key`，因此启动模组后键位与快速施法设置不会另起一套。
- 已经取得的传送点状态保存在角色的当前难度记录里；模组不会自动替你解锁刷宝点。
- 点击人物模型快速进入游戏会固定选择地狱难度，因此角色需要已经解锁地狱难度；需要进入普通或噩梦时，请使用界面上的“开始游戏”按钮并手动选择。
- `Esc` 菜单外区域属于快速保存退出热区，点击后会立即离开当前游戏，不再出现二次确认；需要关闭菜单时请点击“返回游戏”按钮或再次按 `Esc`。
- 崔凡克通透场景修改的是 D2R 高清画面资源；切换到经典画面时仍会显示经典场景。
- 本模组完整覆盖 `actinfo.txt`。与其他也修改该表的模组一起使用时，需要手工合并。

国服客户端的默认配置目录通常是 `Saved Games\Diablo II Resurrected (CN)`；国际服通常是 `Saved Games\Diablo II Resurrected`。本模组会自动使用当前客户端对应的默认目录。

## 自检

在工程根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\verify.ps1
```

该脚本会检查版本文件字节、模组清单 JSON、TSV 列数与映射、人物快速进入控件和指令、两张透明贴图的 SHA-256、两套暂停菜单的退出控件，以及崔凡克场景文件大小、新导航资源哈希、入口光柱和四种方向箭头。

这是静态检查，不会启动游戏，也不会完整解析所有界面/场景 JSON，更不能证明界面命中区域、场景显示或新客户端兼容性正确。通过后仍需要游戏内回归测试。

如果游戏更新后再次出现“检测到不匹配的版本数据”，请按照“游戏更新后的必要维护”完整处理，不要只修改版本号。

## 实现说明

传送功能只重排 `actinfo.txt` 中每幕的 `waypoint1` 至 `waypoint9`，不会改动任务、怪物、地图碰撞或传送点物件，因此目的地保持原版落点和解锁逻辑。由于 D2R 每幕传送点界面最多只有 9 个固定槽位，这种方式不会真正创建第 10 个以上的传送点。

崔凡克功能替换高清场景显示文件，用于减少议会建筑的视觉遮挡；它不会删除怪物、改变掉落或修改怪物 AI。人物快速进入功能在人物选择页增加透明点击区域，并向游戏发送地狱难度（难度编号 `2`）的载入指令。

快速退出功能在两套高清暂停菜单（原版与恶君扩展布局）的背景层增加透明点击区域，并发送游戏原生的“保存并退出”指令；菜单中的原有按钮位于其上方，功能保持不变。

## 后续维护：文件与功能对应

下表中的资源路径均相对于 `mods\FarmHub\FarmHub.mpq`。

| 文件 | 职责与更新约束 |
| --- | --- |
| `modinfo.json` | 模组名称与共享存档路径；保留 `name: FarmHub`、`savepath: ../`，避免键位和存档目录发生切换。 |
| `data\global\DataVersionBuild.txt` | 数据版本标记；必须与目标客户端匹配，且无 BOM、空白和换行。 |
| `data\global\excel\actinfo.txt` | 第四幕刷宝点与其他幕返回映射；必须以新版原表为基础合并。 |
| `data\global\ui\layouts\mainmenupanelhd.json` | 人物模型透明点击控件 `InvisibleHellStart`，载入指令为 `CharacterSelect:LoadCharacter:2`。 |
| `data\hd\global\ui\panel\message\QuickStart.sprite` | 高清全透明四帧按钮图集，提供原按钮结构与尺寸；不要换回带文字版本或直接删除。 |
| `data\hd\global\ui\panel\message\QuickStart.lowend.sprite` | 对应低配置全透明资源；应与高清版本一起维护、安装。 |
| `data\global\ui\layouts\pauselayouthd.json` | 原版高清暂停布局；背景控件 `FastExitBackground` 使用 `PausePanelMessage:ExitGame`。 |
| `data\global\ui\layouts\pauselayoutgardenhd.json` | 恶君扩展高清暂停布局；同样需要退出背景，并保留其原有功能按钮。 |
| `data\hd\env\preset\act3\travincal\travn.json` | 崔凡克议会区域高清显示资源；保留通透显示改动，不修改地图碰撞和刷怪逻辑。 |

### 不要重复引入的已知问题

- 只把人物按钮的 `textString` 设为空，不能隐藏贴图中烘焙的文字。当前两张 `QuickStart` 资源保留文件头和图集结构，像素数据全部清零。
- 不要把图集总宽度当作单帧宽度来计算点击区域。当前高清资源是四帧图集，单帧约 `658×1300`；曾经改成无贴图的 `400×198` 区域后，用户反馈点击人物无法开局。
- 人物按钮目前保留 `filename: PANEL\\message\\QuickStart`、`hoveredFrame: 3` 和空 `textString`，不加入可见说明按钮或焦点提示图。
- 暂停菜单必须同时维护两套布局。仅修改 `pauselayouthd.json`，可能导致读取扩展布局的游戏完全没有变化。
- 透明退出背景必须位于菜单按钮下层。不要用顶层全屏热区盖住设置、返回游戏等按钮。
- 与其他模组冲突不只限于 `actinfo.txt`：人物选择界面、暂停布局、崔凡克场景或同名贴图被覆盖时，也需要合并。

### 更新、同步与发布流程

1. 备份存档、当前已安装 Mod 和本次需要修改的资源。
2. 先更新工程中的 `mods\FarmHub`，不要只修改游戏目录，避免下次安装覆盖修复。
3. 对照新版原始数据合并改动；如果版本号、表结构或透明贴图发生合法变化，同步更新 `verify.ps1` 的版本、结构或哈希预期。
4. 运行 `verify.ps1`，记录输出；关闭游戏后执行安装脚本：

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install.ps1 -D2RPath "E:\Diablo II Resurrected"
   ```

5. 安装脚本只复制并覆盖文件，不会自动清理旧资源。若本次删除或改名文件，应列出并备份后清理安装目录中对应旧文件，不能删除存档。
6. 对本次修改的文件比较工程与安装目录的 SHA-256，确认资源确实同步。
7. 完全重启游戏，完成下方回归测试，再发布包含 `mods`、`README.md`、`install.ps1`、`verify.ps1`、`navigation-assets.json`、`build-navigation.py`、`rune-audio-assets.json`、`build-rune-audio.py` 的新版本压缩包。
8. 更新文档中的发布版本、适配基线、验证状态和变更记录。本文后续补充不自动更新历史 ZIP 包内的旧 README；下次打包应使用工程最新文档。

### 游戏内回归清单

- 启动无版本不匹配警告，离线角色、原键位与快速施法设置正常。
- 地狱已解锁角色点击模型可开局且无文字提示；普通/噩梦仍可由原按钮手动选择。
- 第四幕九个传送槽位正确，新增目的地遵守当前难度解锁状态，其他四幕可返回群魔堡垒。
- 崔凡克高清议会区域视野改善，怪物和原路线正常。
- 暂停菜单外点击保存退出；菜单内设置和返回按钮正常，日常点击不会触发退出。
- 分别检查原版与扩展暂停布局；检查高清/低配置资源及不同分辨率下人物点击区是否仍覆盖模型。
- 保存退出后重新开局，确认角色进度与掉落物品正常保存。

## 变更记录

| 版本 | 主要变更 |
| --- | --- |
| `v1.4.0` | 从磨刀门提取26–33号符文专用掉落音效，以当前客户端93854原表合并八个掉落声音字段和八条声音记录；游戏内待验证。 |
| `v1.3.1` | 根据用户反馈取消崔凡克到憎恨囚牢入口高亮；安装脚本清理该旧覆盖文件，恢复客户端原版显示。用户确认 v1.3.0 导航功能正常。 |
| `v1.3.0` | 添加关键下层入口光柱与光圈、瓦特之厅四种布局的尼拉塞克方向箭头、导航资源清单及静态校验；游戏内效果待回归。 |
| `v1.0.x` | 第四幕刷宝传送枢纽、其他幕返回映射、共享存档/键位设置、版本标记格式修复和更新说明。 |
| `v1.1.0` | 崔凡克通透场景与人物点击进入地狱。 |
| `v1.1.1` | 删除额外的人物快速开始控件；仍存在贴图文字残留。 |
| `v1.2.0` | 添加原版暂停菜单外点击保存退出。 |
| `v1.2.1` | 补齐扩展暂停布局，用户随后确认快速退出正常。 |
| `v1.2.2` | 尝试移除人物按钮贴图以隐藏文字；用户反馈人物点击开局失效，不建议作为最终方案。 |
| `v1.2.3` | 恢复人物按钮贴图结构，将高清与低配置贴图像素清空为透明，并加入哈希校验；人物点击需游戏内回归确认。 |

文档维护记录：2026-09-18 补充完整使用细则、资源对应、历史问题、更新发布流程与回归清单；本次仅更新说明文档，不改变 Mod 资源或启动方法。
