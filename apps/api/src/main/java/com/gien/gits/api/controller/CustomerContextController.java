package com.gien.gits.api.controller;

import com.gien.gits.api.dto.CrmCustomerMaster;
import com.gien.gits.api.dto.CrmCustomerMasterReloadResponse;
import com.gien.gits.api.dto.CrmCustomerUpsertResponse;
import com.gien.gits.api.dto.CustomerCreatedResponse;
import com.gien.gits.api.service.CrmCustomerMasterService;
import com.gien.gits.api.service.CustomerContextService;
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
@RequestMapping("/api/v1/engagement")
public class CustomerContextController {

    private final CustomerContextService customerContextService;
    private final TransactionRepository transactionRepo;
    private final ProductMatchingService productMatchingService;
    private final CrmCustomerMasterService crmCustomerMasterService;

    public CustomerContextController(CustomerContextService customerContextService,
                                      TransactionRepository transactionRepo,
                                      ProductMatchingService productMatchingService,
                                      CrmCustomerMasterService crmCustomerMasterService) {
        this.customerContextService = Objects.requireNonNull(customerContextService);
        this.transactionRepo = Objects.requireNonNull(transactionRepo);
        this.productMatchingService = Objects.requireNonNull(productMatchingService);
        this.crmCustomerMasterService = Objects.requireNonNull(crmCustomerMasterService);
    }

    @GetMapping("/customer/{customerId}/operating-view")
    public ResponseEntity<CustomerContextService.CustomerOperatingView> getOperatingView(
            @PathVariable String customerId) {
        return ResponseEntity.ok(customerContextService.buildOperatingView(customerId));
    }

    @PostMapping("/customer")
    public ResponseEntity<CustomerCreatedResponse> createCustomer(@RequestBody Customer customer) {
        customerContextService.saveCustomer(customer);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(new CustomerCreatedResponse(customer.customerId(), "CREATED"));
    }

    @PutMapping("/customer/{customerId}")
    public ResponseEntity<CrmCustomerUpsertResponse> upsertCrmCustomer(
            @PathVariable String customerId,
            @RequestBody CrmCustomerMaster body) {
        return ResponseEntity.ok(crmCustomerMasterService.upsert(customerId, body));
    }

    @PostMapping("/crm-customer-master/reload")
    public ResponseEntity<CrmCustomerMasterReloadResponse> reloadCrmCustomerMaster() {
        return ResponseEntity.ok(crmCustomerMasterService.reloadFromFixture());
    }

    @GetMapping("/customer")
    public ResponseEntity<List<Customer>> listCustomersByRm(@RequestParam String rmId) {
        return ResponseEntity.ok(customerContextService.findCustomersByRm(rmId));
    }

    // --- P9 Loop G7: 交易流水与产品匹配 ---

    @GetMapping("/customer/{customerId}/transactions")
    public ResponseEntity<List<Transaction>> getTransactions(
            @PathVariable String customerId,
            @RequestParam(required = false) Integer limit) {
        List<Transaction> transactions = (limit != null && limit > 0)
            ? transactionRepo.findRecentByCustomerId(customerId, limit)
            : transactionRepo.findByCustomerId(customerId);
        return ResponseEntity.ok(transactions);
    }

    @PostMapping("/customer/{customerId}/product-matching")
    public ResponseEntity<List<ProductMatchingService.ProductMatch>> matchProducts(
            @PathVariable String customerId) {
        return ResponseEntity.ok(productMatchingService.matchProducts(customerId));
    }
}
