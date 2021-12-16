#!/usr/bin/python

import csv, math, sys, re

###
# read csv in
###

def loadData(f):
    # define new array #1
    data = []
    # define new array #2
    refs = []
    
    i = 0
    for line in f:
        if "Abbreviations:" in line:
            i += 1
            continue

        line = line.replace('"','')

        if i < 1:
            data.append( line.split(",") )
      
        if i == 1:
            intereString = line.split(",,")
            refs.append( intereString[0] )

    return [data, refs]


###
# data: delete any row without value for TL(PPM)
###

def cleanData(f):
    data = []
    # find TL(PPM)
    index = f[0].index("TL(PPM)")
    
    for row in f:
        if row[index]: 
            data.append( row )
        else:
            continue
            
    data.sort() #TODO turn this into a more useful (int) sort?

    return data

###
# refs: [#, first surname + "et al.", year, linkified doi]
###

def cleanRefs(f, data):
    refs = [["GEOROC ID", "Authors", "Year", "DOI"]]
    
    for line in f:
        testSplit  = re.split("(?<=\])\s|\s\s+", line)
        
        # pull out the GEOROC_ID
        try:
            GEOROCID = testSplit[0]
        except:
            GEOROCID = ''
            
        # pull out the author list
        try:
            authors = testSplit[1]
        except:
            authors = ''

        # pull out the year
        yearPos = [i for i, item in enumerate(testSplit) if re.search(re.compile("\[\d{4}\]"), item)]
        try:
            year = testSplit[yearPos[-1]]
        except:
            year = ''

        # sort out the DOI
        doiPos = [i for i, item in enumerate(testSplit) if re.search(re.compile("^doi\:"), item)]
        try:
            doiField = testSplit[doiPos[0]].split()
            doi = doiField[1]
        except:
            doi = ''
        if doi != '':
            doiLink = "https://doi.org/doi/" + doi
        else:
            doiLink = ''
           
        # squish it all together! 
        refs.append( [GEOROCID, authors, year, doiLink] )
        
        # TODO discard any row that doesn't feature in the data lump?

    return refs

# ["GEOROC ID", "Authors", "", "Title", "Journal", "Year", "Pages", "DOI"]
#['"[24479]', 'REAGAN M. K., TURNER SIMON P., HANDLEY H. K., TURNER M. B., BEIER C., CAULFIELD J. T., PEATE D. W.:', '', '210PB-226RA DISEQUILIBRIA IN YOUNG GAS-LADEN MAGMAS', 'SCIENTIFIC REPORTS 7 (45186)', '[2017]', '', ' doi: 10.1038/srep45186"']

###
# actually do the thing!
###

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, "Usage: %s file.csv [file2.csv ...]" % sys.argv[0]
        sys.exit(1)

    files = sys.argv[1:]
    
    for filename in files:
        with open(filename, 'r') as f:
            [data, refs] = loadData(f)
            cleanedData = cleanData(data)
            cleanedRefs = cleanRefs(refs, cleanedData)

#    with open('data-out.csv', 'a') as f:
#            csvwriter = csv.writer(f)
#            for row in cleanedData:
#                csvwriter.writerow(row) 

    with open('refs-out.csv', 'a') as f:
            csvwriter = csv.writer(f)
            for row in cleanedRefs:
                csvwriter.writerow(row) 
