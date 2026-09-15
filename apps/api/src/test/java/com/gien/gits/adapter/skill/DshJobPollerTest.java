package com.gien.gits.adapter.skill;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;

import com.gien.gits.engagement.port.SkillExecutionException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

/**
 * 验证 {@link DshJobPoller} 契约 v1.4 §2.2 轮询行为：
 * COMPLETED 取 data.skill_result；FAILED / 超时 / 非 2xx → {@link SkillExecutionException}。
 */
class DshJobPollerTest {

    private static final String JOB_URL = "http://dsh.local:3080/v1/jobs/JOB-TEST-001";

    private RestClient.Builder builder;
    private MockRestServiceServer server;
    private DshJobPoller poller;

    @BeforeEach
    void setUp() {
        builder = RestClient.builder();
        server = MockRestServiceServer.bindTo(builder).build();
        poller = new DshJobPoller(builder.build(), "http://dsh.local:3080", 60_000L, 10L);
    }

    @Test
    void completedReturnsSkillResult() {
        server.expect(requestTo(JOB_URL))
            .andRespond(withSuccess(
                "{\"jobId\":\"JOB-TEST-001\",\"status\":\"ok\","
                + "\"data\":{\"status\":\"COMPLETED\","
                + "\"skill_result\":{\"status\":\"ok\",\"data\":{\"reportId\":\"R-1\"}}}}",
                MediaType.APPLICATION_JSON));

        String result = poller.pollUntilCompleted("JOB-TEST-001");

        assertThat(result).contains("\"reportId\":\"R-1\"");
        server.verify();
    }

    @Test
    void runningThenCompleted() {
        server.expect(requestTo(JOB_URL))
            .andRespond(withSuccess(
                "{\"jobId\":\"JOB-TEST-001\",\"status\":\"ok\",\"data\":{\"status\":\"RUNNING\"}}",
                MediaType.APPLICATION_JSON));
        server.expect(requestTo(JOB_URL))
            .andRespond(withSuccess(
                "{\"jobId\":\"JOB-TEST-001\",\"status\":\"ok\","
                + "\"data\":{\"status\":\"COMPLETED\",\"skill_result\":{\"status\":\"ok\"}}}",
                MediaType.APPLICATION_JSON));

        String result = poller.pollUntilCompleted("JOB-TEST-001");

        assertThat(result).isEqualTo("{\"status\":\"ok\"}");
        server.verify();
    }

    @Test
    void failedThrows() {
        server.expect(requestTo(JOB_URL))
            .andRespond(withSuccess(
                "{\"jobId\":\"JOB-TEST-001\",\"status\":\"ok\",\"data\":{\"status\":\"FAILED\"}}",
                MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> poller.pollUntilCompleted("JOB-TEST-001"))
            .isInstanceOf(SkillExecutionException.class)
            .hasMessageContaining("job failed");
        server.verify();
    }

    @Test
    void httpErrorThrows() {
        server.expect(requestTo(JOB_URL))
            .andRespond(withStatus(org.springframework.http.HttpStatus.INTERNAL_SERVER_ERROR)
                .contentType(MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> poller.pollUntilCompleted("JOB-TEST-001"))
            .isInstanceOf(SkillExecutionException.class)
            .hasMessageContaining("SKILL JOB HTTP 500");
        server.verify();
    }

    @Test
    void timeoutThrows() {
        // 短超时 + RUNNING 持续：验证总超时兜底（timeout=150ms, interval=100ms，
        // 第 1 次轮询后 100<150 继续，第 2 次轮询后 200>150 判定超时）
        poller = new DshJobPoller(builder.build(), "http://dsh.local:3080", 150L, 100L);
        server.expect(requestTo(JOB_URL))
            .andRespond(withSuccess(
                "{\"jobId\":\"JOB-TEST-001\",\"status\":\"ok\",\"data\":{\"status\":\"RUNNING\"}}",
                MediaType.APPLICATION_JSON));
        server.expect(requestTo(JOB_URL))
            .andRespond(withSuccess(
                "{\"jobId\":\"JOB-TEST-001\",\"status\":\"ok\",\"data\":{\"status\":\"RUNNING\"}}",
                MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> poller.pollUntilCompleted("JOB-TEST-001"))
            .isInstanceOf(SkillExecutionException.class)
            .hasMessageContaining("poll timeout");
        server.verify();
    }
}
