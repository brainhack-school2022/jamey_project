
#BIDS RELATED CODE 

##go to project folder where conda environment is
cd /Users/kevinjamey/Documents/dcm2bidsProj 

##Activate conda
conda activate dcm2bids

##check that cdm2bids works properly
dcm2bids --help

#run one participant with code and session using the config file
dcm2bids -d sourcedata/ -p 09 -s 02 -c code/dcm2bids_config.json

#explore how to run multiple subjects in BASH
bidsdir= /Users/kevinjamey/Documents/dcm2bidsProj/mtDataTest
subdir= /Users/kevinjamey/Documents/dcm2bidsProj/mtDataTest/sourcedata

bidsdir= /Users/kevinjamey/Documents/dcm2bidsProj/mtDataTest
subdir= /Users/kevinjamey/Documents/dcm2bidsProj/mtDataTest/sourcedata

for subject in ${subdir}; do
    dcm2bids \
        -d ${bidsdir}/sourcedata/${subject} \
        -p ${subject} \
        -c ${bidsdir}/code/dcm2bids_config.json
        done

for subject in *; do
    dcm2bids \
        -d sourcedata/${subject} \
        -p ${subject} \
        -c code/dcm2bids_config.json
        done 


for subject in */ ; do
    echo "$subject"
done

##explore how create subject name and session from folder title

