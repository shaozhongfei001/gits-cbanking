package com.gien.gits.knowledge.gkke.plan;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.knowledge.gkke.model.Budget;
import com.gien.gits.knowledge.gkke.model.TaskContextRecord;
import com.gien.gits.knowledge.gkke.permission.PermissionContext;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G4 任务上下文测试（C06 §2 TaskContext：驱动地图选择与权限过滤）。
 */
class TaskContextTest {

    private final ObjectMapper mapper =
            new ObjectMapper().configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

    @Test
    @DisplayName("TaskContext JSON 完整反序列化为 record")
    void deserializeTaskContext() throws Exception {
        String json = """
                {
                  "tenantId": "TENANT-CBANK",
                  "orgIds": ["ORG-001"],
                  "customerIds": ["CUS-001"],
                  "purpose": "INTERPRETATION",
                  "channel": "RM_WORKBENCH",
                  "conversationId": "CONV-001",
                  "taskId": "TASK-PREVISIT-001",
                  "taskType": "PRODUCT_EXPLAIN",
                  "requiredAssetClasses": ["FOUNDATIONAL_DATA", "KNOWLEDGE_RULE"],
                  "budget": {"maxSteps": 8, "maxTokens": 8000, "timeoutMs": 30000}
                }
                """;

        TaskContextRecord context = mapper.readValue(json, TaskContextRecord.class);

        assertThat(context.tenantId()).isEqualTo("TENANT-CBANK");
        assertThat(context.orgIds()).containsExactly("ORG-001");
        assertThat(context.customerIds()).containsExactly("CUS-001");
        assertThat(context.purpose()).isEqualTo("INTERPRETATION");
        assertThat(context.channel()).isEqualTo("RM_WORKBENCH");
        assertThat(context.taskType()).isEqualTo("PRODUCT_EXPLAIN");
        assertThat(context.requiredAssetClasses())
                .containsExactly("FOUNDATIONAL_DATA", "KNOWLEDGE_RULE");
        assertThat(context.budget()).extracting(Budget::maxTokens).isEqualTo(8000);
    }

    @Test
    @DisplayName("TaskContext 可派生运行时 PermissionContext（scope + purpose 传递）")
    void derivePermissionContext() {
        TaskContextRecord task = new TaskContextRecord("TENANT-CBANK",
                java.util.List.of("ORG-001"), java.util.List.of("CUS-001"), "RECOMMENDATION",
                "API", "CONV-1", "TASK-1", "COMPARISON",
                java.util.List.of("FOUNDATIONAL_DATA"), new Budget(4, 4000, 15000L));

        PermissionContext permission = new PermissionContext(task.tenantId(), task.orgIds(),
                task.customerIds(), task.purpose());

        assertThat(permission.tenantId()).isEqualTo("TENANT-CBANK");
        assertThat(permission.orgIds()).containsExactly("ORG-001");
        assertThat(permission.customerIds()).containsExactly("CUS-001");
        assertThat(permission.purpose()).isEqualTo("RECOMMENDATION");
    }
}
