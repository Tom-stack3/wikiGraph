from graphviz import Digraph
from datetime import datetime

'''
This is a simple script generating a simple tree using the Graphviz library.
I just play around here with different features of the nodes and arrows in graphviz.
Read there documentation here:
https://graphviz.org/documentation/

To read about fonts:
https://graphviz.org/doc/info/attrs.html#d:fontname
'''

u = Digraph('unix_try', filename='try_graph', strict=True,
            node_attr={'color': 'lightskyblue', 'style': 'filled'})
u.attr(size='10,10', layersep="{")

# we make the output format .svg
u.format = 'svg'

u.edge('Nicholas I', 'Alexander II', label="\E")
u.edge('Nicholas I', 'Grand Duke Michael')
u.edge('Nicholas I', 'Maria, Duchess of Leuchtenberg')
u.edge('Nicholas"˸" a I', 'Olga, Queen of Württemberg')
u.edge('Alexander II', 'Grand Duchess Alexandra')
u.edge('Alexander II', 'Tsarevich Nicholas')
u.edge('Alexander II', 'Alexander III')
u.edge('Alexander III', 'Nicholas II', color="red", label="the last")
u.edge('Alexander III', 'Grand Duke Alexander')
u.edge('Alexander III', 'Grand Duke George')
u.edge('Nicholas II', 'Grand Duchess Olga')
u.edge('Nicholas II', 'Grand Duchess Tatiana')
u.edge('Nicholas II', 'Grand Duchess Maria')
u.edge('Nicholas II', 'Grand Duchess Anastasia', headlabel="head label", label="label", taillabel="tail label")
u.edge('Nicholas II', 'Tsesarevich Alexei')

u.node("Grand Duke Michael", fontname="times-bold", textitem="i like your")

u.node("Nicholas I", label="Nicholas I of Russia", URL="https://en.wikipedia.org/wiki/Nicholas_I_of_Russia",
       fontname="Courier-BoldOblique")

now = datetime.now()
l = "\lGraph generated on " + now.strftime("%d/%m/%Y %H:%M:%S") + ".\lChecked " + str(
        100) + " pages. Time took: 69 minutes."
u.attr(label=l, fontsize="20", text="i like your", textitem="yes i am a text")

# we save the file in a .svg file and view it.
u.view()

# we change the output format to .pdf
u.format = 'pdf'
# we save the file in a .pdf file and view it.
# u.view()
