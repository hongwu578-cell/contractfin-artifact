# SCI held-out预注册冻结审阅报告

- 协议：`contractfin-sci-finqa-test500-v1`
- 冻结日期：`2026-09-29`
- 冻结锁SHA-256：`090d7b4e71be4cbdf9fe41e9dd614953a2f7fe56de7a28c4d3b470f5f6414b40`
- 真实模型API调用：`0`
- 结论：**通过冻结审阅，可以作为后续held-out实验的唯一v1依据；当前仍未获得live授权。**

## 冻结前审阅发现及处理

1. 原gold评估文件缺少表格上下文，会使表格聚合程序无法复算。现已补入仅供后置评估使用的document/table上下文，推理runtime仍无gold路径。
2. 原主实验首运行系统顺序为244:256。现已改为严格250:250，并保持每题B0/B1相邻执行。
3. 原程序与执行准确率可能采用选择性分母。现已冻结为全500题ITT口径，缺失、无效或不可执行程序均计错。
4. 已补充100题稳定性实验的两轮调度：每轮首系统50:50，同一题在第2、3轮中交换首系统。
5. 已明确基础设施失败、系统输出失败和返回模型漂移的判定边界，并规定越阈值后必须在揭盲前停止。
6. live授权改为独立日期化修订文件，不修改已冻结runtime；授权文件必须绑定runtime哈希和实验范围。

## 冻结检查

| 检查项 | 结果 |
|---|:---:|
| `preregistration_status_is_frozen` | 通过 |
| `local_audit_passed` | 通过 |
| `primary_sample_is_500` | 通过 |
| `inference_contains_no_gold_fields` | 通过 |
| `gold_contains_execution_documents` | 通过 |
| `primary_runtime_is_not_authorized` | 通过 |
| `stability_runtime_is_not_authorized` | 通过 |
| `primary_first_order_is_250_250` | 通过 |
| `stability_first_order_is_50_50_per_replicate` | 通过 |
| `primary_test_is_two_sided_exact_mcnemar` | 通过 |
| `secondary_itt_denominators_are_frozen` | 通过 |
| `small_effect_power_at_500_is_at_least_80_percent` | 通过 |
| `B2_is_excluded_from_confirmation` | 通过 |
| `current_call_authorization_is_zero` | 通过 |

## 仍需在论文中主动声明的边界

- 研究仅使用FinQA，结论不能直接外推到全部金融任务、全部模型或全部多智能体系统。
- `deepseek-flash`是服务别名而非不可变模型快照；成对交错、返回模型记录和漂移阈值只能降低而不能完全消除该风险。
- 500题是带稀有运算最低配额的压力感知样本；未加权主效应对应这一预注册样本组合，FinQA全测试集总体效应仅作加权次要估计。
- B2结果来自开发集失败诊断，只能支持机制假设，不能作为held-out架构优劣的确证性证据。
- 稳定性子集的重复结果不与主实验合并做显著性检验。

## 变更规则

冻结锁所列任一文件发生变化，v1锁即失效。后续只能通过日期化、说明理由的修订文件变更；不得静默覆盖、替换样本或按结果调整分析。
