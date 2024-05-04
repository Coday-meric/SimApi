#!/bin/bash


#Dossier de base
dir=../data/video
dir_timestamp=../data/temp_var
filename="$dir_timestamp/timestamp.txt"
date_log=$(date '+%d/%m/%Y %r')

#Time for save temp video
timestamp_save=$((648900))


if [ ! -f $filename ]
then
    touch $filename
fi

#Récupération du dernier timestamp de transfer

timestamp_modif=$(cat "$filename")

if [ "$timestamp_modif" == '' ]
then
    echo "1577833200" > "$filename"
    timestamp_modif=$(cat "$filename")
fi

#Ecriture du timestamp 
timestamp_final=$(date +%s)
echo "$timestamp_final" > "$filename"

echo '------------------------------------'
echo '------------------------------------'
echo '------------------------------------'
echo '---- Nouvelle synchronisation ! ----'
echo '------------------------------------'
echo '------------------------------------'
echo 'Date :' $date_log
echo '------------------------------------'
echo '------------------------------------'
echo "Dernier transfer: "$timestamp_modif
echo '------------------------------------'
echo '------------------------------------'
echo "Délai de temp: "$timestamp_save
echo '------------------------------------'
echo '------------------------------------'
echo '------------------------------------'

for video in $dir/*
do
   #Nom du fichier apres son répertoire
   destVideo=$(basename "$video")
   #Nom du répertoire
   srcVideo=$(dirname $video)

   #Récupération du timestamp de dérniere modif de la vidéo
   timestamp=$(stat -c '%Y' "$dir/$destVideo")

   #Calcul timestamp limite de stockage temp
   timestamp_sm=$(($timestamp_modif - $timestamp_save))

   #Suppression du temp si la limite est dépassée
   if [ "$timestamp" -lt "$timestamp_sm" ]
   then
      echo "Video a plus de une semaine, suppression :" $video
      rm "$dir/$destVideo"
      continue
   fi

   #Verifie que la vidéo n'es pas deja etais upload
   if [ "$timestamp" -lt "$timestamp_modif" ]
   then
      echo "Vidéo deja traité :" $video
      continue
   fi

   jour=$(date -d @"$(echo $timestamp)" +'%Y-%m-%d')
   mois=$(date -d @"$(echo $timestamp)" +'%m.%y')
   semaine=$(date --date=$jour +"%V")
   annee=$(date -d @"$(echo $timestamp)" +'%Y')
   
   #Remplacement des espaces pour URL
   echo "$destVideo"|sed -e 's/ /%20/g'
   
   #Chemin de la destination et debug
   destnext="$(echo "$url_nextcloud")remote.php/dav/files/$(echo "$login")/$(echo "$directory")$(echo "$annee")/Semaine-$semaine%20le%20$mois/$(echo "$destVideo"|sed -e 's/ /%20/g')"
   

   #Execution de la commande de transfert
   log=$(curl -u $login:$password -T "$video" "$(echo "$url_nextcloud")remote.php/dav/files/$(echo "$login")/$(echo "$directory")$(echo "$annee")/Semaine-$semaine%20le%20$mois/$(echo "$destVideo"|sed -e 's/ /%20/g')")
   echo $log
   
   #Debug
   echo "Nom video : "$destVideo
   echo "Timestamp de la derniére modification de la vidéo: "$timestamp
   echo "Chemin complet : "$video
   echo "La semaine : "$semaine
   echo "Le mois annee : "$mois
   echo "L'année: "$annee
   echo "Destination finale : "$destnext

done
