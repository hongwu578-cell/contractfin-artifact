# B2-v1.1 修订与预注册说明

## 状态

B2-v1.1 已完成失败诊断、实现修订和纯本地验证，尚未调用真实模型 API。下一步只能执行单独授权的三题真实接口门槛；在该门槛通过之前，不得运行 30 题重测或任何消融实验。

## B2-v1 失败诊断

B2-v1 完整架构对预注册 30 题执行了精确的 180 次模型调用和 60 次工具调用，工具零失败，但只有 27 题完整成功：

| 失败类型 | 数量 | 根因 |
|---|---:|---|
| `accept` 与检查项/原因码矛盾 | 2 | JSON 字段合法，但跨字段语义不变量不成立；v1 将其作为整题错误 |
| Verifier 在输出上限处中断 | 1 | 前序 Contract 与 Solver 分别消耗 13,986 和 16,311 输出 tokens，只给 Verifier 留下 1,709 |

检索、计算器、样本顺序、日志完整性和零重试约束均不是失败原因。

## v1.1 的三项实质修订

### 1. 保守的 Verifier 规范化

控制器先保存 `verifier_raw_verdict`，再形成独立的有效 verdict：

- 只有四项检查全部为真且原因码为空时，`accept` 才保持不变；
- `accept` 只要带有假检查或原因码，就确定性降级为 `human_review`；
- `human_review` 缺少原因码时，由控制器补充明确的机器原因码；
- 规范化过程记录在 `verifier_normalization` 中；
- 控制器绝不修改候选答案或程序，也绝不把人工复核提升为接受。

这会把原来的接口错误转化为显式、可审计的保守拒答，而不是掩盖为正确答案。

### 2. 固定角色输出预算

每题总上限仍为 32,768，与 B1 的比较边界保持不变，但不再允许前序角色占用全部剩余预算：

| 回合 | 上限 tokens |
|---|---:|
| Contract | 8,192 |
| Evidence 工具请求 | 1,024 |
| Evidence 最终输出 | 2,048 |
| Solver 工具请求 | 8,192 |
| Solver 最终输出 | 2,048 |
| Verifier | 11,264 |
| **合计** | **32,768** |

每次调用日志新增 `requested_max_output_tokens`，从而可以核验实际请求是否遵守分配。

### 3. 精简提示约束

Contract、Solver 和 Verifier 均新增“直接完成结构化任务、不要叙述或延长分析”的指令；Solver 的工具回合被明确要求直接调用计算器。模型、工具、检索器、计算器、评估器、温度/推理默认值和重试次数均未改变。

## 本地验证结果

| 验证项 | 结果 |
|---|---:|
| 单元测试 | 59/59 通过 |
| Python 字节码编译 | 通过 |
| 30 题模拟编排 | 30/30 成功 |
| 模拟模型/工具调用 | 180 / 60 |
| 模拟工具失败 | 0 |
| 运行时 gold 字段泄漏 | 0 |
| 固定预算序列与总和 | 通过 |
| 两类矛盾 `accept` 保守降级 | 通过 |
| 合法 `accept` 保持不变 | 通过 |

本地验证不能证明真实模型在单回合上限内一定完成。旧 APD 样本的 Contract 和 Solver 历史输出均高于新单回合上限，因此它必须进入真实接口门槛；若任一前序角色在新上限处中断，门槛即失败，不能进行 30 题重测。

## 三题真实接口门槛

门槛样本不是新抽样，而是 B2-v1 的全部三个失败样本，按原运行顺序冻结：

1. `finqa:dev:LMT/2012/page_47.pdf-3`：矛盾 Verifier verdict；
2. `finqa:dev:APD/2018/page_59.pdf-1`：输出预算耗尽；
3. `finqa:dev:LKQ/2016/page_26.pdf-2`：矛盾 Verifier verdict。

通过条件为 3/3 结构化完成、18 次模型调用、6 次工具调用、工具零失败、无输出上限或传输超时、三份结果顺序一致且日志完整度为 1.0。准确率、人工复核率和 Verifier 规范化率均不是门槛。

计划命令：

```text
PYTHONPATH=src python3 scripts/run_b2.py --provider deepseek --model deepseek-flash --variant full --sample-manifest config/b2_finqa_dev_v1_1_interface_manifest.json --protocol-id contractfin-b2-finqa-dev3-interface-v1.1 --total-output-budget 32768 --max-model-calls 6 --max-tool-calls 2 --request-timeout-seconds 300 --artifact-stem b2_deepseek_full_interface3_v1_1
```

该门槛最多调用模型 18 次，不含自动重试。只有门槛通过后，才可另行授权 B2-v1.1 完整架构 30 题重测；消融实验仍未解锁。

授权该门槛的准确回复是：

> 同意执行B2-v1.1三题真实接口测试，最多18次模型调用。

## 审计产物

- `config/b2_finqa_dev_v1_1_amendment.json`
- `config/b2_finqa_dev_v1_1_interface_manifest.json`
- `reports/b2_v1_1_failure_diagnostic.json`
- `reports/b2_v1_1_local_orchestration_audit.json`
