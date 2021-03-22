dir=$1
# example: dir = $dir
enc_type=$2
enc="enc05"
pk2="0.9" #[.3, .5, .9]
pgeo="0.9" #[.4, .5, .9]

org_dir=$dir/original
enc_dir=$dir/$enc_type
# mkdir -p enc_dir
for f in $org_dir/*.bench
do
	g=${f##*/}
	ckt=${g%.*}

	bench="$dir/${enc_type}/${ckt}_${enc}.bench"
	cnf="$dir/${enc_type}/${ckt}_${enc}.cnf"

	python3 /home/hduser/OneDrive/satconda/bench2cnf.py -b ${bench} -c ${cnf} 
	# start time of SATConda
	SECONDS=0

	python3 /home/hduser/OneDrive/satconda/sat-2-unsat.py -c ${cnf} -pk2 ${pk2} -pgeo ${pgeo}


	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CNF to bench Conversion:

	python3 /home/hduser/OneDrive/satconda/cnf2bench_v3.py -b ${bench} -c $dir/${enc_type}/${ckt}_${enc}_unsat.cnf
	# end time of SATConda
	duration=$SECONDS

	echo "benchmark: ${ckt} time: $duration" > $enc_dir/algrthm.txt


	# # SAT ATTACK
	echo "Starting SAT Attack"
	echo "Program Timeout is 10 Hours"

	# SAT attack
	gnome-terminal -x sh -c \
	  'echo "SAT $1"; /home/hduser/host15-logic-encryption/bin/sld "$2" "$3"; exec bash' \
	  sh "$ckt" "${enc_dir}/${ckt}_${enc}_unsat_bench.bench" "$f"
	# APPSAT attack
	# gnome-terminal -x sh -c \
	#   'echo "AppSAT $1"; /home/hduser/host15-logic-encryption/bin/sld "$2" "$3" "$4"; exec bash' \
	#   sh "$ckt" "-a 12" "${enc_dir}/${ckt}_${enc}_unsat_bench.bench" "$f"
done
echo "Decryption Done"

# gnome-terminal -- /bin/sh -c 'echo hello world; sleep 1; exec bash'


