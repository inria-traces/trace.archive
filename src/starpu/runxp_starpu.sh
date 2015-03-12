#!/bin/bash
# Script for running StarPU experiments

set -e # fail fast

# Script parameters
basename="$PWD"
host="$(hostname | sed 's/[0-9]*//g' | cut -d'.' -f1)"
capture_metadata="/home/stanisic/Repository/trace.archive/src/capture_metadata.sh"
template_index="/home/stanisic/Repository/trace.archive/src/template_index.org"

datafolder="/home/stanisic/Repository/trace.archive/data/testing"
starpu_build="/home/stanisic/Repository/git_gforge/starpu-simgrid/src/StarPU/build-native"
help_script()
{
    cat << EOF
Usage: $0 options

Script for running StarPU experiments

OPTIONS:
   -h      Show this message
   -d      Specify output data folder
   -s      Path to the StarPU installation

Example how to run it:
STARPU_NCPU=4 STARPU_NCUDA=0 STARPU_NOPECL=0 STARPU_SIZE=9600 STARPU_BLK=10 STARPU_SCHED=dmda STARPU_CALIBRATE=1 STARPU_PROGRAM=cholesky ./runxp_starpu.sh -d /home/stanisic/Repository/trace.archive/data/testing/ -s /home/stanisic/Repository/git_gforge/starpu-simgrid/src/StarPU/build-native/
EOF
}
# Parsing options
while getopts "d:s:h" opt; do
    case $opt in
	d)
	    datafolder="$OPTARG"
	    ;;
	s)
	    starpu_build="$OPTARG"
	    ;;
	h)
	    help_script
	    exit 4
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG"
	    help_script
	    exit 3
	    ;;
    esac
done
info="$datafolder/info.org"

# Reading StarPU command line arguments
ncpu=$STARPU_NCPU
if [[ -z $ncpu ]]; then
    ncpu="4"
fi
ncuda=$STARPU_NCUDA
if [[ -z $ncuda ]]; then
    ncuda="0"
fi
nopencl=$STARPU_NOPENCL
if [[ -z $nopencl ]]; then
    nopencl="0"
fi
nsize=$STARPU_SIZE
if [[ -z $nsize ]]; then
    nsize="9600"
fi
nblk=$STARPU_BLK
if [[ -z $nblk ]]; then
    nblk="10"
fi
starpu_home=$STARPU_HOME
if [[ -z $starpu_home ]]; then
    starpu_home=$datafolder
fi
starpu_hostname=$STARPU_HOSTNAME
if [[ -z $starpu_hostname ]]; then
    starpu_hostname=$(hostname)
fi
starpu_sched=$STARPU_SCHED
if [[ -z $starpu_sched ]]; then
    starpu_sched="dmda"
fi
starpu_calibrate=$STARPU_CALIBRATE
if [[ -z $starpu_calibrate ]]; then
    starpu_calibrate="1"
fi
starpu_history_max_error=$STARPU_HISTORY_MAX_ERROR
if [[ -z $starpu_history_max_error ]]; then
    starpu_history_max_error="5"
fi
starpu_cpuid=$STARPU_WORKERS_CPUID 
if [[ -z $starpu_cpuid ]]; then
    starpu_cpuid=""
else
    ncpu="$ncpu STARPU_WORKERS_CPUID=\"$STARPU_WORKERS_CPUID\""
fi

# To choose which program to run
starpu_program=$STARPU_PROGRAM
starpu_program_binary="./examples/cholesky/.libs/cholesky_implicit"
case $starpu_program in
    'cholesky' | '$starpu_build/examples/cholesky/cholesky_implicit')
        starpu_program="$starpu_build/examples/cholesky/cholesky_implicit" 
	starpu_program_binary="$starpu_build/examples/cholesky/.libs/cholesky_implicit"
        ;;   
    'lu' | '$starpu_build/examples/lu/lu_example_float')
        starpu_program="$starpu_build/examples/lu/lu_example_float" 
	starpu_program_binary="$starpu_build/examples/lu/.libs/lu_example_float"
        ;;           
    *)
        starpu_program="$starpu_build/examples/cholesky/cholesky_implicit" 
	starpu_program_binary="$starpu_build/examples/cholesky/.libs/cholesky_implicit"
esac

#################################################################
# Checking if everything is commited
if git diff-index --quiet HEAD --; then
    echo "Everything is commited"
else
    echo "ERROR-need to commit all changes before doing experiment!"
    git status
    #exit 1
fi

##################################################
# Exporting FxT path
case ${host} in
    'winnetou')
	export FXT_PATH=/home/stanisic/Repository/FxT
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/stanisic/Repository/FxT/lib
	;;
    'paul-bdx' | 'attila' | 'hannibal' | 'conan' | 'mirage' | 'fourmi')
        ;;
    'frog' | 'frogkepler' )
	export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/home/stanisic/FxT/lib/pkgconfig
        ;;
    'pilipili' | 'uv')
        export FXT_PATH=/home/stanisic/fxt-0.2.11
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/stanisic/fxt-0.2.11/lib
        ;;
    'idgraf')
        export FXT_PATH=/home/lukstanisic/fxt-0.2.11
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lukstanisic/fxt-0.2.11/lib
        ;;
    *)
        echo "New machine: be sure FxT flags are correct!"
esac

##################################################
# Starting to write output file and getting all metadata
title="StarPU execution on $(eval hostname)"
$capture_metadata -s $starpu_build -t "$title" $info

##################################################
# Compilation
echo "* COMPILATION" >> $info
# Configure and make StarPU+Simgrid
cd $starpu_build
echo "Make distclean..."
set +e #If there is nothing to clean
make -i distclean > /dev/null
set -e
# Configure and make StarPU
echo "** CONFIGURATION OF STARPU:" >> $info
configopt=""
case ${host} in
    'paul-bdx' | 'attila' | 'hannibal' | 'conan' | 'pilipili')
	;;
    'winnetou' )
	;;
    'fourmi' | 'mirage')
	configopt="--disable-build-doc --disable-socl --disable-gcc-extensions
--disable-opencl --with-mkl-cflags=\"-I$MKLROOT/include\" --with-mkl-ldflags=\"-Wl,--start-group $MKLROOT/lib/intel64/libmkl_intel_lp64.so $MKLROOT/lib/intel64/libmkl_sequential.so $MKLROOT/lib/intel64/libmkl_core.so -Wl,--end-group -lpthread -lm\""
        ;;
    'frog' | 'frogkepler')
	configopt="BLAS_LIBS=\"-L/applis/site/stow/gcc_4.4.6/atlas_3.11.17/lib -lsatlas\"" 
	;;
    'uv')
	configopt="--enable-maxcpus=192 --enable-max-sched-ctxs=192 --enable-maxbuffers=192 --with-mkl-cflags=\"-I$MKLROOT/include\" --with-mkl-ldflags=\"-Wl,--start-group $MKLROOT/lib/intel64/libmkl_intel_lp64.so $MKLROOT/lib/intel64/libmkl_sequential.so $MKLROOT/lib/intel64/libmkl_core.so -Wl,--end-group -lpthread -lm\""
	;;
    'idgraf')
	configopt="--disable-build-doc --enable-maxcudadev=8"
	;;
    *)
        echo "New machine: be sure config options are correct!"
esac
echo "Configure..."
echo "#+BEGIN_EXAMPLE" >> $info    
eval ../configure --prefix=$starpu_build --with-fxt=$FXT_PATH --enable-paje-codelet-details $configopt >> $info
echo "#+END_EXAMPLE" >> $info
echo "** COMPILATION OF STARPU" >> $info
echo "Make..."
echo "#+BEGIN_EXAMPLE" >> $info    
make -j5 >> $info
make install
echo "#+END_EXAMPLE" >> $info
echo "** PROGRAM SCRIPT" >> $info
echo "#+BEGIN_EXAMPLE" >> $info
cat $starpu_program >> $info
echo "#+END_EXAMPLE" >> $info
echo "** PROGRAM BINARY LIBRARIES" >> $info
echo "#+BEGIN_EXAMPLE" >> $info
ldd $starpu_program_binary >> $info
echo "#+END_EXAMPLE" >> $info

##################################################
# Prepare running options
cd $datafolder
running="STARPU_HOME=$starpu_home STARPU_HOSTNAME=$starpu_hostname STARPU_HISTORY_MAX_ERROR=$starpu_history_max_error STARPU_GENERATE_TRACE=1 STARPU_CALIBRATE=$starpu_calibrate STARPU_NCPU=$ncpu STARPU_NCUDA=$ncuda STARPU_NOPENCL=$nopencl STARPU_SCHED=$starpu_sched $starpu_program -size $nsize -nblocks $nblk"

#################################
# Run application
echo "* RUNNING OPTIONS" >> $info
echo "#+BEGIN_EXAMPLE" >> $info
echo $running >> $info
echo "#+END_EXAMPLE" >> $info
echo "Execute..."
# Writing results
rm -f stdout.out
rm -f stderr.out
time1=$(date +%s.%N)
set +e # In order to detect and print execution errors
eval $running 1> stdout.out 2> stderr.out
set -e
time2=$(date +%s.%N)
echo "* ELAPSED TIME" >> $info
echo "#+BEGIN_EXAMPLE" >> $info
echo "Elapsed:    $(echo "$time2 - $time1"|bc ) seconds" >> $info
echo "#+END_EXAMPLE" >> $info
echo "* STDERR OUTPUT" >> $info
echo "#+BEGIN_EXAMPLE" >> $info
cat stderr.out >> $info
if [ ! -s stdout.out ]; then
    echo "ERROR DURING THE EXECUTION!!!" >> stdout.out
fi
echo "#+END_EXAMPLE" >> $info
echo "* STDOUT OUTPUT" >> $info
echo "#+BEGIN_EXAMPLE" >> $info
(echo -n "Makespan (in ms): "; cat stdout.out) >> $info
cat stderr.out
echo -n "Makespan (in ms): "
cat stdout.out
echo "#+END_EXAMPLE" >> $info

##################################
# StarPU calibration used for this experiment
echo "* CALIBRATION" >> $info
find $starpu_home/.starpu -not -iwholename '*~' -name *$host* -printf "** %f\n#+BEGIN_EXAMPLE\n%p\n " -exec cat {} \; -printf "#+END_EXAMPLE\n" >> $info

##################################
# Copy template to index.org
cp $template_index $datafolder/index.org
