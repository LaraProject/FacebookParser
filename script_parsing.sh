fb_folder=$1
out_folder=$2
answerer=$3
fb_parser=$4
count=0

for file in $(find $fb_folder -type f -name "message_*.json"); do
  python $fb_parser $file "$answerer" --nbMessages 999999 --export "$out_folder/message_$count.js"
  count=$(expr $count + 1)
done