# ---- Stage 1: Build ----
FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /app

# 先复制pom.xml利用Docker层缓存
COPY pom.xml .
COPY modules/operational-ontology/pom.xml modules/operational-ontology/pom.xml
COPY modules/semantic-runtime/pom.xml modules/semantic-runtime/pom.xml
COPY modules/context-evidence/pom.xml modules/context-evidence/pom.xml
COPY modules/human-action/pom.xml modules/human-action/pom.xml
COPY modules/evaluation/pom.xml modules/evaluation/pom.xml
COPY modules/scenario-customer-journey/pom.xml modules/scenario-customer-journey/pom.xml
COPY modules/knowledge-architecture/pom.xml modules/knowledge-architecture/pom.xml
COPY scenario/execute/pom.xml scenario/execute/pom.xml
COPY adapters/semantic-jena/pom.xml adapters/semantic-jena/pom.xml
COPY adapters/persistence-relational/pom.xml adapters/persistence-relational/pom.xml
COPY adapters/oracle-source/pom.xml adapters/oracle-source/pom.xml
COPY adapters/knowledge-filesystem/pom.xml adapters/knowledge-filesystem/pom.xml
COPY apps/api/pom.xml apps/api/pom.xml
COPY apps/worker/pom.xml apps/worker/pom.xml

# 下载依赖（利用缓存层）
RUN mvn --batch-mode --no-transfer-progress dependency:go-offline

# 复制全部源码并构建
COPY . .
RUN mvn --batch-mode --no-transfer-progress -pl apps/api -am package -DskipTests

# ---- Stage 2: Runtime ----
FROM eclipse-temurin:21-jre-jammy

LABEL maintainer="GITS Team" \
      description="GITS Knowledge Engineering API" \
      version="0.1.0-SNAPSHOT"

WORKDIR /app

COPY --from=build /app/apps/api/target/*.jar app.jar

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["exec", "java", "-jar", "app.jar"]
