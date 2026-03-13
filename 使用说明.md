# A股市场数据 Skill 使用说明

这个仓库提供了一个给 OpenClaw 使用的 skill，内部名是 `ashare`，用于通过 AKShare 查询 A 股市场数据、指数、开放式基金、宏观数据和财经快讯。

## 目录结构

- `skills/ashare/SKILL.md`
  - OpenClaw 读取的技能定义文件
- `skills/ashare/scripts/query_akshare.py`
  - 实际执行 AKShare 查询的脚本入口
- `skills/ashare/references/datasets.md`
  - 自然语言请求到脚本子命令的映射说明

## 使用前提

在使用这个 skill 之前，确保机器上已经具备下面两个条件：

1. 已安装 OpenClaw，并且当前工作区会加载 `skills/` 目录下的本地 skills。
2. 已安装 Python，并且能直接执行 `python`。

如果还没有安装 `akshare`，先执行：

```bash
python -m pip install akshare --upgrade
```

## 如何放到 OpenClaw 工作区

把整个仓库作为 OpenClaw workspace 使用即可，或者把 `skills/ashare/` 这个目录复制到你自己的 OpenClaw workspace 的 `skills/` 目录下。

最终目录应类似这样：

```text
your-workspace/
  skills/
    ashare/
      SKILL.md
      scripts/
      references/
```

## 如何触发这个 Skill

这个 skill 有两种常见用法。

### 1. 通过自然语言自动触发

直接向 OpenClaw 提问，例如：

- `今天 A 股市场怎么样？`
- `平安银行现在多少钱？`
- `沪深300最近3个月走势如何？`
- `华夏成长混合最近净值怎么样？`
- `最近 10 条财联社快讯`
- `帮我看一下最新 PMI 数据`

如果模型判断你的问题属于这个 skill 的范围，它会自动调用 `ashare`。

### 2. 通过 slash command 显式触发

由于这个 skill 的内部名是 `ashare`，所以可以直接用：

```text
/ashare 平安银行现在多少钱
/ashare 今天A股市场概况
/ashare 沪深300最近3个月走势
/ashare 最近10条财联社快讯
```

## 支持的数据范围

当前版本支持下面这些能力：

- A 股市场概览
- A 股个股实时行情
- A 股个股历史走势
- A 股个股基础信息
- A 股指数实时行情
- A 股指数历史走势
- 开放式基金净值和历史净值
- 中国宏观指标
- 宏观日历
- 财联社快讯

当前版本不支持：

- 港股、美股、期货、期权
- 任意 AKShare 接口透传
- 自动安装 Python 或 AKShare

## 脚本直调方式

如果你想先不通过 OpenClaw，而是在终端里直接验证这个 skill 的数据能力，可以直接运行脚本：

```bash
python skills/ashare/scripts/query_akshare.py market-overview
python skills/ashare/scripts/query_akshare.py stock-quote 000001
python skills/ashare/scripts/query_akshare.py stock-quote 平安银行
python skills/ashare/scripts/query_akshare.py stock-history 600519 --limit 30
python skills/ashare/scripts/query_akshare.py index-history 000300 --limit 60
python skills/ashare/scripts/query_akshare.py fund-history 000001 --indicator unit_nav --limit 30
python skills/ashare/scripts/query_akshare.py macro-series china_pmi --limit 12
python skills/ashare/scripts/query_akshare.py macro-calendar --date 20260313 --limit 10
python skills/ashare/scripts/query_akshare.py news-flash --limit 10
```

脚本输出是统一的 JSON 结构，核心字段包括：

- `ok`
- `dataset`
- `resolved`
- `params`
- `columns`
- `rows`
- `row_count`
- `truncated`
- `as_of`

## 常见问题

### 1. 提示缺少 `akshare`

执行：

```bash
python -m pip install akshare --upgrade
```

### 2. slash command 没触发

确认下面几点：

- OpenClaw 当前打开的是这个仓库，或者 skill 已经被复制到你的 workspace 的 `skills/` 目录
- `skills/ashare/SKILL.md` 存在
- skill 内部名是 `ashare`，所以命令应写成 `/ashare`

### 3. 返回 `ambiguous_symbol`

这表示你输入的名称匹配到了多个证券或基金。此时改用更精确的名称，或者直接使用代码，例如：

- `000001`
- `600519`
- `000300`

### 4. 日期格式报错

脚本要求日期格式是 `YYYYMMDD`，例如：

- `20260313`
- `20260101`

不要写成：

- `2026-03-13`
- `2026/03/13`

## 给维护者的建议

如果后续要继续扩展这个 skill，优先看这两个文件：

- `skills/ashare/SKILL.md`
- `skills/ashare/references/datasets.md`

如果要新增数据源，建议同步更新：

1. `query_akshare.py` 的 CLI 子命令
2. `datasets.md` 的映射说明
3. 相关测试
