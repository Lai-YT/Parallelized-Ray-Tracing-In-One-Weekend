#!/usr/bin/env bash

export CMAKE_BUILD_TYPE="Release"
# CPUS="0-9,20-29"
# CPUS="10-19,30-39"

# CMD1="taskset -c ${CPUS} ./build/serial/InOneWeekend"
CMD1="./build/serial/InOneWeekend"
# CMD2="OMP_NUM_THREADS=22 taskset -c ${CPUS} ./build/openmp/OMPInOneWeekend"
CMD2="OMP_NUM_THREADS=22 ./build/openmp/OMPInOneWeekend"
# CMD3="taskset -c ${CPUS} ./build/cuda/CUDAInOneWeekend"
CMD3="./build/cuda/CUDAInOneWeekend"
SETUP='CUDAFLAGS="-DCUDA_BLOCK_SIZE=8 -DMAP_SIZE={map_size}" CXXFLAGS="-DMAP_SIZE={map_size}" cmake -B build --fresh . && cmake --build build'
hyperfine -w 3 -r 5 -P map_size 1 32 -D 1 --export-json=map_size.json --sort=command --shell=bash --setup "${SETUP}" "${CMD1}" "${CMD2}" "${CMD3}"
