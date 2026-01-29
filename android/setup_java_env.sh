#!/bin/bash
# Script para configurar Java 17 no ambiente
# Execute: source setup_java_env.sh

export JAVA_HOME=/usr/local/opt/openjdk@17
export PATH=$JAVA_HOME/bin:$PATH

echo "✅ Java 17 configurado!"
echo "JAVA_HOME: $JAVA_HOME"
java -version


