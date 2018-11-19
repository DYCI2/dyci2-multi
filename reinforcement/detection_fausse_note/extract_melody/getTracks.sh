song_dir=$1
output_dir=$2"acc/"
melody_dir=$2"mel/"

if [ ! -d $output_dir ]; then
  mkdir $output_dir
fi
if [ ! -d $melody_dir ]; then
  mkdir $melody_dir
fi

for file in $1; do
  temp=`basename $file`
  output_file=$output_dir$temp
  num_tracks=`./extract_melody.sh -input $file  \
                      -output $melody_dir -tagged \
                      | grep --color "\->" \
                      | awk -F "\->" '{print $1}'`

  # Midi to csv
  ./midicsv-1.1/midicsv $1 > "temp.csv"

  # Remove tracks
  python removeTracks.py $num_tracks

  # Csv to midi
  ./midicsv-1.1/csvmidi "output.csv" > $output_file
done
