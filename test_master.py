import scribus

master = scribus.getMasterPage(7)
if master.startswith('T -'):
	masters = scribus.masterPageNames()
	new_master = master
	for m in masters:
		print m
		if m.startswith('T0'):
			new_master = m
	scribus.applyMasterPage(new_master,7)
