-- GK-KE L2-2 受控查询模板：SIM-QRY-AVG-DEPOSIT（日均存款）
-- 依据 C02 §3 QueryDefinition：LLM 只选择 queryId 与参数；模板由平台签署。
-- 依据 C07 §5：C001 日均真值 = 2,983,333.33 CNY。
-- simulationOnly: true   namespace: gk-ke/v1 SIM
--
-- 口径（不下推为杭银规定，仅本包模拟口径）：
--   日均存款 = Σ(每个业务日的客户名下 CNY 账户日终余额之和) / 区间天数
--   区间：左闭右开 [2026-09-01, 2026-10-01) → 30 天
--
-- 参数：
--   :customerId  稳定客户标识（不得以名称替代）
--   :fromDate    业务日（Asia/Shanghai），左闭
--   :toDate      业务日（Asia/Shanghai），右开
--
-- 安全约束：
--   仅返回已授权 scope 内的行；不接受调用方传入的原始 SQL/SPARQL 片段。
--   金额一律十进制字符串，禁止浮点聚合。

SELECT
    b.accountId                                   AS accountId,
    b.businessDate                                AS businessDate,
    SUM(CAST(b.closingBalance AS DECIMAL(20, 2))) AS dailyClosingTotal,
    b.currency                                    AS currency
FROM daily_balances b
JOIN accounts a
      ON a.accountId = b.accountId
WHERE a.customerId = :customerId
  AND a.currency   = 'CNY'                        -- CNY_ONLY 口径
  AND b.businessDate >= :fromDate
  AND b.businessDate <  :toDate                   -- 左闭右开
GROUP BY b.accountId, b.businessDate, b.currency
ORDER BY b.businessDate, b.accountId;
