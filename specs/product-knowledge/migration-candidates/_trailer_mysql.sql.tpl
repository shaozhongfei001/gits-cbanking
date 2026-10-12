
-- ============================================================
-- 不可变性保障（MySQL）：BEFORE UPDATE 触发器直接报错
-- ============================================================
DELIMITER $$

CREATE TRIGGER pk_evidence_span_no_update BEFORE UPDATE ON pk_evidence_span
FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'pk_evidence_span is immutable (CTR-PK-EVS-002)';
END$$

CREATE TRIGGER pk_fragment_no_update BEFORE UPDATE ON pk_fragment
FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'pk_fragment is immutable';
END$$

CREATE TRIGGER pk_field_assertion_no_update BEFORE UPDATE ON pk_field_assertion
FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'pk_field_assertion is immutable; use supersedes chain (INV-ASM-06)';
END$$

CREATE TRIGGER pk_review_decision_no_update BEFORE UPDATE ON pk_review_decision
FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'pk_review_decision is append-only (INV-CNF-05)';
END$$

CREATE TRIGGER pk_knowledge_release_published_immutable BEFORE UPDATE ON pk_knowledge_release
FOR EACH ROW BEGIN
    IF OLD.lifecycle_state = 'PUBLISHED'
       AND NOT (NEW.bundle_hash <=> OLD.bundle_hash) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'published release is immutable; create new releaseId (INV-RLS-05)';
    END IF;
END$$

DELIMITER ;
