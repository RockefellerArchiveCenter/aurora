#!/bin/sh
#
# Script to restart the Fedora application
#
# Stop Tomcat
cd /data/tomcat/bin
./shutdown.sh
# Kill all the Java processes just in case
killall java
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.modeshape.configuration=file:/config/jdbc-mysql/repository.json"
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.mysql.username=rac_fedora"
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.mysql.password=xxxxxxxx"
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.mysql.host=db001.it.marist.cloud"
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.mysql.port=3306"
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.binary.directory=/data/fedora-binaries"
export CATALINA_HOME=/data/tomcat
export JAVA_HOME=/usr/bin
export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/data/tomcat/bin
cd /data/tomcat/bin
# Startup Tomcat
./startup.sh
#
# End of script (restartfedora.sh)
#

