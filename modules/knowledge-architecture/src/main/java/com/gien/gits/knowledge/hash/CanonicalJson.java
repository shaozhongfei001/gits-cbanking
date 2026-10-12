package com.gien.gits.knowledge.hash;

import java.text.Normalizer;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * GK-KE 跨语言规范化 JSON（合同 C08 / 验收 T35）。
 *
 * <p>与 Python 造数侧严格对齐：
 * {@code json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))}，
 * 字符串先做 Unicode NFC 归一化，再做 UTF-8 SHA-256。
 *
 * <p>零外部依赖：自带最小 JSON 解析器，避免在知识架构模块引入 Jackson。
 * 仅支持合同对象用到的类型：object / array / string / number / true / false / null。
 */
public final class CanonicalJson {

    private CanonicalJson() {
    }

    /** 解析 JSON 文本为 Java 表示（Map 保持插入序，规范化时再排序）。 */
    public static Object parse(String json) {
        Parser parser = new Parser(json);
        Object value = parser.parseValue();
        parser.skipWhitespace();
        if (!parser.atEnd()) {
            throw new IllegalArgumentException("trailing content at index " + parser.pos);
        }
        return value;
    }

    /** 规范化为与 Python 对齐的紧凑 JSON 字符串（NFC + 键排序 + 无空格 + 非 ASCII 原样）。 */
    public static String canonicalize(Object value) {
        StringBuilder sb = new StringBuilder();
        write(normalize(value), sb);
        return sb.toString();
    }

    /** 解析并规范化的便捷方法。 */
    public static String canonicalizeJson(String json) {
        return canonicalize(parse(json));
    }

    // ---- 规范化：字符串 NFC，结构递归 ----

    @SuppressWarnings("unchecked")
    private static Object normalize(Object value) {
        if (value instanceof String s) {
            return Normalizer.normalize(s, Normalizer.Form.NFC);
        }
        if (value instanceof Map<?, ?> map) {
            Map<String, Object> out = new LinkedHashMap<>();
            for (Map.Entry<?, ?> e : map.entrySet()) {
                out.put(Normalizer.normalize((String) e.getKey(), Normalizer.Form.NFC),
                        normalize(e.getValue()));
            }
            return out;
        }
        if (value instanceof List<?> list) {
            List<Object> out = new ArrayList<>(list.size());
            for (Object item : list) {
                out.add(normalize(item));
            }
            return out;
        }
        return value;
    }

    @SuppressWarnings("unchecked")
    private static void write(Object value, StringBuilder sb) {
        if (value == null) {
            sb.append("null");
        } else if (value instanceof Boolean || value instanceof Number) {
            sb.append(value.toString());
        } else if (value instanceof String s) {
            writeString(s, sb);
        } else if (value instanceof Map<?, ?> map) {
            // sort_keys=True：按 Unicode 码点排序（TreeMap 按 String 自然序，即码点序）
            TreeMap<String, Object> sorted = new TreeMap<>((Map<String, Object>) map);
            sb.append('{');
            boolean first = true;
            for (Map.Entry<String, Object> e : sorted.entrySet()) {
                if (!first) {
                    sb.append(',');
                }
                first = false;
                writeString(e.getKey(), sb);
                sb.append(':');
                write(e.getValue(), sb);
            }
            sb.append('}');
        } else if (value instanceof List<?> list) {
            sb.append('[');
            for (int i = 0; i < list.size(); i++) {
                if (i > 0) {
                    sb.append(',');
                }
                write(list.get(i), sb);
            }
            sb.append(']');
        } else {
            throw new IllegalArgumentException("unsupported type: " + value.getClass());
        }
    }

    /** ensure_ascii=False：非 ASCII（含中文）原样输出，仅转义 JSON 必需字符，对齐 Python json。 */
    private static void writeString(String s, StringBuilder sb) {
        sb.append('"');
        int i = 0;
        while (i < s.length()) {
            int cp = s.codePointAt(i);
            switch (cp) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\b' -> sb.append("\\b");
                case '\f' -> sb.append("\\f");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> {
                    if (cp < 0x20) {
                        sb.append(String.format("\\u%04x", cp));
                    } else {
                        sb.appendCodePoint(cp);
                    }
                }
            }
            i += Character.charCount(cp);
        }
        sb.append('"');
    }

    // ---- 最小递归下降 JSON 解析器 ----

    private static final class Parser {
        private final String src;
        private int pos;

        Parser(String src) {
            this.src = src;
        }

        boolean atEnd() {
            return pos >= src.length();
        }

        void skipWhitespace() {
            while (pos < src.length() && Character.isWhitespace(src.charAt(pos))) {
                pos++;
            }
        }

        Object parseValue() {
            skipWhitespace();
            if (atEnd()) {
                throw new IllegalArgumentException("unexpected end of JSON");
            }
            char c = src.charAt(pos);
            return switch (c) {
                case '{' -> parseObject();
                case '[' -> parseArray();
                case '"' -> parseString();
                case 't', 'f' -> parseBoolean();
                case 'n' -> parseNull();
                default -> parseNumber();
            };
        }

        Map<String, Object> parseObject() {
            Map<String, Object> map = new LinkedHashMap<>();
            expect('{');
            skipWhitespace();
            if (peek() == '}') {
                pos++;
                return map;
            }
            while (true) {
                skipWhitespace();
                String key = parseString();
                skipWhitespace();
                expect(':');
                Object value = parseValue();
                map.put(key, value);
                skipWhitespace();
                char c = next();
                if (c == '}') {
                    break;
                }
                if (c != ',') {
                    throw new IllegalArgumentException("expected ',' or '}' at " + pos);
                }
            }
            return map;
        }

        List<Object> parseArray() {
            List<Object> list = new ArrayList<>();
            expect('[');
            skipWhitespace();
            if (peek() == ']') {
                pos++;
                return list;
            }
            while (true) {
                list.add(parseValue());
                skipWhitespace();
                char c = next();
                if (c == ']') {
                    break;
                }
                if (c != ',') {
                    throw new IllegalArgumentException("expected ',' or ']' at " + pos);
                }
            }
            return list;
        }

        String parseString() {
            expect('"');
            StringBuilder sb = new StringBuilder();
            while (true) {
                char c = next();
                if (c == '"') {
                    break;
                }
                if (c == '\\') {
                    char e = next();
                    switch (e) {
                        case '"' -> sb.append('"');
                        case '\\' -> sb.append('\\');
                        case '/' -> sb.append('/');
                        case 'b' -> sb.append('\b');
                        case 'f' -> sb.append('\f');
                        case 'n' -> sb.append('\n');
                        case 'r' -> sb.append('\r');
                        case 't' -> sb.append('\t');
                        case 'u' -> {
                            int hex = Integer.parseInt(src.substring(pos, pos + 4), 16);
                            pos += 4;
                            sb.append((char) hex);
                        }
                        default -> throw new IllegalArgumentException("bad escape \\" + e);
                    }
                } else {
                    sb.append(c);
                }
            }
            return sb.toString();
        }

        Boolean parseBoolean() {
            if (src.startsWith("true", pos)) {
                pos += 4;
                return Boolean.TRUE;
            }
            if (src.startsWith("false", pos)) {
                pos += 5;
                return Boolean.FALSE;
            }
            throw new IllegalArgumentException("invalid literal at " + pos);
        }

        Object parseNull() {
            if (src.startsWith("null", pos)) {
                pos += 4;
                return null;
            }
            throw new IllegalArgumentException("invalid literal at " + pos);
        }

        Number parseNumber() {
            int start = pos;
            if (peek() == '-') {
                pos++;
            }
            boolean isFractional = false;
            while (!atEnd()) {
                char c = peek();
                if (Character.isDigit(c)) {
                    pos++;
                } else if (c == '.' || c == 'e' || c == 'E' || c == '+' || c == '-') {
                    if (c == '.') {
                        isFractional = true;
                    }
                    pos++;
                } else {
                    break;
                }
            }
            String token = src.substring(start, pos);
            // 合同要求金额用字符串；这里数字仅用于结构字段，整数走 Long，小数走 Double。
            // 必须用显式 if/else 返回 Number，不能用三元表达式——
            // 否则 JLS 数值提升会把 Long 分支也拆箱提升为 double，整数 1 被序列化成 1.0。
            if (isFractional) {
                return (Number) Double.valueOf(token);
            }
            return (Number) Long.valueOf(token);
        }

        private char peek() {
            if (atEnd()) {
                throw new IllegalArgumentException("unexpected end");
            }
            return src.charAt(pos);
        }

        private char next() {
            char c = peek();
            pos++;
            return c;
        }

        private void expect(char c) {
            skipWhitespace();
            char actual = next();
            if (actual != c) {
                throw new IllegalArgumentException("expected '" + c + "' but got '" + actual + "' at " + pos);
            }
        }
    }
}
