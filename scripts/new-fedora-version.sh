#!/bin/sh
# Stop Tomcat
cd /data/tomcat8/bin
./shutdown.sh
# Kill all the Java processes just in case
killall java
# Clean out Tomcat for new version
rm -rf /data/tomcat8/logs/*
rm -rf /data/tomcat8/components/*
rm -rf /data/tomcat8/lib/*
rm -rf /data/tomcat8/temp/*
rm -rf /data/tomcat8/work/*
cd /data/tomcat8/webapps
shopt -s extglob
rm -rf !(ROOT)
# Copy the original jars shipped with Tomcat 8  
cp /data/tomcat-do-not-delete/apache-tomcat-8.0.29/lib/* /data/tomcat8/lib/
export CATALINA_HOME=/data/tomcat8
export JAVA_HOME=/data/java
export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/data/tomcat8/bin:/data/java/bin
# Start a clean tomcat
cd /data/tomcat8/bin
./startup.sh
# Sleep for 1 minute to allow for tomcat to start
sleep 1m
# Shutdown tomcat
./shutdown.sh
killall java
# Copy the new Fedora .war file to the webapps directory
cp /data/fedora.war /data/tomcat8/webapps/fedora.war
# Start up Tomcat to deploy Fedora
./startup.sh
# Sleep 5 minutes for Tomcat to start (This will also start Fedora)
sleep 5m
# Shutdown Tomcat
./shutdown.sh
killall java
# Clean out the Tomcat logs
rm -rf /data/tomcat8/logs/*
# Copy the modified repository.json file to the appropriate location
cp /data/fedora/marist/repository.json /data/tomcat8/webapps/fedora/WEB-INF/classes/config/jdbc-mysql/repository.json
# Copy the mysql connector to the appropriate location
cp /data/fedora/marist/mysql-connector-java-5.1.38-bin.jar /data/tomcat8/webapps/fedora/WEB-INF/lib/mysql-connector-java-5.1.38-bin.jar

