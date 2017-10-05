#!/bin/sh
#
# Script to peform a minor Fedora upgrade
#
# Prerequisite:
#
# A copy of the latest Fedora .war file uploaded to /data as fedora.war
#
# See: http://fedorarepository.org/download to download the latest .war
#
# Select the "Web Application with Authorization and Audit" version of Fedora
#
# Stop Tomcat
cd /data/tomcat/bin
./shutdown.sh
# Kill all the Java processes just in case
killall java
# Clean out Tomcat for new version
rm -rf /data/tomcat/logs/*
rm -rf /data/tomcat/components/*
rm -rf /data/tomcat/lib/*
rm -rf /data/tomcat/temp/*
rm -rf /data/tomcat/work/*
cd /data/tomcat/webapps
shopt -s extglob
rm -rf !(ROOT)
# Copy the original jars shipped with Tomcat 8
cp /data/tomcat-do-not-delete/apache-tomcat-8.0.29/lib/* /data/tomcat/lib/
export CATALINA_HOME=/data/tomcat
export JAVA_HOME=/usr/bin
export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/data/tomcat/bin
# Start a clean tomcat
cd /data/tomcat/bin
./startup.sh
# Sleep for 1 minute to allow for tomcat to start
sleep 1m
# Shutdown tomcat
./shutdown.sh
killall java
# Copy the new Fedora .war file to the webapps directory
cp /data/fedora.war /data/tomcat/webapps/fedora.war
# Start up Tomcat to deploy Fedora
./startup.sh
# Wait 5 minutes for Tomcat to start
sleep 5m
# Shutdown Tomcat
./shutdown.sh
killall java
# Clean out the Tomcat logs
rm -rf /data/tomcat/logs/*
# Copy the modified repository.json file to the appropriate location
cp /data/fedora/marist/repository.json /data/tomcat/webapps/fedora/WEB-INF/classes/config/jdbc-mysql/repository.json
# Copy the mysql connector to the appropriate location
cp /data/fedora/marist/mysql-connector-java-5.1.38-bin.jar /data/tomcat/webapps/fedora/WEB-INF/lib/mysql-connector-java-5.1.38-bin.jar
# Fix the links in /data/tomcat/webapps/fedora/index.html to make them work properly with where Fedora is installed
cd /data/tomcat/webapps/fedora
sed -i -- 's/static/\/fedora\/static/g' *.html
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.modeshape.configuration=file:/config/jdbc-mysql/repository.json"
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.mysql.username=rac_fedora"
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.mysql.password=xxxxxxxx"
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.mysql.host=db001.it.marist.cloud"
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.mysql.port=3306"
export JAVA_OPTS="${JAVA_OPTS} -Dfcrepo.binary.directory=/data/fedora-binaries"
export CATALINA_HOME=/data/tomcat
export JAVA_HOME=/usr/java
export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/data/tomcat/bin
cd /data/tomcat/bin
# Startup Tomcat
./startup.sh
#
# End of script (minor-fedora-upgrade.sh)
#

