#/home/rhassa2/OneDrive/satconda/satconda_script_v2.sh
# setup variable
ppa_dir=$1

ppa_base=$(basename ${ppa_dir})
# ckt=$1 #{c432, c499, c880, c880, c1355, c1908, c2670, c3540, c5315, c7552}
# enc_type=$2  # {iolts14 or dac12}

# enc="enc05"
# pk2="0.3"
# pgeo="0.4"
# #IOLTS'14
# bench="/home/rhassa2/host15-logic-decryption/benchmarks/${enc_type}/${ckt}_${enc}.bench"
# cnf="/home/rhassa2/host15-logic-decryption/benchmarks/${enc_type}/${ckt}_${enc}.cnf"

# Copy all the bench file to a directory:
# 1.

# cp /home/rhassa2/host15-logic-decryption/benchmarks/iolts14/*enc05_unsat_bench.bench /home/rhassa2/host15-logic-decryption/benchmarks/iolts14/iolts_enc05_3_4/

# 2. convert benchfile to verilog 
python3 /home/rhassa2/OneDrive/satconda/toverilog.py -b ${ppa_dir}

# 3. upload the verilog file to zeus:
scp -r ${ppa_dir} rhassa2@zeus.vse.gmu.edu:~/satconda/DC/source/

# 4. modify overhead_ppa according to the ppa_dir
python3 /home/rhassa2/OneDrive/satconda/overhead_ppa.py -tcl /home/rhassa2/OneDrive/satconda/overhead_ppa.tcl -dir ${ppa_dir}

# 5. upload the overhead_ppa to zeus
scp /home/rhassa2/OneDrive/satconda/overhead_ppa_new.tcl rhassa2@zeus.vse.gmu.edu:/home/rhassa2/satconda/DC/scripts/

# ssh rhassa2@zeus.vse.gmu.edu "bash --login -c 'module add Synopsys'"

# ssh rhassa2@zeus.vse.gmu.edu << EOF
# # bash --login -c 'source ~/.bash_profile'
# "bash --login -c 'dc_shell -f ~/satconda/DC/scripts/overhead_ppa_new.tcl'"

# # cd ~/satconda/DC/work/
# # dc_shell -f ~/satconda/DC/scripts/overhead_ppa_new.tcl >& output_file
# EOF

# ssh rhassa2@zeus.vse.gmu.edu "bash --login -c 'dc_shell'"
# 6. login to zues and calculate ppa:
ssh rhassa2@zeus.vse.gmu.edu "bash --login -c 'dc_shell -f ~/satconda/DC/scripts/overhead_ppa_new.tcl >& ~/dc_log.txt'"

# exit

scp -r  rhassa2@zeus.vse.gmu.edu:~/satconda/DC/results/${ppa_base} /home/rhassa2/OneDrive/satconda/TC_2020/

# scp -r  rhassa2@zeus.vse.gmu.edu:~/dc_log.txt /home/rhassa2/OneDrive/satconda/DAC_20_OVERHEAD/${ppa_base}/

scp -r  rhassa2@zeus.vse.gmu.edu:~/dc_log.txt /home/rhassa2/OneDrive/satconda/TC_2020/${ppa_base}/

# module add synopsys
# module load DesignCompiler/L-2016.03-SP3
# module add Synopsys
# module add PrimeTime/D-2010.06-SP3-6