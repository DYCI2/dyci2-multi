VERSION_JIM=20061123_bin
WEKA=weka.jar
CLASSPATH=jim$VERSION_JIM.jar:commons-cli-1.0.jar:$WEKA:corporaxml.jar:corpora.jar

#MODEL=trained_with_200folders.mdl
MODEL=all_corpora.mdl
java -Xmx4096m -cp $CLASSPATH es.ua.dlsi.im.mains.ExtractMelodyTrack -model $MODEL $* 