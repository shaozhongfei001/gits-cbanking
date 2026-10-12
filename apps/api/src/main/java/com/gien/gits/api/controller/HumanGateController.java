package com.gien.gits.api.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.api.dto.HumanGateDecisionRequest;
import com.gien.gits.api.dto.HumanGateDto;
import com.gien.gits.api.dto.RecommendationHumanDecisionRequest;
import com.gien.gits.api.service.ProductRecommendationHumanGateService;
import com.gien.gits.ontology.GateType;
import com.gien.gits.ontology.HumanGate;
import com.gien.gits.ontology.HumanGateStatus;
import com.gien.gits.ontology.port.HumanGateRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 人工门禁 API 控制器。
 *
 * <p>WP5-2 改造：{@code decide} 入口注入 {@link ProductRecommendationHumanGateService}，
 * 不再直接操作 {@link HumanGateRepository} 做决策。D01（{@link GateType#D01_PRODUCT_RECOMMEND}）
 * 用结构化 payload（{@link RecommendationHumanDecisionRequest}，含 {@code proposalVersionId}），
 * 走产品推荐应用服务；其他 GateType 保持旧 {@code HumanGateDecisionRequest} 兼容（经服务透传）。
 * 列表/详情为只读查询，仍直接读 {@link HumanGateRepository}。</p>
 */
@RestController
@RequestMapping("/api/v1/human-gates")
public class HumanGateController {

    private static final Logger log = LoggerFactory.getLogger(HumanGateController.class);

    private final HumanGateRepository humanGateRepository;
    private final ProductRecommendationHumanGateService productRecommendationHumanGateService;
    private final ObjectMapper objectMapper;

    public HumanGateController(HumanGateRepository humanGateRepository,
                               ProductRecommendationHumanGateService productRecommendationHumanGateService,
                               ObjectMapper objectMapper) {
        this.humanGateRepository = humanGateRepository;
        this.productRecommendationHumanGateService = productRecommendationHumanGateService;
        this.objectMapper = objectMapper;
    }

    @GetMapping
    public ResponseEntity<List<HumanGateDto>> listHumanGates(
            @RequestParam(required = false) HumanGateStatus status,
            @RequestParam(required = false) GateType gateType,
            @RequestParam(required = false) String journeyId,
            @RequestParam(required = false) String customerId) {

        log.info("Listing human gates: status={}, gateType={}, journeyId={}, customerId={}",
                status, gateType, journeyId, customerId);

        List<HumanGate> gates;
        if (status != null) {
            gates = humanGateRepository.findByStatus(status);
        } else if (gateType != null) {
            gates = humanGateRepository.findByGateType(gateType);
        } else if (journeyId != null) {
            gates = humanGateRepository.findByJourneyId(journeyId);
        } else if (customerId != null) {
            gates = humanGateRepository.findByCustomerId(customerId);
        } else {
            gates = humanGateRepository.findAll();
        }

        var dtos = gates.stream().map(HumanGateDto::from).toList();
        return ResponseEntity.ok(dtos);
    }

    @GetMapping("/{gateId}")
    public ResponseEntity<HumanGateDto> getHumanGate(@PathVariable String gateId) {
        log.info("Getting human gate: gateId={}", gateId);
        return humanGateRepository.findById(gateId)
                .map(gate -> ResponseEntity.ok(HumanGateDto.from(gate)))
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * 门禁决策入口。按 payload 形态分流：
     * <ul>
     *   <li>含 {@code proposalVersionId} → D01 结构化决定（走产品推荐应用服务，过期/并发 → 409）。</li>
     *   <li>否则 → 旧 {@code HumanGateDecisionRequest} 决定（经服务透传 {@code HumanGateRepository.decide}，保持兼容）。</li>
     * </ul>
     */
    @PostMapping("/{gateId}/decide")
    public ResponseEntity<?> decideHumanGate(
            @PathVariable String gateId,
            @RequestBody JsonNode body) {

        if (body != null && body.has("proposalVersionId")) {
            RecommendationHumanDecisionRequest request =
                    objectMapper.convertValue(body, RecommendationHumanDecisionRequest.class);
            log.info("Deciding HG-D01: gateId={}, decision={}, actor={}, proposalVersionId={}",
                    gateId, request.decision(), request.actorId(), request.proposalVersionId());
            return ResponseEntity.ok(
                    productRecommendationHumanGateService.decideRecommendation(gateId, request));
        }

        HumanGateDecisionRequest request =
                objectMapper.convertValue(body, HumanGateDecisionRequest.class);
        log.info("Deciding human gate: gateId={}, decision={}, actor={}",
                gateId, request.decision(), request.actorId());
        return ResponseEntity.ok(HumanGateDto.from(
                productRecommendationHumanGateService.decideLegacy(gateId, request)));
    }
}
