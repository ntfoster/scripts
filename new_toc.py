import scribus

num_pages = scribus.pageCount()
scribus.gotoPage(1)
i = 7
text= []
while (i <= 10):
    scribus.gotoPage(i)
    items = scribus.getPageItems()
    for item in items:
        print item[0]
        if item[1] == 4:
            if len(scribus.getText(item[0])) > 0:
                scribus.selectText(0,1,item[0])
            if scribus.getStyle(item[0]) == "HEADER level 1":
                scribus.selectText(0,0,item[0])
                text.append(scribus.getText(item[0]))

    i += 1
scribus.messageBox("Results",str(text))
