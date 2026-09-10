package com.gien.gits.knowledge.gkke.registry;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 从文件目录批量加载 {@link AssetVersionRecord} JSON 到内存注册中心。
 *
 * <p>每个文件必须是一个 AssetVersion 对象（CR-02 §4.1）；重复版本由注册中心拒绝。
 * 文件按文件名排序加载，保证登记顺序确定。
 */
public final class InMemoryAssetRegistryLoader {

    private static final Logger LOG = LoggerFactory.getLogger(InMemoryAssetRegistryLoader.class);
    private static final String JSON_SUFFIX = ".json";

    private final ObjectMapper objectMapper;

    public InMemoryAssetRegistryLoader() {
        this(new ObjectMapper().configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false));
    }

    public InMemoryAssetRegistryLoader(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    /** 从文件系统目录加载全部 {@code *.json}（按文件名排序保证确定性）。 */
    public InMemoryAssetRegistry loadDirectory(Path directory) throws IOException {
        InMemoryAssetRegistry registry = new InMemoryAssetRegistry();
        try (Stream<Path> paths = Files.list(directory)) {
            List<Path> files = paths
                    .filter(Files::isRegularFile)
                    .filter(path -> path.getFileName().toString().endsWith(JSON_SUFFIX))
                    .sorted(Comparator.comparing(path -> path.getFileName().toString()))
                    .toList();
            for (Path file : files) {
                registry.register(objectMapper.readValue(file.toFile(), AssetVersionRecord.class));
            }
        }
        LOG.info("Asset registry loaded from directory: dir={}, assets={}", directory, registry.size());
        return registry;
    }
}
