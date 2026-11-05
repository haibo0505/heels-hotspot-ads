# 高跟鞋热点爆款广告

把真实热点、八大爆款元素和“说人话”编辑方法接成一条工作流，为高跟鞋抖音千川素材交付五条完整创意广告。需要AI制作时，可继续编译Seedance文本提示词。

## 能交付什么

每条包含热点来源与日期、关联逻辑、目标人群和SKU适配、元素组合、两版前三秒、20—30秒分镜、一整段自然口播、商品证明与购买引导、拍摄资源和互动文案。五条完成后，推荐优先试拍的两条及A/B测试方法。

热点来源优先高跟鞋，其次穿搭服装，再扩展全网。允许夸张联想，事实、商品参数与授权关系不能编造。“炸裂”是创意目标，不是流量或成交承诺。

## 安装

在项目根目录执行：

```bash
git clone https://github.com/haibo0505/heels-hotspot-ads.git .agents/skills/heels-hotspot-ads
```

全局使用可将整个文件夹安装到当前客户端的skills目录。下一轮对话调用；若客户端未刷新，重新打开聊天。

## 使用

```text
使用 $heels-hotspot-ads，围绕我提供的商品资料，找近期热点，
结合八大爆款元素写五条完整抖音广告，台词说人话。
不要编造价格、舒适性或明星背书。
```

```text
把这五条转成Seedance提示词，只引用我已提供的产品图。
若目标平台只能单次生成15秒，分成能衔接的两段。
```

在[业务上下文模板](references/business-context.md)或当前聊天中提供商品资料、客群、输出位置和历史创意。已有信息不重复索要，资料读不到时仍可交不依赖未知参数的母版。默认只写脚本，用户要求AI制作时再写生成提示词，不自动付费生成或投放。

## 热点数据

写作规则本身无第三方依赖。红狐取数助手需要Python 3.9+，只用标准库；实时查询另需网络及有效的`REDFOX_API_KEY`。从[红狐](https://redfox.hk/settings/api-keys?source=github)取得密钥后，通过你的安全环境配置，不能写进技能、命令参数、任务提示词或Git提交。

```bash
python -B scripts/fetch_hotspots.py --hours 24 --output outputs/redfox.json
```

脚本保留原始响应、去重记录、来源时间与平台分布，不自动完成事件识别、预测或广告创作。最多查询7天区间；接口边界和数据覆盖需核验。缺密钥、网络故障或无权限时，智能体应回退官方热榜和可核验网页，明确实际来源与更新时间。报告不会把异构平台热度直接相加，也不把标题分析说成评论区实证。

## 组合来源

核心方法已汇入本包，可独立使用；不强制安装其他Skill。原版可选：[八大爆款元素](https://github.com/haibo0505/bada-baokuan-yuansu)、[说人话](https://github.com/MrGeDiao/shuorenhua)、[Seedance提示词](https://github.com/dexhunter/seedance2-skill)。来源、参考版本与许可见[来源说明](references/sources.md)。

## 每周交付

可由用户授权后配置每周一北京时间09:00任务，执行`$heels-hotspot-ads`。Skill文件不会自行创建定时任务，也不包含任何商户的任务或账户标识。调度方式、运行条件和凭据访问取决于所在客户端。

## 验证

```bash
python -B -m unittest discover -s tests -v
```

测试验证缺凭据回退、API记录去重、字段保留与凭据反射脱敏，不访问真实API，不验证广告效果。

## 许可

[MIT License](LICENSE)，保留上游MIT声明。本仓库不携带商户私有商品资料、本地绝对路径、历史广告报告、密钥或定时配置。
