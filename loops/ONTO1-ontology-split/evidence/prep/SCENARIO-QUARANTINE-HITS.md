# 场景资产内的隔离别名｜待裁清单

> **不得自行映射**：这些别名属 `QUARANTINED_UNRESOLVED`，语义归属须由 Owner / 数据 Owner 裁定。

| 别名 | 文件 | 处 | 上下文（节选） |
|---|---|---|---|
| `CASH_MANAGEMENT` | `apps/api/src/test/java/com/gien/gits/api/controller/ProductKnowledgeVersionControllerTest.java` | 30 | `"集团现金池", "CASH_MANAGEMENT", "desc",` |
| `CASH_MANAGEMENT` | `apps/api/src/test/java/com/gien/gits/api/controller/ProductKnowledgeVersionControllerTest.java` | 66 | `when(versionService.findByCategory("CASH_MANAGEMENT")).thenReturn(List.of(samp` |
| `CASH_MANAGEMENT` | `apps/api/src/test/java/com/gien/gits/api/controller/ProductKnowledgeVersionControllerTest.java` | 67 | `mockMvc.perform(get("/api/v1/product-knowledge").param("category", "CASH_MANAG` |
| `CASH_MANAGEMENT` | `apps/api/src/test/java/com/gien/gits/api/productknowledge/ProductInterpretationControllerTest.java` | 39 | `product_family: CASH_MANAGEMENT` |
| `CASH_MANAGEMENT` | `apps/api/src/test/java/com/gien/gits/api/service/ProductKnowledgeVersionServiceTest.java` | 25 | `"集团现金池", "CASH_MANAGEMENT", "desc",` |
| `CASH_MANAGEMENT` | `apps/api/src/test/java/com/gien/gits/api/service/ProductKnowledgeVersionServiceTest.java` | 51 | `when(repo.findByCategory("CASH_MANAGEMENT")).thenReturn(List.of(sample));` |
| `CASH_MANAGEMENT` | `apps/api/src/test/java/com/gien/gits/api/service/ProductKnowledgeVersionServiceTest.java` | 52 | `assertThat(service.findByCategory("CASH_MANAGEMENT")).hasSize(1);` |

- 合计 **7** 处 / **1** 个别名 / **3** 个文件

## 代码级佐证（本轮实测，供裁定参考，**不构成裁定**）

- `ProductKnowledgeVersionControllerTest.java` 用 `findByCategory("CASH_MANAGEMENT")` ⇒ 该值在代码中作**类别**使用；
- `ProductKnowledgeVersionServiceTest.java` 夹具为 `"集团现金池", "CASH_MANAGEMENT", "desc"` ⇒ `CASH_MANAGEMENT` 是**产品族/类别**，而 `集团现金池` 才是产品名；
- 因此把它映射为产品实例（如 `prod_cm_001`）**可能有害**；最终裁定见 `待人类-3`。

## 处置（未裁定前）

1. 场景开发中**照原样使用**这些字符串（不要替换、不要注释掉）；
2. 若该场景功能依赖其语义，**先标注 `PENDING_D2_RULING`**，不要自行归类；
3. 裁定后由 TL 按结果更新（`product-alias-resolution.json` 或登记为类别）。

