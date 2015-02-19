import sys
sys.path.insert(1, '../spec-widgets/specviewer')
import sp_model_manager as mm
from specviewer import SpecViewer

a = mm.ModelManager()

sv = SpecViewer()

a.connect_viewer(sv)
