# Giai đoạn 1: Build file .jar
FROM maven:3.9.4-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
# Build bỏ qua test để chạy nhanh hơn
RUN mvn clean package -DskipTests

# Giai đoạn 2: Chạy file .jar
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
# Copy file .jar từ giai đoạn 1 sang
COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]