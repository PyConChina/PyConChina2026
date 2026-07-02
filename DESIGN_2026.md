# PyCon China 2026 — Design System (as-built)

> 主题: **AI for Good** · 视觉语言: brick-on-baseplate(乐高积木拼在波点底板上)+ 8-bit 像素
> 本文档描述**已实现**的设计系统(单一事实来源),供后续维护与 QA 验收对照。
> 历史: v1 曾用"白卡 + 硬位移投影"(neobrutalism),经 Frost 否决后重构为本方案。
> 维护: Rubick(设计/PM)· Arthas(实现)· Lina(QA)。重写于 2026-07-02(原稿曾遗失未入库)。

---

## 1. 核心隐喻与禁令

**内容是「积木」,拼在乐高底板上。** 立体感来自砖块的"塑料厚度"(同色更深的底边),不是投影。

禁令(违者即回退):
- 禁 `backdrop-filter` / 毛玻璃、紫色渐变(v1 遗产,也是 AI-slop 默认款)
- 禁面板/砖块用对角硬位移投影(`box-shadow: Npx Npx 0 ink`)——那是 neobrutalism
- 禁像素字体加粗:Press Start 2P / Zpix 均单一字重,任何 700 触发浏览器合成加粗即糊。
  所有像素字 `font-weight: 400` + `font-synthesis: none`;CJK 像素标题描边最多 1px
- 显示大标题**允许**位移 `text-shadow`(街机文字深度,与面板投影是两回事)

## 2. 颜色 Tokens(`pycon/static/css/pycon.css` `:root`)

```css
--bg-base: #3daa84;    /* 底板绿(设计稿采样) */
--bg-dot: #4fb089;     /* 底板圆点 */
--bg-deep: #2a7f61;    /* footer 深绿; 从 #2e8c6b 调深使白字过 AA (4.88) */
--paper: #ffffff;  --paper-muted: #edf8f3;
--ink: #1a1a1a;    --ink-soft: #3a3a3a;    --gray-pixel: #9e9e9e;
--py-yellow: #f9ca33;  --py-orange: #f19640;  --py-redhot: #e27344;
--py-red: #ec4567;     --py-pink: #b6316c;    --py-purple: #8312dc;
--py-indigo: #424990;  --py-blue: #149ada;    --py-green: #75be4e;
--accent: #0e6c9e;             /* 链接/强调: Python 蓝 (白底 AA 5.74) */
--accent-bright: var(--py-blue);  /* hover/focus */
```

## 3. 对比度规则(实测 WCAG,强制)

| 场景 | 规则 | 实测 |
|---|---|---|
| 亮砖(yellow/orange/redhot/red/blue/green)上的文字 | **ink** | 4.65–11.21 AA |
| 暗砖(pink/purple/indigo)上的文字 | **white**(`--brick-on-dark`) | 5.76–8.12 AA |
| `--accent` 蓝文字 | **只允许在 paper/paper-muted 上**(5.74/5.28);任何彩砖/底板上都 FAIL(1.19–3.70) | |
| `--ink-soft` 次级文字 | 只在 paper/yellow/green 上过 AA;蓝/红砖上必须用全 ink | |
| 直接压底板的链接 | ink + `text-decoration-color: var(--py-yellow)`(accent 压底板仅 1.99) | 6.03 AA |
| footer(`--bg-deep`)上文字 | white | 4.88 AA |

实现模式:组件轮转砖色时,同步定义文字 token,不要写死颜色:
```css
.member { --brick-color: var(--paper); --on-strong: var(--accent); --on-soft: var(--ink-soft); }
.member:nth-child(5n+2) { --brick-color: var(--py-yellow); --on-strong: var(--ink); --on-soft: var(--ink); }
/* .role { color: var(--on-strong); }  .bio { color: var(--on-soft); } */
```
共享组件(如 `.card-header`)一律用 `var(--brick-on)`,不硬编码 ink/white。

## 4. 字体

| 层 | 字体 | 用途 |
|---|---|---|
| Display 像素 | Press Start 2P(Latin)+ Zpix(CJK),自托管 `pycon/static/fonts/` | 大标题/kicker/导航品牌,**仅短文本** |
| Body | AlibabaPuHuiTi(400/700)+ system fallback | 正文/卡片/表格 |

全部 `font-display: swap`。像素字禁加粗(见 §1)。

## 5. 组件语言

- **砖块**(`.card` 等):实色面 + 顶部高光渐变 + **同色深底边**
  `box-shadow: 0 var(--brick-depth) 0 color-mix(in srgb, var(--brick-color) 68%, #000)`
  + studs 凸点(`::before` repeating radial-gradient,`aria-hidden` 性质的纯装饰)。
  hover = 拎起(`translateY(-3px)` + 底边加深);active = 按下(底边收缩 + `translateY(2px)`)。
- **导航** = 波点底板上的**便利贴 tab**:五色 pastel 轮转、±2° 交替倾斜、hover 扶正抬起、
  中性阴影 `rgba(26,26,26,.22)`;导航条本体 = 波点底板(无白卡、无投影——白色导航条是被否决的旧方案)。
- **小按钮/chip**(talk meta、staff 邮箱等):透明底 + `2px` ink 描边 + ink 内容;
  实心 CTA 用品牌色小砖(如 生成海报 = 黄砖)。焦点环用 **ink**(白环在白卡上不可见)。
- **四角装饰**:`base.html` 的 `.page-shell{position:relative}` 内四个 SVG 精灵
  (`pycon/static/images/decor/corner-*.svg`,矢量透明,由脚本生成),
  `position:absolute` 贴边(offset 0)、`z-index:1`、`pointer-events:none`、≤700px 隐藏。
  **风格 = banner 参考图的扁平像素风**(2026-07-02 对齐):积木 = 扁平色块 + 顶部小方块 studs +
  底部深色条,**无描边**;黄色四分之一圆"管道"角块;蛇 = 连续粗折线 S 身 + 浅色虚线花纹 + 方块头。
  禁止卡通描边/光泽风(被 Frost 否决的旧版)。
- **Banner 标题逐字配色**(从 banner 采样):P红 Y黄 C蓝 O米黄(#f5dc85) N紫 / C紫 H蓝 I黄 N红 A米黄;
  "2026" 灰 #adb0b5 + 浮雕(亮左上/暗右下 text-shadow);字母 8 向 3px ink 黑描边 + 柔和投影(Frost 2026-07-02 定版;曾试无描边被否)。
- **日程表**:boundary-index 网格——当天所有 start/end 去重排序 → 行号;
  `grid-auto-rows: minmax(104px, auto)`(行高不按时长正比);房间表头 `grid-row:1`;
  主会场 `grid-column: 1 / -1`;蓝砖 item 上时间标签用 ink。
- **焦点**:全局 `:focus-visible` 3px `--py-blue` 环;压蓝/白背景处按上文改 ink/paper。
- **动效**:统一 `var(--ease-ui)`(180ms);`prefers-reduced-motion: reduce` 全量降级。

## 6. QA 验收清单(Lina)

- [ ] 无 `backdrop-filter`/紫色渐变/对角硬投影回归;像素字无 700 字重
- [ ] §3 对比度规则逐项 computed 抽查(尤其彩砖上的次级文字与链接)
- [ ] 砖块 hover/active、便利贴扶正、焦点环在各底色上可见
- [ ] 四角装饰贴边、不挡内容、移动端隐藏;无横向溢出(三档 viewport)
- [ ] 日程:表头行/主会场跨列/同刻对齐/最小行高;项目文字不重叠
- [ ] `manage.py check` + `pdm run build` 通过(既有 Treebeard/W042 警告除外)
- [ ] 改样式必升 `?v=` cache-bust

## 7. 已知坑(修过的,别再犯)

1. 源码有规则 ≠ 生效:多列布局里 `width:100%` 不跨列(要 `column-span`/单列);
   `.wall .item { --brick-color: paper }`(0-2-0)会盖过 `.brick-yellow`(0-1-0)。**一律浏览器 computed 验证。**
2. 全局 `button:not(.a):not(.b)` 特异性是 (0,2,1),会压过页面单类规则(曾致搜索按钮 44px vs 输入框 48px)。
3. 装饰 `z-index:-1` 会被不透明 section 背景整体盖住。
4. `elementFromPoint` 打在 SVG 透明区会命中底层元素,判"可见"要看渲染/实心处。
5. 原型/演示数据不可直接上线(曾把占位英文硬编码进首页);内容一律走 CMS + i18n。
6. `Staff` 模型无 email 字段;staff 卡邮箱按钮曾是 `href="#"` 死链(处置待 Frost 决策)。
7. 全局 `a:hover { color: accent-bright }` 会泄漏进组件链接(曾致蓝色便签 hover 文字蓝压蓝不可见)。
   现已收窄为 `a:not([class]):hover`(只作用于 richtext 无类链接);**组件型 `<a>` 必须带 class 并自管颜色**。
