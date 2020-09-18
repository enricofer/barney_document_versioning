import diff_match_patch as dmp_module
from version.models import Version as V

import sys

dmp = dmp_module.diff_match_patch()

SORGENTE = """
## Qt

Qt è un framework applicativo open-source sviluppato da Nokia per costruire interfacce utente grafiche (GUI) e sviluppare software. Qt è utilizzato in programmi come Google Earth, Virtual Box, Skype, Autodesk e Android. QGIS stesso è costruito con Qt. L'utilizzo di un framework applicativo come Qt velocizza il ciclo di sviluppo di un'applicazione e consente di sviluppare applicazioni multi-piattaforma.
### PyQt
il modulo di collegamento (*bindings*) si chiama PyQt e può essere importato in un programma Python per controllare i widget dell'interfaccia utente
[moduli di Qt](http://doc.qt.io/qt-4.8/modules.html)
[API di PyQt](http://pyqt.sourceforge.net/Docs/PyQt4/modules.html)
"""

TARGET = """
## Qt

Qt è un framework applicativo open-source sviluppato da Nokia per implementare interfacce utente grafiche (GUI) e sviluppare software. Qt è utilizzato in programmi come Google Earth, Virtual Box, Skype, Autodesk e Android. QGIS stesso è costruito con Qt. L'utilizzo di un framework applicativo come Qt velocizza il ciclo di sviluppo di un'applicazione e consente di sviluppare applicazioni multi-piattaforma.
### PyQt
il modulo di "collegamento" (*bindings*) si chiama PyQt e può essere gestito in un programma Python per controllare i widget dell'interfaccia utente
[moduli di Qt](http://doc.qt.io/qt-4.8/modules.html)
[API di PyQt](http://pyqt.sourceforge.net/Docs/PyQt4/modules.html)

"""
TARGET2 = """
## Qt

Qt è un framework applicativo open-source sviluppato da Nokia per implementare interfacce utente grafiche (GUI) e sviluppare software. Qt è utilizzato in programmi come Google Earth, Virtual Box, Skype, Autodesk e Android. QGIS stesso è costruito con Qt. L'utilizzo di un framework applicativo come Qt velocizza il ciclo di sviluppo di un'applicazione e consente di sviluppare applicazioni multi-piattaforma.
### PyQt
il modulo di "collegamento" (*bindings*) si chiama PyQt e può essere gestito in un programma Python per controllare i widget dell'interfaccia utente
[moduli di Qt](http://doc.qt.io/qt-4.8/modules.html)
ambaraba
[API di PyQt](http://pyqt.sourceforge.net/Docs/PyQt4/modules.html)

"""

patch_obj = dmp.patch_make(SORGENTE, TARGET)
patch_text = dmp.patch_toText(patch_obj)

print (patch_text, len(patch_text), file=sys.stderr)

patch_da_txt = dmp.patch_fromText(patch_text)
TARGET_da_patch = dmp.patch_apply(patch_da_txt, SORGENTE)[0]

print (TARGET_da_patch, len(TARGET_da_patch), file=sys.stderr)

master_version = V()
master_version.content = SORGENTE
master_version.save()

version1 = V()
version1.parent = master_version
version1.save()

version1.content = TARGET
version1.save()

version1.content = TARGET2
version1.save()