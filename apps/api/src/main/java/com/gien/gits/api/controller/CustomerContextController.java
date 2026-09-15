package com.gien.gits.api.controller;

import com.gien.gits.api.dto.AssembledKnowledgeMapResponse;
import com.gien.gits.api.dto.AssemblyTraceStep;
import com.gien.gits.api.dto.CustomerCreatedResponse;
import com.gien.gits.api.service.CustomerContextService;
import com.gien.gits.api.service.KnowledgeDrivenPrevisitReportGenerator;
import com.gien.gits.api.service.ProductMatchingService;
import com.gien.gits.ontology.Customer;
import com.gien.gits.ontology.Transaction;
import com.gien.gits.ontology.port.TransactionRepository;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;

/**
 * 客户上下文控制器 — 客户信息与经营视图
 */
@RestController
@RequestMapping("/api/v1/engagement/customer")
public class CustomerContextController {

    private final CustomerContextService customerContextService;
    private final TransactionRepository transactionRepo;
    private final ProductMatchingService productMatchingService;
    private final KnowledgeDrivenPrevisitReportGenerator knowledgeDrivenPrevisitReportGenerator;

    public CustomerContextController(CustomerContextService customerContextService,
                                      TransactionRepository transactionRepo,
                                      ProductMatchingService productMatchingService,
                                      KnowledgeDrivenPrevisitReportGenerator knowledgeDrivenPrevisitReportGenerator) {
        this.customerContextService = Objects.requireNonNull(customerContextService);
        this.transactionRepo = Objects.requireNonNull(transactionRepo);
        this.productMatchingService = Objects.requireNonNull(productMatchingService);
        this.knowledgeDrivenPrevisitReportGenerator = Objects.requireNonNull(knowledgeDrivenPrevisitReportGenerator);
    }

    @GetMapping("/{customerId}/operating-view")
    public ResponseEntity<CustomerContextService.CustomerOperatingView> getOperatingView(
            @PathVariable String customerId) {
        return ResponseEntity.ok(customerContextService.buildOperatingView(customerId));
    }

    @PostMapping
    public ResponseEntity<CustomerCreatedResponse> createCustomer(@RequestBody Customer customer) {
        customerContextService.saveCustomer(customer);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(new CustomerCreatedResponse(customer.customerId(), "CREATED"));
    }

    @GetMapping
    public ResponseEntity<List<Customer>> listCustomersByRm(@RequestParam String rmId) {
        return ResponseEntity.ok(customerContextService.findCustomersByRm(rmId));
    }

    // --- P9 Loop G7: 交易流水与产品匹配 ---

    @GetMapping("/{customerId}/transactions")
    public ResponseEntity<List<Transaction>> getTransactions(
            @PathVariable String customerId,
            @RequestParam(required = false) Integer limit) {
        List<Transaction> transactions = (limit != null && limit > 0)
            ? transactionRepo.findRecentByCustomerId(customerId, limit)
            : transactionRepo.findByCustomerId(customerId);
        return ResponseEntity.ok(transactions);
    }

    @PostMapping("/{customerId}/product-matching")
    public ResponseEntity<List<ProductMatchingService.ProductMatch>> matchProducts(
            @PathVariable String customerId) {
        return ResponseEntity.ok(productMatchingService.matchProducts(customerId));
    }

    /**
     * P38 只读知识地图：请求 DKWS Skill，不返回仓库内 KI/KE 快照。
     * Skill 失败或空 data 时 sections 为空数组。
     */
    @GetMapping("/{customerId}/knowledge-map")
    public ResponseEntity<AssembledKnowledgeMapResponse> assembledKnowledgeMap(
            @PathVariable String customerId) {
        KnowledgeDrivenPrevisitReportGenerator.GenerationResult generated =
                knowledgeDrivenPrevisitReportGenerator.generate(customerId, "");
        return ResponseEntity.ok(new AssembledKnowledgeMapResponse(
                customerId,
                generated.skillReportTitle(),
                generated.skillExecutiveSummary(),
                generated.skillSections(),
                AssemblyTraceStep.from(generated.assemblyTrace())));
    }
}
