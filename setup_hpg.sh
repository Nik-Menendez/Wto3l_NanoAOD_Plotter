export PYTHONPATH=${PYTHONPATH}:${PWD}/
export PATH=${PATH}:${PWD}/bin/
#export PYTHONPATH=/home/${USER}/.local/lib/python2.7/:$PYTHONPATH
export PYTHONPATH=/home/${USER}/.local/lib/python3.8/:$PYTHONPATH

export BASE_PATH=${PWD}

module load git cuda python/3.8
#python3 -c "import uproot"
