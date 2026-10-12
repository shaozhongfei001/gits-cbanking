package com.gien.gits.api.productknowledge;

/**
 * 检索召回的出处（可回译到 KERT 产物：chunkId=referenceId，docId=filePath）。
 */
public record RetrievalCitation(String chunkId, String docId, String content,
                                String artifact, String planId, String planHash) {
}
