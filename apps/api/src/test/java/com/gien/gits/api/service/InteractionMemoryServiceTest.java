package com.gien.gits.api.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.adapter.skill.InteractionMemoryMapper;
import com.gien.gits.engagement.port.*;
import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.Map;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class InteractionMemoryServiceTest {
    private final SkillExecutionPort skill = mock(SkillExecutionPort.class);
    private final InteractionMemoryMapper mapper = mock(InteractionMemoryMapper.class);
    private final ObjectMapper om = new ObjectMapper();
    private final InteractionMemoryService svc = new InteractionMemoryService(skill, mapper, om);

    private SkillExecutionResult failed() {
        return new SkillExecutionResult(SkillExecutionStatus.SKILL_ERROR, "r", null, List.of(), List.of(), List.of());
    }

    @Test void nullResultReturnsEmpty() {
        when(skill.execute(any())).thenReturn(null);
        InteractionMemoryExtraction x = svc.extract("i","c","t",null);
        assertThat(x.interactionId()).isEqualTo("i");
        assertThat(x.candidateMemories()).isEmpty();
    }

    @Test void failedResultReturnsEmpty() {
        when(skill.execute(any())).thenReturn(failed());
        assertThat(svc.extract("i","c","t",List.of()).candidateMemories()).isEmpty();
    }

    @Test void okResultMapsFromResultNode() {
        SkillExecutionResult ok = new SkillExecutionResult(SkillExecutionStatus.OK,"r",
            Map.of("result",Map.of("k","v")),List.of(),List.of(),List.of());
        when(skill.execute(any())).thenReturn(ok);
        InteractionMemoryExtraction mapped = mock(InteractionMemoryExtraction.class);
        when(mapper.fromResult(any(),eq("i"))).thenReturn(mapped);
        assertThat(svc.extract("i","c","t",null)).isSameAs(mapped);
    }

    @Test void applyNullIsNoOp() {
        assertThatCode(() -> svc.apply(null)).doesNotThrowAnyException();
        verifyNoInteractions(mapper);
    }
}
