
################### TO MODIFY ###################

# Path to a directory containing these files:
# * java_card_kit-2_2_1
# * java_card_kit-2_2_2
# * ant-javacard.jar
PATH_JAVACARD_DIR=""

# Path to gp.jar
PATH_GP_JAR=""

#################################################


if PATH_GP_JAR == "" or PATH_JAVACARD_DIR == "":
  print("/!\ You have to fill the path to the different libraries in the file configure.py")
  exit(-1)


# Write build.xml
if PATH_JAVACARD_DIR[-1] != '/':
  PATH_JAVACARD_DIR += '/'
file = open("build.xml", "w")
content_build_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<project basedir="." default="rockelliptic" name="RockElliptic by pakat">
  <!-- Applet building dependencies -->
  <property name="JC221" value="%sjava_card_kit-2_2_1"/>
  <property name="JC222" value="%sjava_card_kit-2_2_2"/>

  <!-- ant-javacard task from javacard.pro -->
  <taskdef name="javacard" classname="pro.javacard.ant.JavaCard" classpath="%sant-javacard.jar"/>
  <!-- All included applets -->
  <target name="rockelliptic">
    <javacard>

      <cap jckit="${JC221}" output="RockElliptic221.cap" sources="src/rockelliptic">
        <applet class="rockelliptic.RockElliptic" aid="0102030405093270"/>
      </cap>

    </javacard>
  </target>
</project>''' % (PATH_JAVACARD_DIR, PATH_JAVACARD_DIR, PATH_JAVACARD_DIR)
file.write(content_build_xml)
file.close()

# Write the Makefile
file = open("Makefile", "w")
content_makefile = '''PATH_TO_GP_JAR="/home/tim/INF648_Embedded_security/DevJavaCard/tools/GlobalPlatformPro/gp.jar"

all: create_keys install_card

create_keys:
	python ressources/generate_keys.py
	mv *.pem ressources/

install_card:
	ant
	java -jar $(PATH_TO_GP_JAR) -v --uninstall RockElliptic221.cap --params 4a6176614361726479
	java -jar $(PATH_TO_GP_JAR) -v --install RockElliptic221.cap --params 4a6176614361726479

clean:
	rm -f ressources/client_data.db ressources/*.pem'''

file.write(content_makefile)
file.close()