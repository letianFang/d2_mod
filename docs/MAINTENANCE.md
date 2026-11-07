# FarmHub 维护文档

本文面向模组维护者，记录实现方式、资源对应、已知问题和发布流程。玩家使用说明见 [README](../README.md)。

发布 ZIP 和历史备份统一放在 [GitHub Releases](https://github.com/letianFang/d2_mod/releases)，不作为仓库目录中的文件维护。仓库保留 `.original-build-93854/` 构建基线；不收录本机 `.tools/` 工具及 `.reference-*` 第三方参考检出。游戏存档不纳入此仓库。

## 实现说明

### 传送

只重排 `actinfo.txt` 中每幕的 `waypoint1` 至 `waypoint9`，不改动任务、怪物、地图碰撞或传送点物件，因此目的地保持原版落点和解锁逻辑。D2R 每幕传送点界面最多只有 9 个固定槽位，这种方式不会真正创建第 10 个以上的传送点。

### 崔凡克视野

替换高清场景显示文件，减少议会建筑的视觉遮挡；不删除怪物，不改变掉落或怪物 AI。

### 一键进地狱

在人物选择页增加透明点击区域，并向游戏发送地狱难度（难度编号 `2`）的载入指令。

### 快速退出

在两套高清暂停菜单（原版与恶君扩展布局）的背景层增加透明点击区域，并发送游戏原生的“保存并退出”指令；菜单中的原有按钮位于其上方，功能保持不变。

### 入口导航

入口提示和方向箭头只作用于高清游戏画面，不在小地图绘制箭头，也不揭开未探索地图。

入口使用共享的下层楼梯资源，因此憎恨囚牢第二层通往第三层、世界之石要塞第三层通往毁灭王座及采用相同资源的其他下层楼梯都会显示提示；提示不区分楼层号码，不改变入口点击范围或传送目标。崔凡克通往憎恨囚牢的入口保持原版显示。

箭头是静态高清场景资源：在 `nihln.json`、`nihle.json`、`nihls.json`、`nihlw.json` 四种地图布局中分别放置对应方向的粒子实体，游戏加载本局布局时自然加载对应箭头。这个实现说明不等于对战网使用或账号处罚作出保证，本项目仅用于离线角色。

资源参考自 [lukezord/d2r-advanced](https://github.com/lukezord/d2r-advanced)，固定提交与文件哈希记录在 `navigation-assets.json`。`build-navigation.py` 可从工程内 `.reference-d2r-advanced` 重建资源。参考场景不是从当前客户端重新提取的原文件，客户端更新后应提取新版四种场景并只迁移 `FarmHubNihlathakArrow*` 实体及其依赖。

### 大号符文音效

音效提取自本机 `E:\磨刀门MOD\MDM\MDM\MDM.mpq\Data\HD\Global\sfx\item\high_rune_26.flac` 至 `high_rune_33.flac`，逐文件保留原音频。范围为 26 Vex、27 Ohm、28 Lo、29 Sur、30 Ber、31 Jah、32 Cham、33 Zod；Ist/Gul 及以下仍为原版掉落声音。各音频长度不同，Ber 提示约 6.6 秒。

从 build 93854 客户端 CASC 中提取原版 `misc.txt`、`sounds.txt`，只修改八个符文的 `dropsound`，并在原声音表末尾追加八行专用音效记录及不冲突的 ID。拾取/使用声音 `usesound` 保留原版。没有导入磨刀门的符文模型、光柱、其他物品规则或完整数据表，不修改掉率。

`rune-audio-assets.json` 记录音频和表哈希、符文范围、原表哈希及音频时长；`build-rune-audio.py` 可用提取后的当前客户端原表和 MDM 资源重建。复查时可将已有大号符文从背包丢到地上确认音效，再检查实际怪物掉落。提示遵守游戏的声音距离与播放限制，不能保证所有远处掉落都听得到。

### 尸体与面板

- 尸体显示：`-assettestmode 1` 恢复墓碑为尸体，依赖该参数，不是新增模型替换文件。
- 已使用尸体：仅将 `states.txt` 中 `corpse_noselect`（ID 118）的 `hide` 改为 `1`。全地图生效；其他触发相同状态的已使用尸体也会隐藏。
- 面板边框：去除高清键鼠面板外侧边框及对应鼠标拦截区，保留面板锚点。

`build-farming-visibility.py` 和 `farming-visibility-assets.json` 记录构建方式、原文件及输出哈希。

### 战斗体能 / 战斗指挥提示（MDM3C 移植）

来源是本机 `E:\磨刀门MOD\MDM3C.7z`（作者：暗黑2阿檬），经维护者确认使用此版本。`E:\磨刀门MOD\MDM` 解压版没有这两个战吼的显示覆盖。只移植战斗指挥、战斗体能，不导入其他战吼、刺客集气或游戏数据表。

- 从当前客户端 CASC 提取 `data/hd/overlays/common/battlecommand.json`、`battleorders.json`，保存到 `.original-build-93854/`。`build-buff-labels.py` 以这两个文件为基础，仅替换 VFX 组件、加入 MDM3C 的 Transform 组件和更新对应粒子/贴图依赖；保留原文件其余字节及实体 ID。构建中用回退替换断言确认无额外改动。
- `buff_skill.particles`、`buff_hp.particles` 和 `buff_skillup_0000000.texture`、`buff_hpup_0000000000.texture` 与 MDM3C 逐字节一致。显示红色 `Skill ↑` / `HP ↑`，贴图中分别位于上部/下部。保留 MDM3C 的位置 `(122, 95, 116)`、单位缩放、单位四元数和 `inheritOnlyPosition: true`；不按场景单位猜测或重新换算这些坐标。
- 粒子唯一的活动采样器 `__sampler_0` 指向对应移植贴图。文件中其余 nickname 材质字符串是方向箭头模板残留的编辑器元数据；不因此覆盖共享的白色或 NPC 贴图。
- `states.txt` 中两个状态仍分别引用原版同名 overlay，buff 效果与持续时间不变。施放特效 `battlecommandcast`、`battleorderscast` 不改，组件 `hardKillOnDestroy: true` 用于状态结束时清理图标。角色、佣兵及其他获得相同状态的单位共享显示。
- `buff-labels-assets.json` 记录六个来源文件、两个客户端基线及六个输出文件的 SHA-256。四个旧 `farmhub_bc_skilltext` / `farmhub_bo_life_text` 贴图和粒子列入 `removedFiles`，构建和安装时清理。
- 重建：从 `MDM3C.7z` 解压上述六个来源文件，运行 `python build-buff-labels.py --source-root "解压路径/MDM3C/MDM3C.mpq"`。仅使用 Python 标准库；无需重新生成或编辑二进制贴图/粒子。
- `verify.ps1` 校验来源二进制一致性、输出和基线哈希、状态映射、Transform、贴图采样器及旧资源清理。本次只做静态检查，需游戏内确认大小、位置、两种状态分别获得/消失、死亡后清理及佣兵显示。

### 火蛇显示调整

只改高清显示，不改 `monstats.txt`、`skills.txt`、`missiles.txt` 等任何影响怪物行为的数据表。

- `data\hd\missiles\missiles.json`：原版把 `hydra` 飞弹映射到与法师火弹、骷髅法师、陷阱共用的 `firebolt` 模型。只把 `hydra` 一项改为原版 `icebolt` 模型（冰弹、冰系骷髅法师、青蛙也用它），火弹显示为青色；`firebolt`、`icebolt` 本身不变。伤害仍是火焰。
- `data\hd\character\enemy\hydra1`–`hydra3.json`：只保留 `entity_root`，删除 `entity_torso`（本体模型）、`entity_spine*_vfx`（身上火焰）和 `entity_vfx_decal`（地面焦痕）。依赖列表保持原样，动作文件可能仍会引用。
- 命中火花 `fireexplode`（高清 `fire_arrow_explode_2`）与火弹、火焰箭共用，不修改。
- `hydra1`–`hydra3` 也是法师九头蛇召唤的怪物，法师九头蛇在高清下同样显示。
- 把火蛇本体改成青色需要它的贴图（`data\hd\character\enemy\hydra1\textures\`）和身上火焰粒子的替代方案，目前未提取。
- `build-hydra-display.py` 先确认能逐字节复现原版紧凑 JSON 再写出；`hydra-display-assets.json` 记录原文件与输出哈希。

### 底材等级

只修改 `data\local\lng\strings\item-names.json` 中底材名称（键为 `armor.txt`/`weapons.txt` 的 `namestr`）的 `zhCN` 文字，在后面追加 `[普]`/`[扩]`/`[精]`。地面标签、未鉴定物品和所有品质都显示底材名，因此鉴定前即可看到。

- 等级：底材代码等于 `normcode`/`ubercode`/`ultracode` 时分别为普、扩、精。
- 规则由 `python build-item-labels.py rules <d2data 的 json/base 目录>` 生成 `item-label-rules.json`，数据来自 [blizzhackers/d2data](https://github.com/blizzhackers/d2data)，与 93854 原表一致。
- 名称文件由 `python build-item-labels.py` 从 `.original-build-93854/` 中的原版 `item-names.json` 生成；原版重新序列化后逐字节一致，因此只有底材名改变。`item-labels-assets.json` 记录哈希，`verify.ps1` 自动校验。
- 曾经尝试同时显示“有用孔数”，用户测试后要求只保留等级。
- 客户端更新后必须重新提取 `item-names.json` 再生成，旧文件会覆盖新版本的物品名称。

### 合并材料页

做法参考本机 MDM Mod（作者：暗黑2阿檬，适配 build 93854）：

- `bankexpansionlayouthd.json` 把全部 `AdvancedStashSlotWidget` 放进 `advancedstash_gems`，`advancedstash_materials`、`advancedstash_runes` 保留为空容器；第三个标签页的背景换成 `panel_bg_craft`。
- 自动重塑不使用 DLL：勾选框发送 `PanelManager:TogglePanel:CALL/mymodConvertAutoStart`，该面板用循环 `TimerWidget` 反复打开 `CALL/mymodConvert`，后者定时发送原生的 `BankPanelMessage:Convert` 后自行卸载。

与 MDM 的不同：

- 标签文字为“材料”。
- 重塑间隔由约 0.3 秒改为约 0.5 秒（`TRANSMUTE_INTERVAL = 0.4`，加上开始面板 0.1 秒的循环定时器）。v1.5.0 时为约 1 秒。
- `withdraw_button`（提取）移到屏幕外隐藏，不删除控件。
- 对齐 `ua1`–`ua5` 的横向位置，消除 MDM 中 8 像素的点击区重叠。
- 不带入 MDM 的自定义金币按钮、额外翻页箭头和方块下方重复的 7、8 号符文格。

重建：运行 `python build-stash-merge.py <MDM.mpq 路径>`，默认读取 `.reference-mdm/MDM.mpq`。源文件哈希记录在 `stash-merge-assets.json`。

`install.ps1` 会清理 `stash-merge-assets.json` 的 `removedFiles` 列出的早期试验资源（放大的个人、共享背景和 `bankoriginallayouthd.json`）。

只回退合并页：完全退出游戏后，删除安装目录 `mods\FarmHub\FarmHub.mpq` 下的 `data\global\ui\layouts\bankexpansionlayouthd.json`、`data\global\ui\layouts\CALL\` 和 `data\hd\global\ui\panel\stash\` 目录，即恢复原版三页。

## 自检

在工程根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\verify.ps1
```

脚本检查版本文件字节、模组清单 JSON、TSV 列数与映射、人物快速进入控件和指令、两张透明贴图的 SHA-256、两套暂停菜单的退出控件、崔凡克场景文件大小、导航和音效资源、尸体状态、面板边框、合并页格子与 `misc.txt` 的对应关系，以及自动重塑定时面板。

这是静态检查，不会启动游戏，也不能证明界面命中区域、场景显示或新客户端兼容性正确。通过后仍需要游戏内回归测试。

## 游戏更新后的必要维护

暴雪更新 D2R 后，本模组也需要同步检查。不要仅仅点击版本警告中的“继续”，因为客户端数据表结构或内容可能已经改变。

1. 启动一次未加载模组的游戏，确认客户端已完成更新。
2. 记录客户端显示的新数据版本号。
3. 从当前客户端重新提取最新版 `data\global\DataVersionBuild.txt`、`data\global\excel\` 下的 `actinfo.txt`、`misc.txt`、`sounds.txt`、`states.txt`，界面文件 `mainmenupanelhd.json`、`pauselayouthd.json`、`pauselayoutgardenhd.json`、`panelborderspanelhd.json`、`bankexpansionlayouthd.json`，名称文件 `data\local\lng\strings\item-names.json`，高清 `data\hd\missiles\missiles.json` 与 `data\hd\character\enemy\hydra1`–`hydra3.json`，以及崔凡克 `travn.json` 和四种 `nihl*.json`；同时确认新版 `states.txt` 中 `battleorders`、`battlecommand` 的 `overlay1` 和 `overlay.txt` 中的 `Character` 未变。
4. 以新版数据表为基础，重新应用传送点映射、符文音效和尸体状态改动；不要用旧表覆盖新版表。
5. 以新版界面和场景文件为基础，重新合并人物点击进入地狱、崔凡克通透布局和合并材料页；不要长期沿用旧版本的完整资源文件。
6. 确认 `DataVersionBuild.txt` 与客户端版本完全一致。
7. 运行 `verify.ps1`，通过后再启动模组，完成下方回归清单。

`DataVersionBuild.txt` 有严格格式要求：内容只能是版本号本身，必须使用纯 ASCII、无 BOM，并且末尾不能有空格或换行。例如 build 93854 的正确文件恰好是以下 5 个字节：

```text
39 33 38 35 34
```

如果弹窗中的“当前数据版本”和“检测到的数据版本”看起来相同，但仍提示不匹配，通常就是版本文件包含了隐藏的 BOM、回车或换行。弹窗句号被挤到下一行也是末尾换行的明显特征。

仅修改版本号只能消除版本检测警告，不能证明旧数据表、界面布局或场景资源与新客户端兼容。

## 文件与功能对应

下表中的资源路径均相对于 `mods\FarmHub\FarmHub.mpq`。

| 文件 | 职责与更新约束 |
| --- | --- |
| `modinfo.json` | 模组名称与共享存档路径；保留 `name: FarmHub`、`savepath: ../`，避免键位和存档目录发生切换。 |
| `data\global\DataVersionBuild.txt` | 数据版本标记；必须与目标客户端匹配，且无 BOM、空白和换行。 |
| `data\global\excel\actinfo.txt` | 第四幕刷宝点与其他幕返回映射；必须以新版原表为基础合并。 |
| `data\global\excel\misc.txt`、`sounds.txt` | 大符文掉落音效；更新客户端后重新提取原表合并。 |
| `data\global\excel\states.txt` | 隐藏已使用尸体。 |
| `data\global\ui\layouts\mainmenupanelhd.json` | 人物模型透明点击控件 `InvisibleHellStart`，载入指令为 `CharacterSelect:LoadCharacter:2`。 |
| `data\hd\global\ui\panel\message\QuickStart.sprite` | 高清全透明四帧按钮图集，提供原按钮结构与尺寸；不要换回带文字版本或直接删除。 |
| `data\hd\global\ui\panel\message\QuickStart.lowend.sprite` | 对应低配置全透明资源；应与高清版本一起维护、安装。 |
| `data\global\ui\layouts\pauselayouthd.json` | 原版高清暂停布局；背景控件 `FastExitBackground` 使用 `PausePanelMessage:ExitGame`。 |
| `data\global\ui\layouts\pauselayoutgardenhd.json` | 恶君扩展高清暂停布局；同样需要退出背景，并保留其原有功能按钮。 |
| `data\global\ui\layouts\panelborderspanelhd.json` | 去除面板外侧边框和鼠标拦截区，保留 `LeftAnchor`、`RightAnchor`。 |
| `data\hd\env\preset\act3\travincal\travn.json` | 崔凡克议会区域高清显示资源；保留通透显示改动，不修改地图碰撞和刷怪逻辑。 |
| `data\hd\roomtiles\*.json`、`data\hd\env\porory\beacon\` | 入口光柱、光圈与纹理。 |
| `data\hd\env\preset\expansion\wildtemple\nihl{n,e,s,w}.json`、`data\hd\directionarrows\` | 四种布局及方向箭头。 |
| `data\hd\nickname\textures\graphic\` | 两张兼容纹理，补齐粒子中残留的材质引用。 |
| `data\hd\overlays\common\battleorders.json`、`battlecommand.json` | MDM3C 红色 HP ↑ / Skill ↑ 提示；覆盖原版持续光圈。由 `build-buff-labels.py` 移植，依赖 `buff_hp` / `buff_skill` 粒子及对应贴图。 |
| `data\hd\directionarrows\particles\buff_{hp,skill}.particles`、`textures\buff_*up_*.texture` | MDM3C 原始战吼贴片粒子和贴图，逐字节复制；旧 `farmhub_bc_skilltext` / `farmhub_bo_life_text` 已退役。 |
| `data\hd\missiles\missiles.json`、`data\hd\character\enemy\hydra1`–`hydra3.json` | 火蛇本体不显示、火弹用冰弹外观；由 `build-hydra-display.py` 从原版生成，`missiles.json` 只改 `hydra` 一项。 |
| `data\local\lng\strings\item-names.json` | 底材名后的 [普]/[扩]/[精]；由 `build-item-labels.py` 从原版文件生成，只改 `zhCN`。 |
| `data\global\ui\layouts\bankexpansionlayouthd.json` | 合并页布局；全部 `AdvancedStashSlotWidget` 位于 `advancedstash_gems`，`advancedstash_materials` 和 `advancedstash_runes` 必须保留为空容器。 |
| `data\global\ui\layouts\CALL\mymodConvert*hd.json` | 自动重塑定时面板；面板 `name` 必须与勾选框消息和文件路径一致。 |
| `data\hd\global\ui\panel\stash\additionalstash\panel_bg_craft*.sprite` | 合并页背景，格子框已画在贴图中，移动格子时要同步修改；高清与 `lowend` 版本应一起维护。 |

## 不要重复引入的已知问题

- 只把人物按钮的 `textString` 设为空，不能隐藏贴图中烘焙的文字。当前两张 `QuickStart` 资源保留文件头和图集结构，像素数据全部清零。
- 不要把图集总宽度当作单帧宽度来计算点击区域。当前高清资源是四帧图集，单帧约 `658×1300`；曾经改成无贴图的 `400×198` 区域后，人物点击无法开局。
- 人物按钮保留 `filename: PANEL\\message\\QuickStart`、`hoveredFrame: 3` 和空 `textString`，不加入可见说明按钮或焦点提示图。
- 暂停菜单必须同时维护两套布局。仅修改 `pauselayouthd.json`，可能导致读取扩展布局的游戏完全没有变化。
- 透明退出背景必须位于菜单按钮下层。不要用顶层全屏热区盖住设置、返回游戏等按钮。
- 不要放大仓库面板或替换个人、共享页背景。早期试验采用过 1718×1801 的面板，留有大量空白；手动升级时若残留这些旧文件，面板会错位。
- 与其他模组冲突不只限于 `actinfo.txt`：人物选择界面、暂停布局、仓库界面、崔凡克场景或同名贴图被覆盖时，也需要合并。

## 更新、同步与发布流程

1. 备份存档、当前已安装 Mod 和本次需要修改的资源。
2. 先更新工程中的 `mods\FarmHub`，不要只修改游戏目录，避免下次安装覆盖修复。
3. 对照新版原始数据合并改动；如果版本号、表结构或透明贴图发生合法变化，同步更新 `verify.ps1` 的版本、结构或哈希预期。
4. 运行 `verify.ps1`，记录输出；关闭游戏后执行安装脚本：

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install.ps1 -D2RPath "E:\Diablo II Resurrected"
   ```

5. 安装脚本只覆盖文件，并清理脚本、`stash-merge-assets.json` 和 `buff-labels-assets.json` 中明确列出的退役资源。若本次删除或改名了其他文件，要把它们加入退役列表，不能删除存档。
6. 对本次修改的文件比较工程与安装目录的 SHA-256，确认资源确实同步。
7. 完全重启游戏，完成下方回归测试，再发布包含 `mods`、`docs`、`README.md`、`install.ps1`、`verify.ps1`、全部 `*-assets.json` 和 `build-*.py` 的新版本压缩包。
8. 更新 README 的变更记录和 `docs/DOWNLOADS.md`。历史 ZIP 内的 README 保持当时版本。

## 游戏内回归清单

- 启动无版本不匹配警告，离线角色、原键位与快速施法设置正常。
- 地狱已解锁角色点击模型可开局且无文字提示；普通/噩梦仍可由原按钮手动选择。
- 第四幕九个传送槽位正确，新增目的地遵守当前难度解锁状态，其他四幕可返回群魔堡垒。
- 崔凡克高清议会区域视野改善，怪物和原路线正常；看不到火蛇本体，火蛇的火弹显示为青色冰弹，法师火弹、骷髅法师等其他火弹正常显示。
- 地上的武器和护甲底材名后显示 [普]/[扩]/[精]，未鉴定和各品质物品都显示。
- 暂停菜单外点击保存退出；菜单内设置和返回按钮正常，日常点击不会触发退出。
- 分别检查原版与扩展暂停布局；检查高清/低配置资源及不同分辨率下人物点击区是否仍覆盖模型。
- 保存退出后重新开局，确认角色进度与掉落物品正常保存。
- 战斗指挥后角色和佣兵显示红色 Skill ↑，战斗体能后显示红色 HP ↑；同时存在时两行不重叠，位置与大小符合 MDM3C；分别等待 buff 结束及死亡后确认对应提示消失；吼叫施放特效正常。
- “材料”页显示既有的符文、宝石和材料数量；放入、取出、自动入库、方块合成、合成后保存重开都正常；个人和共享页可正常存取；勾选自动重塑后约每 0.5 秒重塑一次，取消勾选、关闭仓库或切换标签页后不再继续；过往赛季勾选框不与其他控件重叠。

## 验证记录

- 2026-11-07：经维护者确认移植 MDM3C 的 Skill ↑ / HP ↑；完整静态检查及重复构建一致性通过，游戏内显示待确认。
- 2026-10-30：用户确认当前工程全部功能的游戏内测试正常，包括合并材料页和自动重塑。
