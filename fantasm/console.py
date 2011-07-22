""" Views for the console. """

from google.appengine.ext import webapp
from fantasm import config

class Dashboard(webapp.RequestHandler):
    """ The main dashboard. """
    
    def get(self):
        """ GET """
        
        self.response.out.write(self.generateDashboard())
        
        
    def generateDashboard(self):
        """ Generates the HTML for the dashboard. """
        
        currentConfig = config.currentConfiguration()
        
        s = """
<html>
<head>
  <title>Fantasm</title>
"""
        s += STYLESHEET
        s += """
</head>
<body>

<h1>Fantasm</h1>

<h4>Configured Machines</h4>

<table class='ae-table ae-table-striped' cellpadding='0' cellspacing='0'>
<thead>
  <tr>
    <th>Name</th>
    <th>Queue</th>
    <th>States</th>
    <th>Transitions</th>
    <th>Chart</th>
  </tr>
</thead>
<tbody>
"""
        even = True
        for machineKey in sorted(currentConfig.machines.keys()):
            machine = currentConfig.machines[machineKey]
            even = False if even else True
            s += """
  <tr class='%(class)s'>
    <td>%(machineName)s</td>
    <td>%(queueName)s</td>
    <td>%(numStates)d</td>
    <td>%(numTransitions)d</td>
    <td><a href='%(rootUrl)sgraphviz/%(machineName)s/'>view</a></td>
  </tr>
""" % {
    'class': 'ae-even' if even else '',
    'machineName': machine.name,
    'queueName': machine.queueName,
    'numStates': len(machine.states),
    'numTransitions': len(machine.transitions),
    'rootUrl': currentConfig.rootUrl,
}

        s += """
</tbody>
</table>

</body>
</html>
"""
        return s


STYLESHEET = """
<style>
html, body, div, h1, h2, h3, h4, h5, h6, p, img, dl, dt, dd, ol, ul, li, table, caption, tbody, tfoot, thead, tr, th, td, form, fieldset, embed, object, applet {
    border: 0px;
    margin: 0px;
    padding: 0px;
}
body {
  color: black;
  font-family: Arial, sans-serif;
  padding: 20px;
  font-size: 0.95em;
}
h4, h5, table {
    font-size: 0.95em;
}
table {
    border-collapse: separate;
}
table[cellspacing=0] {
    border-spacing: 0px 0px;
}
thead {
    border-color: inherit;
    display: table-header-group;
    vertical-align: middle;
}
tbody {
    border-color: inherit;
    display: table-row-group;
    vertical-align: middle;
}
tr {
    border-color: inherit;
    display: table-row;
    vertical-align: inherit;
}
th {
    font-weight: bold;
}
td, th {
    display: table-cell;
    vertical-align: inherit;
}
.ae-table {
    border: 1px solid #C5D7EF;
    border-collapse: collapse;
    width: 100%;
}
.ae-table thead th {
    background: #C5D7EF;
    font-weight: bold;
    text-align: left;
    vertical-align: bottom;
}
.ae-table th, .ae-table td {
    background-color: white;
    margin: 0px;
    padding: 0.35em 1em 0.25em 0.35em;
}
.ae-table td {
    border-bottom: 1px solid #C5D7EF;
    border-top: 1px solid #C5D7EF;
}
.ae-even td, .ae-even th, .ae-even-top td, .ae-even-tween td, .ae-even-bottom td, ol.ae-even {
    background-color: #E9E9E9;
    border-bottom: 1px solid #C5D7EF;
    border-top: 1px solid #C5D7EF;
}
</style>
"""
