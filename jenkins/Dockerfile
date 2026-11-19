FROM jenkins/jenkins:lts-jdk17
USER root
RUN apt-get update && apt-get install -y docker.io python3 python3-venv python3-pip unzip curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sL https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-linux-x64.zip -o /tmp/scanner.zip \
    && unzip -q /tmp/scanner.zip -d /opt \
    && ln -s /opt/sonar-scanner-*/bin/sonar-scanner /usr/local/bin/sonar-scanner \
    && rm /tmp/scanner.zip \
    && curl -sL https://github.com/jeremylong/DependencyCheck/releases/download/v11.1.0/dependency-check-11.1.0-release.zip -o /tmp/odc.zip \
    && unzip -q /tmp/odc.zip -d /opt \
    && rm /tmp/odc.zip
