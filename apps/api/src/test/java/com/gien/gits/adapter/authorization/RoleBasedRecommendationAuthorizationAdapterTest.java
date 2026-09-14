package com.gien.gits.adapter.authorization;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * {@link RoleBasedRecommendationAuthorizationAdapter} 单元测试（F-4）。
 *
 * <p>核心断言是「消除无条件越权」：此前占位实现只要 actorId 非空即放行，
 * 本测试显式覆盖那些旧实现会放行、新实现必须拒绝的场景。</p>
 */
class RoleBasedRecommendationAuthorizationAdapterTest {

    private static final Set<String> ROLES = Set.of("RM", "RM_SUPERVISOR");

    private final RoleBasedRecommendationAuthorizationAdapter adapter =
            new RoleBasedRecommendationAuthorizationAdapter(ROLES);

    @Test
    @DisplayName("白名单角色 + 非空 actorId/gateId → 放行")
    void allowsWhitelistedRole() {
        assertThat(adapter.isAuthorized("RM-001", "RM", "HG-D01-001")).isTrue();
        assertThat(adapter.isAuthorized("RM-002", "RM_SUPERVISOR", "HG-D01-002")).isTrue();
    }

    @Test
    @DisplayName("角色大小写与空白不敏感 → 放行")
    void normalizesRoleCaseAndWhitespace() {
        assertThat(adapter.isAuthorized("RM-001", " rm ", "HG-D01-001")).isTrue();
        assertThat(adapter.isAuthorized("RM-001", "Rm_Supervisor", "HG-D01-001")).isTrue();
    }

    @Test
    @DisplayName("F-4 回归：actorId 非空但角色缺失 → 拒绝（旧占位实现会放行）")
    void deniesBlankRoleEvenWithActorId() {
        assertThat(adapter.isAuthorized("RM-001", null, "HG-D01-001")).isFalse();
        assertThat(adapter.isAuthorized("RM-001", "", "HG-D01-001")).isFalse();
        assertThat(adapter.isAuthorized("RM-001", "   ", "HG-D01-001")).isFalse();
    }

    @Test
    @DisplayName("F-4 回归：actorId 非空但角色不在白名单 → 拒绝（旧占位实现会放行）")
    void deniesRoleOutsideWhitelist() {
        assertThat(adapter.isAuthorized("X-001", "GUEST", "HG-D01-001")).isFalse();
        assertThat(adapter.isAuthorized("X-001", "ANONYMOUS", "HG-D01-001")).isFalse();
        assertThat(adapter.isAuthorized("X-001", "ADMIN", "HG-D01-001")).isFalse();
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {"   "})
    @DisplayName("actorId 为空 → 拒绝（无法归因的操作不可审计）")
    void deniesBlankActorId(String actorId) {
        assertThat(adapter.isAuthorized(actorId, "RM", "HG-D01-001")).isFalse();
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {"   "})
    @DisplayName("gateId 为空 → 拒绝（不允许无目标的决定）")
    void deniesBlankGateId(String gateId) {
        assertThat(adapter.isAuthorized("RM-001", "RM", gateId)).isFalse();
    }

    @Test
    @DisplayName("fail-closed：白名单为空集时拒绝一切请求")
    void failsClosedOnEmptyWhitelist() {
        RoleBasedRecommendationAuthorizationAdapter empty =
                new RoleBasedRecommendationAuthorizationAdapter(Set.of());
        assertThat(empty.isAuthorized("RM-001", "RM", "HG-D01-001")).isFalse();
    }

    @Test
    @DisplayName("fail-closed：白名单为 null 时拒绝一切请求")
    void failsClosedOnNullWhitelist() {
        RoleBasedRecommendationAuthorizationAdapter nullWhitelist =
                new RoleBasedRecommendationAuthorizationAdapter(null);
        assertThat(nullWhitelist.isAuthorized("RM-001", "RM", "HG-D01-001")).isFalse();
    }

    @Test
    @DisplayName("白名单不可变：构造后外部修改入参集合不影响判定")
    void whitelistIsImmutableCopy() {
        Set<String> mutable = new java.util.HashSet<>(Set.of("RM"));
        RoleBasedRecommendationAuthorizationAdapter a =
                new RoleBasedRecommendationAuthorizationAdapter(mutable);
        mutable.add("GUEST");
        assertThat(a.isAuthorized("X-001", "GUEST", "HG-D01-001")).isFalse();
    }
}
