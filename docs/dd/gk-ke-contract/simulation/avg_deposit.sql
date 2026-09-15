-- Reference query. balance_cents is an INTEGER materialized from decimal strings.
-- Service must execute the contract prechecks BEFORE this query.
-- authorizedOrgId MUST be injected by authenticated server-side policy.
SELECT SUM(b.balance_cents) AS totalBalanceCents,
       COUNT(*) AS accountDayCount,
       COUNT(DISTINCT a.accountId) AS accountCount
FROM account_day_cents b
JOIN accounts a ON a.accountId = b.accountId
JOIN customers c ON c.customerId = a.customerId
WHERE c.customerId = :customerId
  AND c.orgId = :authorizedOrgId
  AND b.businessDate >= :periodFrom
  AND b.businessDate < :periodTo
  AND b.snapshotId = :snapshotId;
