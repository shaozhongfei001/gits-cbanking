package com.gien.gits.knowledge.gkke.registry;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.gien.gits.knowledge.gkke.model.VersionRef;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Q3 能力注册表测试（CR-02 §6.1，验收 T06）。
 *
 * <p>未注册能力必须抛 {@link CapabilityNotRegisteredException}，携带稳定错误码
 * {@code CAPABILITY_NOT_REGISTERED}；错误码字符串跨版本稳定。</p>
 */
class CapabilityRegistryTest {

    private final CapabilityRegistry registry = new CapabilityRegistry();

    @Test
    @DisplayName("已登记能力校验通过")
    void registeredCapabilityPasses() {
        registry.register("CAP-RETRIEVE", "1.0.0");

        assertThat(registry.isRegistered("CAP-RETRIEVE", "1.0.0")).isTrue();
        assertThatCode(() -> registry.requireRegistered(
                new VersionRef("CAP-RETRIEVE", "1.0.0"))).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("未登记能力抛 CAPABILITY_NOT_REGISTERED（验收 T06）")
    void unregisteredCapabilityRejected() {
        assertThatThrownBy(() -> registry.requireRegistered(
                new VersionRef("CAP-GHOST", "1.0.0")))
                .isInstanceOf(CapabilityNotRegisteredException.class)
                .hasMessageContaining("CAP-GHOST")
                .extracting(ex -> ((GkDomainException) ex).errorCode())
                .isEqualTo("CAPABILITY_NOT_REGISTERED");
    }

    @Test
    @DisplayName("同 ID 不同版本视为不同能力；null 入参被拒绝")
    void versionIsPartOfIdentity() {
        registry.register("CAP-RETRIEVE", "1.0.0");

        assertThat(registry.isRegistered("CAP-RETRIEVE", "2.0.0")).isFalse();
        assertThatThrownBy(() -> registry.requireRegistered(null))
                .isInstanceOf(NullPointerException.class);
    }

    @Test
    @DisplayName("错误码枚举合同字符串稳定（T06 依赖的机器可读契约）")
    void errorCodeWireValuesStable() {
        assertThat(GkErrorCode.DEPENDENCY_UNRESOLVED.wireValue())
                .isEqualTo("DEPENDENCY_UNRESOLVED");
        assertThat(GkErrorCode.CAPABILITY_NOT_REGISTERED.wireValue())
                .isEqualTo("CAPABILITY_NOT_REGISTERED");
        assertThat(GkErrorCode.ASSET_NOT_AVAILABLE.wireValue()).isEqualTo("ASSET_NOT_AVAILABLE");
        assertThat(GkErrorCode.ROUTE_AMBIGUOUS.wireValue()).isEqualTo("ROUTE_AMBIGUOUS");
    }
}
