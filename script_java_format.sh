in_folder=$1
out_folder=$2
answerer=$3
java_lib=$4
count=0

for file in $(find $in_folder -type f); do
  java -cp $java_lib org.lara.nlp.context.FacebookTest $file "$answerer" "$out_folder/conv_$count.txt"
  count=$(expr $count + 1)
done