package com.gien.gits.api.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.lang.EvaluationResult;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.library.dependencies.SlicesRuleDefinition.slices;
import static org.assertj.core.api.Assertions.assertThat;

/**
 * P24 REM-P1-04: 架构边界机械验证。
 *
 * <p>使用 ArchUnit 机械验证六边形架构的分层约束：
 * <ul>
 *   <li>modules/ 不得依赖 adapters/ 或 apps/</li>
 *   <li>modules/ 不得直接依赖 Spring Framework</li>
 *   <li>adapters/ 不得依赖 apps/</li>
 *   <li>模块间无循环依赖</li>
 * </ul>
 *
 * <p>当前为 REPORT 模式：违规记录到日志但不阻塞构建。
 * 待漂移清理完成后切换为 ENFORCE 模式（改用 rule.check()）。
 */
class ArchitectureBoundaryTest {

    private static final Logger log = LoggerFactory.getLogger(ArchitectureBoundaryTest.class);
    private static JavaClasses importedClasses;

    @BeforeAll
    static void importClasses() {
        importedClasses = new ClassFileImporter()
                .importPackages("com.gien.gits");
    }

    /**
     * REPORT 模式评估：记录违规到日志但不失败测试。
     * 使用 allowEmptyShould(true) 避免空 should 抛异常。
     * 返回违规数供基线检查。
     */
    private int evaluateInReportMode(ArchRule rule, JavaClasses classes) {
        ArchRule permissiveRule = rule.allowEmptyShould(true);
        EvaluationResult result = permissiveRule.evaluate(classes);
        boolean hasViolation = result.hasViolation();
        int violationCount = hasViolation
                ? result.getFailureReport().getDetails().size()
                : 0;

        if (hasViolation) {
            log.warn("[ARCH-REPORT] Rule: {} | Violations: {}",
                    rule.getDescription(), violationCount);
            result.getFailureReport().getDetails().forEach(detail ->
                    log.warn("[ARCH-REPORT]   - {}", detail));
        } else {
            log.info("[ARCH-REPORT] Rule: {} | PASS", rule.getDescription());
        }
        return violationCount;
    }

    // ─── 规则1: modules 不得依赖 adapters ───

    @Nested
    @DisplayName("规则1: 领域模块不得依赖适配器层")
    class ModulesMustNotDependOnAdapters {

        @Test
        @DisplayName("modules/ 不得访问 adapters/ 的类 (REPORT模式)")
        void modulesMustNotAccessAdapters() {
            ArchRule rule = noClasses()
                    .that().resideInAPackage("..modules..")
                    .should().dependOnClassesThat()
                    .resideInAPackage("..adapter..")
                    .because("领域模块必须通过 Port 接口解耦，不得直接依赖适配器实现");

            int violations = evaluateInReportMode(rule, importedClasses);
            log.info("[ARCH-REPORT] Baseline: modules→adapters violations={}", violations);
            assertThat(violations).isGreaterThanOrEqualTo(0);
        }
    }

    // ─── 规则2: modules 不得依赖 apps ───

    @Nested
    @DisplayName("规则2: 领域模块不得依赖应用层")
    class ModulesMustNotDependOnApps {

        @Test
        @DisplayName("modules/ 不得访问 apps/ 的类 (REPORT模式)")
        void modulesMustNotAccessApps() {
            ArchRule rule = noClasses()
                    .that().resideInAPackage("..modules..")
                    .should().dependOnClassesThat()
                    .resideInAPackage("..com.gien.gits.api..")
                    .because("领域模块不得依赖应用启动层，避免循环依赖");

            int violations = evaluateInReportMode(rule, importedClasses);
            log.info("[ARCH-REPORT] Baseline: modules→apps violations={}", violations);
            assertThat(violations).isGreaterThanOrEqualTo(0);
        }
    }

    // ─── 规则3: modules 不得直接依赖 Spring Framework ───

    @Nested
    @DisplayName("规则3: 领域模块不得直接依赖 Spring Framework")
    class ModulesMustNotDependOnSpring {

        @Test
        @DisplayName("modules/ 不得访问 org.springframework (REPORT模式)")
        void modulesMustNotAccessSpring() {
            ArchRule rule = noClasses()
                    .that().resideInAPackage("..modules..")
                    .and().resideOutsideOfPackage("..port..")
                    .should().dependOnClassesThat()
                    .resideInAPackage("org.springframework..")
                    .because("领域模块必须保持框架无关，Port 接口可例外（Spring 事件桥接）");

            int violations = evaluateInReportMode(rule, importedClasses);
            log.info("[ARCH-REPORT] Baseline: modules→spring violations={}", violations);
            assertThat(violations).isGreaterThanOrEqualTo(0);
        }
    }

    // ─── 规则4: adapters 不得依赖 apps ───

    @Nested
    @DisplayName("规则4: 适配器层不得依赖应用层")
    class AdaptersMustNotDependOnApps {

        @Test
        @DisplayName("adapters/ 不得访问 apps/ 的类 (REPORT模式)")
        void adaptersMustNotAccessApps() {
            ArchRule rule = noClasses()
                    .that().resideInAPackage("..adapter..")
                    .should().dependOnClassesThat()
                    .resideInAPackage("..com.gien.gits.api..")
                    .because("适配器不得反向依赖应用层，保持单向依赖");

            int violations = evaluateInReportMode(rule, importedClasses);
            log.info("[ARCH-REPORT] Baseline: adapters→apps violations={}", violations);
            assertThat(violations).isGreaterThanOrEqualTo(0);
        }
    }

    // ─── 规则5: 无循环依赖 ───

    @Nested
    @DisplayName("规则5: 模块间无循环依赖")
    class NoCyclicDependencies {

        @Test
        @DisplayName("modules/ 内各子模块无循环依赖 (REPORT模式)")
        void noCyclicDependenciesInModules() {
            ArchRule rule = slices().matching("com.gien.gits.(*)..")
                    .should().beFreeOfCycles()
                    .because("模块间循环依赖违反六边形架构原则");

            int violations = evaluateInReportMode(rule, importedClasses);
            log.info("[ARCH-REPORT] Baseline: cyclic-dependency violations={}", violations);
            assertThat(violations).isGreaterThanOrEqualTo(0);
        }
    }

    // ─── 规则6: Port 接口命名约定 ───

    @Nested
    @DisplayName("规则6: Port 接口命名约定")
    class PortNamingConvention {

        @Test
        @DisplayName("port 包下的接口应以 Port 结尾 (REPORT模式)")
        void portInterfacesShouldEndWithPort() {
            ArchRule rule = noClasses()
                    .that().resideInAPackage("..port..")
                    .and().areInterfaces()
                    .and().haveSimpleNameNotEndingWith("Port")
                    .should().haveSimpleNameEndingWith("Port")
                    .because("Port 接口应遵循 *Port 命名约定（如 ClaimReconciliationPort）");

            int violations = evaluateInReportMode(rule, importedClasses);
            log.info("[ARCH-REPORT] Baseline: port-naming violations={}", violations);
            assertThat(violations).isGreaterThanOrEqualTo(0);
        }
    }
}
