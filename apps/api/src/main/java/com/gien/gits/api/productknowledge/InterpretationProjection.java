package com.gien.gits.api.productknowledge;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;
import java.util.Map;

/**
 * KERT 侧 {@code 04_serve/interpretation/{productId}.json} 投影的内存表示。
 *
 * <p>字段与 CTR-PK-INT-001 的三视图结构一致；本类只做反序列化载体，
 * 不承载任何业务规则。</p>
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class InterpretationProjection {

    private String productId;
    private String releaseId;
    private String bundleHash;
    private String lifecycleState;
    private Boolean isStale = Boolean.FALSE;
    private String staleReason;
    private String provenanceState;
    private Map<String, Boolean> purposeAllowed = Map.of();
    private Map<String, List<ProjectionField>> views = Map.of();
    private List<String> sourceVersions = List.of();
    private String generatedAt;

    public String getProductId() {
        return productId;
    }

    public void setProductId(String productId) {
        this.productId = productId;
    }

    public String getReleaseId() {
        return releaseId;
    }

    public void setReleaseId(String releaseId) {
        this.releaseId = releaseId;
    }

    public String getBundleHash() {
        return bundleHash;
    }

    public void setBundleHash(String bundleHash) {
        this.bundleHash = bundleHash;
    }

    public String getLifecycleState() {
        return lifecycleState;
    }

    public void setLifecycleState(String lifecycleState) {
        this.lifecycleState = lifecycleState;
    }

    public Boolean getIsStale() {
        return isStale;
    }

    public void setIsStale(Boolean isStale) {
        this.isStale = isStale == null ? Boolean.FALSE : isStale;
    }

    public String getStaleReason() {
        return staleReason;
    }

    public void setStaleReason(String staleReason) {
        this.staleReason = staleReason;
    }

    public String getProvenanceState() {
        return provenanceState;
    }

    public void setProvenanceState(String provenanceState) {
        this.provenanceState = provenanceState;
    }

    public Map<String, Boolean> getPurposeAllowed() {
        return purposeAllowed;
    }

    public void setPurposeAllowed(Map<String, Boolean> purposeAllowed) {
        this.purposeAllowed = purposeAllowed == null ? Map.of() : purposeAllowed;
    }

    public Map<String, List<ProjectionField>> getViews() {
        return views;
    }

    public void setViews(Map<String, List<ProjectionField>> views) {
        this.views = views == null ? Map.of() : views;
    }

    public List<String> getSourceVersions() {
        return sourceVersions;
    }

    public void setSourceVersions(List<String> sourceVersions) {
        this.sourceVersions = sourceVersions == null ? List.of() : sourceVersions;
    }

    public String getGeneratedAt() {
        return generatedAt;
    }

    public void setGeneratedAt(String generatedAt) {
        this.generatedAt = generatedAt;
    }

    /** 投影中的单个字段（含证据回链摘要）。 */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ProjectionField {

        private String fieldPath;
        private String displayValue;
        private String knowledgeState;
        private List<ProjectionEvidence> evidenceSummaries = List.of();
        private String conflictId;

        public String getFieldPath() {
            return fieldPath;
        }

        public void setFieldPath(String fieldPath) {
            this.fieldPath = fieldPath;
        }

        public String getDisplayValue() {
            return displayValue;
        }

        public void setDisplayValue(String displayValue) {
            this.displayValue = displayValue;
        }

        public String getKnowledgeState() {
            return knowledgeState;
        }

        public void setKnowledgeState(String knowledgeState) {
            this.knowledgeState = knowledgeState;
        }

        public List<ProjectionEvidence> getEvidenceSummaries() {
            return evidenceSummaries;
        }

        public void setEvidenceSummaries(List<ProjectionEvidence> evidenceSummaries) {
            this.evidenceSummaries = evidenceSummaries == null ? List.of() : evidenceSummaries;
        }

        public String getConflictId() {
            return conflictId;
        }

        public void setConflictId(String conflictId) {
            this.conflictId = conflictId;
        }
    }

    /** 证据回链摘要。 */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ProjectionEvidence {

        private String evidenceId;
        private String sourceId;
        private String sourceVersionId;
        private String authorityLevel;
        private String locatorHint;
        private String quoteExcerpt;

        public String getEvidenceId() {
            return evidenceId;
        }

        public void setEvidenceId(String evidenceId) {
            this.evidenceId = evidenceId;
        }

        public String getSourceId() {
            return sourceId;
        }

        public void setSourceId(String sourceId) {
            this.sourceId = sourceId;
        }

        public String getSourceVersionId() {
            return sourceVersionId;
        }

        public void setSourceVersionId(String sourceVersionId) {
            this.sourceVersionId = sourceVersionId;
        }

        public String getAuthorityLevel() {
            return authorityLevel;
        }

        public void setAuthorityLevel(String authorityLevel) {
            this.authorityLevel = authorityLevel;
        }

        public String getLocatorHint() {
            return locatorHint;
        }

        public void setLocatorHint(String locatorHint) {
            this.locatorHint = locatorHint;
        }

        public String getQuoteExcerpt() {
            return quoteExcerpt;
        }

        public void setQuoteExcerpt(String quoteExcerpt) {
            this.quoteExcerpt = quoteExcerpt;
        }
    }
}
