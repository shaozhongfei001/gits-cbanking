package com.gien.gits.knowledge.gkke.registry;

import java.util.Comparator;

/**
 * GK-KE v1 语义版本比较（CR-02 §4.1：版本按语义版本比较）。
 *
 * <p>支持 {@code MAJOR.MINOR.PATCH} 数字点分版本；非法/缺失版本排在最前。
 */
final class SemanticVersion {

    static final Comparator<String> COMPARATOR =
            (left, right) -> compareArrays(parse(left), parse(right));

    private SemanticVersion() {
    }

    private static int compareArrays(int[] left, int[] right) {
        for (int index = 0; index < Math.min(left.length, right.length); index++) {
            int result = Integer.compare(left[index], right[index]);
            if (result != 0) {
                return result;
            }
        }
        return Integer.compare(left.length, right.length);
    }

    private static int[] parse(String version) {
        if (version == null || version.isBlank()) {
            return new int[]{-1, -1, -1};
        }
        String[] parts = version.trim().split("\\.");
        int[] numbers = new int[3];
        for (int index = 0; index < 3; index++) {
            numbers[index] = index < parts.length ? parsePart(parts[index]) : 0;
        }
        return numbers;
    }

    private static int parsePart(String part) {
        try {
            return Integer.parseInt(part);
        } catch (NumberFormatException ex) {
            return 0;
        }
    }
}
