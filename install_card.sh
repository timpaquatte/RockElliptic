#!/bin/sh

PATH_TO_GP_JAR=""

ant
java -jar "$PATH_TO_GP_JAR" -v --uninstall RockElliptic221.cap --params 4a6176614361726479
java -jar "$PATH_TO_GP_JAR" -v --install RockElliptic221.cap --params 4a6176614361726479
