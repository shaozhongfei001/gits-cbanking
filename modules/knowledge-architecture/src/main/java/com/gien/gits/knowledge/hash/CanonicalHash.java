package com.gien.gits.knowledge.hash;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * GK-KE 规范化内容哈希工具（合同 C08 / 验收 T35）。
 *
 * <p>对规范化 JSON 字节做 UTF-8 SHA-256，输出小写十六进制。
 * 必须与 Python 造数侧 {@code hashlib.sha256(canonical.encode('utf-8')).hexdigest()}
 * 逐位一致。
 */
public final class CanonicalHash {

    private CanonicalHash() {
    }

    /** 对已规范化的 JSON 字符串计算 SHA-256 十六进制摘要。 */
    public static String sha256Hex(String canonicalJson) {
        return sha256Hex(canonicalJson.getBytes(StandardCharsets.UTF_8));
    }

    /** 对原始字节计算 SHA-256 十六进制摘要。 */
    public static String sha256Hex(byte[] bytes) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(bytes);
            StringBuilder sb = new StringBuilder(digest.length * 2);
            for (byte b : digest) {
                sb.append(Character.forDigit((b >> 4) & 0xF, 16));
                sb.append(Character.forDigit(b & 0xF, 16));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 unavailable", e);
        }
    }

    /** 解析 + 规范化 + 哈希的一步式便捷方法。 */
    public static String canonicalSha256(String json) {
        return sha256Hex(CanonicalJson.canonicalizeJson(json));
    }
}
