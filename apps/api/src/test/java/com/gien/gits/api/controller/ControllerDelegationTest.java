package com.gien.gits.api.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.gien.gits.action.domain.RecordingConsent;
import com.gien.gits.action.domain.Task;
import com.gien.gits.api.service.CommitmentService;
import com.gien.gits.api.service.ExternalEventService;
import com.gien.gits.api.service.OpportunityService;
import com.gien.gits.api.service.ProductKnowledgeVersionService;
import com.gien.gits.api.service.RecordingConsentService;
import com.gien.gits.api.service.TaskService;
import com.gien.gits.ontology.Commitment;
import com.gien.gits.ontology.ExternalEvent;
import com.gien.gits.ontology.domain.Opportunity;
import com.gien.gits.ontology.domain.ProductKnowledgeVersion;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

/**
 * P24: 轻量委托 Controller 的纯单元测试（不启动 Spring 上下文）。
 * 覆盖 Task/Commitment/Opportunity/ProductKnowledgeVersion/RecordingConsent/ExternalEvent 六个控制器的全部分支。
 */
class ControllerDelegationTest {

    @Test
    void taskController_coversAllEndpointsAndBranches() {
        TaskService service = mock(TaskService.class);
        TaskController controller = new TaskController(service);
        Task task = mock(Task.class);
        when(service.findById("T-1")).thenReturn(Optional.of(task));
        when(service.findById("missing")).thenReturn(Optional.empty());
        when(service.findByInteractionId("I-1")).thenReturn(List.of(task));
        when(service.findByCustomerId("C-1")).thenReturn(List.of(task));
        when(service.findByOperatingCaseId("O-1")).thenReturn(List.of(task));
        when(service.findByAssignedTo("RM-1")).thenReturn(List.of(task));
        when(service.findAll()).thenReturn(List.of(task));
        when(service.findOverdue()).thenReturn(List.of(task));
        when(service.create(task)).thenReturn(task);
        when(service.updateStatus("T-1", "DONE")).thenReturn(Optional.of(task));
        when(service.updateStatus("T-2", "DONE")).thenReturn(Optional.empty());

        assertSame(task, controller.getById("T-1").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.getById("missing").getStatusCode());
        assertEquals(List.of(task), controller.list("I-1", null, null, null).getBody());
        assertEquals(List.of(task), controller.list(null, "C-1", null, null).getBody());
        assertEquals(List.of(task), controller.list(null, null, "O-1", null).getBody());
        assertEquals(List.of(task), controller.list(null, null, null, "RM-1").getBody());
        assertEquals(List.of(task), controller.list(null, null, null, null).getBody());
        assertEquals(List.of(task), controller.getOverdue().getBody());
        assertEquals(HttpStatus.CREATED, controller.create(task).getStatusCode());
        assertSame(task, controller.updateStatus("T-1", "DONE").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.updateStatus("T-2", "DONE").getStatusCode());

        verify(service).findByOperatingCaseId("O-1");
        verify(service).findByAssignedTo("RM-1");
    }

    @Test
    void commitmentController_coversAllEndpointsAndBranches() {
        CommitmentService service = mock(CommitmentService.class);
        CommitmentController controller = new CommitmentController(service);
        Commitment commitment = mock(Commitment.class);
        when(service.findById("CM-1")).thenReturn(Optional.of(commitment));
        when(service.findById("missing")).thenReturn(Optional.empty());
        when(service.findByInteractionId("I-1")).thenReturn(List.of(commitment));
        when(service.findByCustomerId("C-1")).thenReturn(List.of(commitment));
        when(service.findByStatus("OPEN")).thenReturn(List.of(commitment));
        when(service.findAll()).thenReturn(List.of(commitment));
        when(service.findOverdue()).thenReturn(List.of(commitment));
        when(service.create(commitment)).thenReturn(commitment);
        when(service.updateStatus("CM-1", "DONE", "RM-1")).thenReturn(Optional.of(commitment));
        when(service.updateStatus("CM-2", "DONE", null)).thenReturn(Optional.empty());

        assertSame(commitment, controller.getById("CM-1").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.getById("missing").getStatusCode());
        assertEquals(List.of(commitment), controller.list("I-1", null, null).getBody());
        assertEquals(List.of(commitment), controller.list(null, "C-1", null).getBody());
        assertEquals(List.of(commitment), controller.list(null, null, "OPEN").getBody());
        assertEquals(List.of(commitment), controller.list(null, null, null).getBody());
        assertEquals(List.of(commitment), controller.getOverdue().getBody());
        assertEquals(HttpStatus.CREATED, controller.create(commitment).getStatusCode());
        assertSame(commitment, controller.updateStatus("CM-1", "DONE", "RM-1").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.updateStatus("CM-2", "DONE", null).getStatusCode());
    }

    @Test
    void opportunityController_coversAllEndpointsAndBranches() {
        OpportunityService service = mock(OpportunityService.class);
        OpportunityController controller = new OpportunityController(service);
        Opportunity opportunity = mock(Opportunity.class);
        when(service.findById("OP-1")).thenReturn(Optional.of(opportunity));
        when(service.findById("missing")).thenReturn(Optional.empty());
        when(service.findByCustomerId("C-1")).thenReturn(List.of(opportunity));
        when(service.findByStatus("OPEN")).thenReturn(List.of(opportunity));
        when(service.findByOpportunityType("TRADE")).thenReturn(List.of(opportunity));
        when(service.findByAssignedTo("RM-1")).thenReturn(List.of(opportunity));
        when(service.findActiveByCustomerId("C-1")).thenReturn(List.of(opportunity));
        when(service.findAll()).thenReturn(List.of(opportunity));
        when(service.create(opportunity)).thenReturn(opportunity);
        when(service.updateStatus("OP-1", "WON")).thenReturn(Optional.of(opportunity));
        when(service.updateStatus("OP-2", "WON")).thenReturn(Optional.empty());

        assertSame(opportunity, controller.getById("OP-1").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.getById("missing").getStatusCode());
        assertEquals(List.of(opportunity), controller.getByCustomerId("C-1").getBody());
        assertEquals(List.of(opportunity), controller.getByStatus("OPEN").getBody());
        assertEquals(List.of(opportunity), controller.getByType("TRADE").getBody());
        assertEquals(List.of(opportunity), controller.getByAssignedTo("RM-1").getBody());
        assertEquals(List.of(opportunity), controller.getActiveByCustomerId("C-1").getBody());
        assertEquals(List.of(opportunity), controller.listAll().getBody());
        assertEquals(HttpStatus.CREATED, controller.create(opportunity).getStatusCode());
        assertSame(opportunity, controller.updateStatus("OP-1", "WON").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.updateStatus("OP-2", "WON").getStatusCode());
    }

    @Test
    void productKnowledgeVersionController_coversAllEndpointsAndBranches() {
        ProductKnowledgeVersionService service = mock(ProductKnowledgeVersionService.class);
        ProductKnowledgeVersionController controller = new ProductKnowledgeVersionController(service);
        ProductKnowledgeVersion version = mock(ProductKnowledgeVersion.class);
        when(service.findByVersionId("V-1")).thenReturn(Optional.of(version));
        when(service.findByVersionId("missing")).thenReturn(Optional.empty());
        when(service.findByProductId("P-1")).thenReturn(List.of(version));
        when(service.findLatestByProductId("P-1")).thenReturn(Optional.of(version));
        when(service.findLatestByProductId("P-2")).thenReturn(Optional.empty());
        when(service.findByCategory("CAT")).thenReturn(List.of(version));
        when(service.findRecentVersions(10)).thenReturn(List.of(version));
        when(service.create(version)).thenReturn(version);

        assertSame(version, controller.getByVersionId("V-1").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.getByVersionId("missing").getStatusCode());
        assertEquals(List.of(version), controller.getByProductId("P-1").getBody());
        assertSame(version, controller.getLatestByProductId("P-1").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.getLatestByProductId("P-2").getStatusCode());
        assertSame(version, controller.getLatest("P-1").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.getLatest("P-2").getStatusCode());
        assertEquals(List.of(version), controller.getByCategory("CAT").getBody());
        assertEquals(List.of(version), controller.getRecent(10).getBody());
        assertEquals(HttpStatus.CREATED, controller.create(version).getStatusCode());
    }

    @Test
    void recordingConsentController_coversAllEndpointsAndBranches() {
        RecordingConsentService service = mock(RecordingConsentService.class);
        RecordingConsentController controller = new RecordingConsentController(service);
        RecordingConsent consent = mock(RecordingConsent.class);
        when(service.findByConsentId("RC-1")).thenReturn(Optional.of(consent));
        when(service.findByConsentId("missing")).thenReturn(Optional.empty());
        when(service.findByInteractionId("I-1")).thenReturn(List.of(consent));
        when(service.findLatestByInteractionId("I-1")).thenReturn(Optional.of(consent));
        when(service.findLatestByInteractionId("I-2")).thenReturn(Optional.empty());
        when(service.findByCustomerId("C-1")).thenReturn(List.of(consent));
        when(service.findByStatus("ACTIVE")).thenReturn(List.of(consent));
        when(service.create(consent)).thenReturn(consent);
        when(service.updateStatus("RC-1", "WITHDRAWN", "reason")).thenReturn(Optional.of(consent));
        when(service.updateStatus("RC-2", "WITHDRAWN", null)).thenReturn(Optional.empty());

        assertSame(consent, controller.getById("RC-1").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.getById("missing").getStatusCode());
        assertEquals(List.of(consent), controller.getByInteractionId("I-1").getBody());
        assertSame(consent, controller.getLatestByInteractionId("I-1").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.getLatestByInteractionId("I-2").getStatusCode());
        assertEquals(List.of(consent), controller.getByCustomerId("C-1").getBody());
        assertEquals(List.of(consent), controller.getByStatus("ACTIVE").getBody());
        assertEquals(HttpStatus.CREATED, controller.create(consent).getStatusCode());
        assertSame(consent, controller.updateStatus("RC-1", "WITHDRAWN", "reason").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.updateStatus("RC-2", "WITHDRAWN", null).getStatusCode());
    }

    @Test
    void externalEventController_coversAllEndpointsAndBranches() {
        ExternalEventService service = mock(ExternalEventService.class);
        ExternalEventController controller = new ExternalEventController(service);
        ExternalEvent event = mock(ExternalEvent.class);
        when(service.findByEventId("E-1")).thenReturn(Optional.of(event));
        when(service.findByEventId("missing")).thenReturn(Optional.empty());
        when(service.findByEventType("REGULATORY")).thenReturn(List.of(event));
        when(service.findByAffectedCustomerId("C-1")).thenReturn(List.of(event));
        when(service.findByAffectedIndustry("BANKING")).thenReturn(List.of(event));
        when(service.findBySeverity("HIGH")).thenReturn(List.of(event));
        when(service.findRecent(10)).thenReturn(List.of(event));
        when(service.findAll()).thenReturn(List.of(event));
        when(service.create(event)).thenReturn(event);

        assertSame(event, controller.getById("E-1").getBody());
        assertEquals(HttpStatus.NOT_FOUND, controller.getById("missing").getStatusCode());
        assertEquals(List.of(event), controller.getByEventType("REGULATORY").getBody());
        assertEquals(List.of(event), controller.getByCustomerId("C-1").getBody());
        assertEquals(List.of(event), controller.getByIndustry("BANKING").getBody());
        assertEquals(List.of(event), controller.getBySeverity("HIGH").getBody());
        assertEquals(List.of(event), controller.getRecent(10).getBody());
        assertEquals(List.of(event), controller.listAll().getBody());
        assertEquals(HttpStatus.CREATED, controller.create(event).getStatusCode());
        assertEquals(HttpStatus.OK, controller.getRecent(20).getStatusCode());
    }
}
