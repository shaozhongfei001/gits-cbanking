package com.gien.gits.knowledge.hash;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

/**
 * GK-KE T35 跨语言规范化哈希黄金字节对拍。
 *
 * <p>黄金字节由 Python 造数侧生成（json.dumps ensure_ascii=False/sort_keys/
 * separators=(',',':') + SHA-256），作为 test resources 固化。Java 侧
 * {@link CanonicalJson}/{@link CanonicalHash} 必须逐字节复现。
 */
class CanonicalHashGoldenTest {

    private static final String DIR = "/gk-ke-hash";

    static List<String> cases() {
        // AssetVersion 用 .positive.json 命名，其余用 .json
        return List.of("AssetVersion", "ControlledAction", "MetricDefinition");
    }

    @DisplayName("Java 规范化字节与 SHA-256 必须与 Python 黄金字节逐位一致 (T35)")
    @ParameterizedTest(name = "{0}")
    @MethodSource("cases")
    void canonicalBytesAndHashMatchPythonGolden(String name) throws IOException {
        String jsonName = "AssetVersion".equals(name) ? name + ".positive.json" : name + ".json";
        String json = readResource(DIR + "/" + jsonName);
        byte[] goldenBytes = readResourceBytes(DIR + "/" + name + ".canonical.bin");
        String goldenHash = readResource(DIR + "/" + name + ".sha256.txt").trim();

        String canonical = CanonicalJson.canonicalizeJson(json);
        byte[] javaBytes = canonical.getBytes(StandardCharsets.UTF_8);

        assertArrayEquals(goldenBytes, javaBytes,
                "规范化字节必须与 Python 黄金字节逐字节一致: " + name);
        assertEquals(goldenHash, CanonicalHash.sha256Hex(javaBytes),
                "SHA-256 必须与 Python 一致: " + name);
    }

    private static String readResource(String path) throws IOException {
        return new String(readResourceBytes(path), StandardCharsets.UTF_8);
    }

    private static byte[] readResourceBytes(String path) throws IOException {
        try (InputStream in = CanonicalHashGoldenTest.class.getResourceAsStream(path)) {
            if (in == null) {
                throw new IOException("missing test resource: " + path);
            }
            return in.readAllBytes();
        }
    }
}
