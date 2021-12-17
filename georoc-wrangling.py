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

    # grab header
    header = [data[0]]

    # sort by first GEOROCID in first column, ignoring header row
    body = sorted(data[1:], key = lambda i: int( re.split('\[|\]', i[0])[1] ) )

    # grab all the reference numbers for good measure
    refNos = []
    for row in data[1:]:
        newNos = filter( None, re.split('\D', row[0]) ) # filter() drops ''
        for i in newNos:
                refNos.append( i )
    
    refNos = list(set(refNos)) # condense list down to unique values
    
    sortedData = header + body
    
    return refNos, sortedData

###
# refs: [#, first surname + "et al.", year, linkified doi]
###

def cleanRefs(f, data, refNos):
    refs = [["GEOROC ID", "Authors", "Year", "DOI", "Title"]]
    
    for line in f:
        testSplit  = re.split("(?<=\])\s|\s\s+", line) #TODO add filter(None, testSplit)???
        
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
            
        # sort out the title...
        try:
            title = testSplit[2]
        except:
            title = ''
           
        # discard any reference not in cleanedData & squish it all together!
        try:
            testID = str(re.split('\D', GEOROCID)[1])
           
            if testID in refNos:
                print "Match!"
                refs.append( [GEOROCID, authors, year, doiLink, title] )
            else:
                print "No match!"
        except:
            continue

    return refs

###
# actually do the thing!
###

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, "Usage: %s file.csv [file2.csv ...]" % sys.argv[0]
        sys.exit(1)

    files = sys.argv[1:]
    
    for filename in files:
    
        name = filename.split('.')[0] 
        dataName = "%s_data.csv" % name
        refsName = "%s_refs.csv" % name
    
        with open(filename, 'r') as f:
            [data, refs] = loadData(f)
            [refNos, cleanedData] = cleanData(data)
            cleanedRefs = cleanRefs(refs, cleanedData, refNos)

        with open(dataName, 'w') as f:
            csvwriter = csv.writer(f)
            for row in cleanedData:
                csvwriter.writerow(row) 

        with open(refsName, 'w') as f:
            csvwriter = csv.writer(f)
            for row in cleanedRefs:
                    csvwriter.writerow(row) 
