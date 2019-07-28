ls test | while read name
do
	echo ${name} >> run.log
	./obj/main ./test/${name} > ./result/${name%%.*}.txt 2>> run.log
	if [ $? -ne 0 ]
	then
		echo ${name}
	fi
done
