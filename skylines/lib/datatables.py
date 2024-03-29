# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import desc


def GetDatatableRecords(kw, querySet, columnIndexNameMap):
    """
    Usage:
            kw: args passed from dataTables query
            querySet: query set to draw data from.
            columnIndexNameMap: field names in order to be displayed.

    """

    # Get the number of columns
    #cols = int(kw.get('iColumns', 0))
    # Safety measure.
    iDisplayLength = min(int(kw.get('iDisplayLength', 50)), 100)
    # Where the data starts from (page)
    startRecord = int(kw.get('iDisplayStart', 0))
    # where the data ends (end of page)
    endRecord = startRecord + iDisplayLength

    # Pass sColumns
    keys = columnIndexNameMap.keys()
    keys.sort()
    colitems = [columnIndexNameMap[key] for key in keys]
    sColumns = ",".join(map(str, colitems))

    # Ordering data
    iSortingCols = int(kw.get('iSortingCols', 0))
    asortingCols = []

    if iSortingCols:
        for sortedColIndex in range(0, iSortingCols):
            sortedColID = int(kw.get('iSortCol_' + str(sortedColIndex), 0))
            # make sure the column is sortable first
            if kw.get('bSortable_{0}'.format(sortedColID), 'false') == 'true':
                sortedColName = columnIndexNameMap[sortedColID]
                sortingDirection = kw.get('sSortDir_' + str(sortedColIndex), 'asc')
                if sortingDirection == 'desc':
                    asortingCols.append(desc(getattr(sortedColName[0], sortedColName[1])))
                else:
                    asortingCols.append(getattr(sortedColName[0], sortedColName[1]))

        querySet = querySet.order_by(*asortingCols)

#    # Determine which columns are searchable
#    searchableColumns = []
#    for col in range(0,cols):
#        if request.GET.get('bSearchable_{0}'.format(col), False) == 'true': searchableColumns.append(columnIndexNameMap[col])
#
#    # Apply filtering by value sent by user
#    customSearch = request.GET.get('sSearch', '').encode('utf-8');
#    if customSearch != '':
#        outputQ = None
#        first = True
#        for searchableColumn in searchableColumns:
#            kwargz = {searchableColumn+"__icontains" : customSearch}
#            outputQ = outputQ | Q(**kwargz) if outputQ else Q(**kwargz)
#        querySet = querySet.filter(outputQ)
#
#    # Individual column search
#    outputQ = None
#    for col in range(0,cols):
#        if request.GET.get('sSearch_{0}'.format(col), False) > '' and request.GET.get('bSearchable_{0}'.format(col), False) == 'true':
#            kwargz = {columnIndexNameMap[col]+"__icontains" : request.GET['sSearch_{0}'.format(col)]}
#            outputQ = outputQ & Q(**kwargz) if outputQ else Q(**kwargz)
#    if outputQ: querySet = querySet.filter(outputQ)

    # count how many records match the final criteria
    iTotalRecords = iTotalDisplayRecords = querySet.count()
    # get the slice
    querySet = querySet[startRecord:endRecord]
    # required echo response
    sEcho = int(kw.get('sEcho', 0))

#    a = querySet.values()
#    for row in a:
#        rowkeys = row.keys()
#        rowvalues = row.values()
#        rowlist = []
#        for col in range(0,len(colitems)):
#            for idx, val in enumerate(rowkeys):
#                if val == colitems[col]:
#                    rowlist.append(str(rowvalues[idx]))
#        aaData.append(rowlist)

    response_dict = {}
    response_dict.update({'sEcho': sEcho, 'iTotalRecords': iTotalRecords,
                          'iTotalDisplayRecords': iTotalDisplayRecords,
                          'sColumns': sColumns})

    return (querySet, response_dict)
