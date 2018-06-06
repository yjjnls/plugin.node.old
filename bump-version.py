
from conans.client.output import ConanOutput
import sys
import colorama
colorama.init()
printer = ConanOutput(sys.stdout, True)

printer.highlight("#########!@#")