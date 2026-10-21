# 即時生產報告工作流

## 使用方式

管理员从左侧菜单进入 `/instant-production-report`：

1. 确认本次告警门槛。
2. 按「立即取得资料并生成」。
3. 系统通过既有唯读 MCP 即时读取 Odoo、MES、QMS、CMMS、WMS、PLM 与 SPC，并由本地有限产能排程引擎建立同一时间点的快照。
4. 固定公式计算计划达成率、FPY、OEE、预测准交率、延期订单、缺料、换线与停机时间。
5. JSON 快照与含来源引用的 PDF 会作为 NAS 资产保存到 `storage/production_reports/YYYY/MM/DD/instant-NNNNNN/`。
6. 报告完成后，可明确选择一个已核准 LINE 群组推送，或针对该份不可变快照向目前系统 LLM 追问。

即时报告与「每日生产报告」分开保存。同一天可以多次产生即时报告，每次都有独立编号、来源、工具轨迹、告警门槛和问答记录；每日生产报告仍维持每天一份与 18:00 定时器。

## 告警字段

| 字段 | 判断 |
| --- | --- |
| 生产计划达成率 | 低于下限时告警 |
| 一次通过率 FPY | 低于下限时告警 |
| OEE | 低于下限时告警 |
| 预测准交率 | 低于下限时告警 |
| 预计延期订单 | 高于上限时告警 |
| 缺料项目 | 高于上限时告警 |
| 停机与保养时间 | 高于上限时告警 |

门槛只用于该份快照的管理判断，不会写回企业系统。来源数据缺失时，对应 KPI 为 `N/A`，不会触发基于虚构数值的告警。

## 推送控制

- 只能选择 LINE 企业管理中已核准的群组。
- 默认启用「仅在触发告警时推送」。无告警时会记录为 skipped，不发送消息。
- 默认不自动对外发送。管理员可在生成前明确勾选「触发告警后自动推送」并指定群组，或在报告完成后按下推送按钮。
- 推送内容包含报告编号、时间、关键 KPI、告警、来源编号及返回报告页面的链接。
- 成功、失败、目标群组和时间会记录在报告资料表。

## 管理层追问

- LLM 只接收当前报告的不可变 JSON 快照，不重新读取实时系统，因此回答可重现。
- 系统提示要求来源使用 `[S1]` 格式，并把来源内容视为不可信数据而非指令。
- KPI 数字由固定公式产生，LLM 不得重算或改写。
- 问题、回答、模型、提问者、时间与来源目录会保存；模型调用也进入既有企业审计。

## API

- `POST /api/instant-production-reports`：即时取数并产生报告，可传入 `alert_rules`。
- `GET /api/instant-production-reports?limit=50`：列出历史报告。
- `GET /api/instant-production-reports/{id}`：读取报告、来源、推送状态和追问历史。
- `GET /api/instant-production-reports/{id}/download`：下载 PDF。
- `POST /api/instant-production-reports/{id}/push`：推送至已核准 LINE 群组。
- `POST /api/instant-production-reports/{id}/ask`：针对该份快照进行管理层追问。

所有页面与 API 目前均只限管理员。报告取数使用唯读 MCP，不修改 Odoo、MES、QMS、CMMS、WMS、PLM、SPC 或 PLC。

## 回退

移除即时报告页面、路由和左侧入口即可停用功能。保留 `instant_production_reports`、`instant_production_report_questions` 及 NAS 资产以维持审计记录；除非另有资料保留授权，不应自动删除历史 PDF、JSON 或问答。
