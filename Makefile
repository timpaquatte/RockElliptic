PATH_TO_GP_JAR=""

all: create_key install_card

create_keys:
	python ressources/generate_keys.py
	mv *.pem ressources/

install_card:
	ant
	java -jar $(PATH_TO_GP_JAR) -v --uninstall RockElliptic221.cap --params 4a6176614361726479
	java -jar $(PATH_TO_GP_JAR) -v --install RockElliptic221.cap --params 4a6176614361726479

clean:
	rm -f ressources/client_data.db ressources/*.pem