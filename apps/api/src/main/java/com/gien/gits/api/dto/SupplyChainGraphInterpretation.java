package com.gien.gits.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record SupplyChainGraphInterpretation(
        String supplyChainPosition,
        String bargainingPower,
        List<String> concentrationRisk,
        String keyChanges,
        String overallAssessment,
        List<String> followUpQuestions,
        Object confidence) {

    public SupplyChainGraphInterpretation {
        concentrationRisk = concentrationRisk == null ? List.of() : List.copyOf(concentrationRisk);
        followUpQuestions = followUpQuestions == null ? List.of() : List.copyOf(followUpQuestions);
    }
}
