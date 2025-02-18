#!/usr/bin/env bash

ORIGINAL="/nfs3m/css/curated01/g5nr/data/Ganymed/7km/c1440_NR/DATA/0.0625_deg/inst/inst30mn_3d_T_Nv/Y2006/M06/D15/c1440_NR.inst30mn_3d_T_Nv.20060615_2330z.nc4"

OUTDIR="experiments/"

if [ ! -f "$OUTDIR/original.nc" ]; then
  
    h5repack -S PAGE -G $((8 * 1024 * 1024)) $ORIGINAL $OUTDIR/original.nc
fi

VARIABLES="T"

# chunk_sizes=("1x4x67x480" "1x4x180x480" "1x6x67x480" "1x4x180x576" "1x4x67x640")
# chunk_sizes=("1x4x67x180" "1x4x43x240" "1x6x67x90" "1x4x180x576")
# chunk_sizes=("1x2x67x180" "1x3x67x180")
# chunk_sizes=("1x2x91x180" "1x2x182x360" "1x3x43x90")
# chunk_sizes=("1x2x67x120")
# chunk_sizes=("1x2x67x160" "1x2x67x144" "1x2x121x192" "1x2x144x240")
chunk_sizes=("1x2x67x160")
for chunk in "${chunk_sizes[@]}"; do
    echo "Processing chunk size: $chunk"
    h5repack \
        -S PAGE \
        -G $((8 * 1024 * 1024)) \
        -l $VARIABLES:CHUNK=$chunk \
        $ORIGINAL $OUTDIR/chunked-${chunk}.nc
done

size_ratio() {
  SORIG=$(du -sH "$OUTDIR/original.nc" | cut -f1)
  STARGET=$(du -sH $1 | cut -f1)
  RESULT=$(bc <<< "scale=3; $STARGET/$SORIG")
  echo "$1: $RESULT $SORIG $STARGET"
}

for fname in $OUTDIR/*.nc; do
  size_ratio $fname
done

compression_ratio() {
  echo "$1: $(h5dump -d /T -Hp $1 | grep 'COMPRESSION)' --color=never)"
}

for fname in $OUTDIR/*.nc; do
  compression_ratio $fname
done


