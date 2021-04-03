from time import sleep
 
from onvif2 import ONVIFCamera

# Workaround type error (copied from ONVIFCameraControl)
import zeep
def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue
zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue 

mycam = ONVIFCamera('192.168.1.171', 8899, 'admin', '')
# Create media service object
media = mycam.create_media_service()
# Get target profile for token
media_profile = media.GetProfiles()[0];
profile_token=media_profile.token
# ~ print (media_profile)

# Create ptz service object
ptz = mycam.create_ptz_service()
# Get PTZ status for a dummy PTZVector
req = ptz.create_type('GetStatus')
req.ProfileToken = profile_token
ptz_status=ptz.GetStatus(req)
# ~ print(ptz_status)
ptz_vector=ptz_status.Position # just a random PTZVector we have around
print(ptz_vector)
# Now we can build the stop request
stop_req=ptz.create_type('Stop')
stop_req.ProfileToken=media_profile.token
stop_req.PanTilt=True
stop_req.Zoom=True
# Now build the move request
move_req = ptz.create_type('ContinuousMove')
move_req.ProfileToken = profile_token
move_req.Velocity = ptz_vector # otherwise it's None type

# ~ # Get PTZ configuration options for getting continuous move range
# ~ req = ptz.create_type('GetConfigurationOptions')
# ~ req.ConfigurationToken = profile_token
# ~ ptz_configuration_options = ptz.GetConfigurationOptions(req)
# ~ print(ptz_configuration_options)

def cam_move(x,y,z):
	global move_req
	move_req.Velocity.PanTilt.x=x
	move_req.Velocity.PanTilt.y=y
	move_req.Velocity.Zoom.x=z
	ptz.ContinuousMove(move_req)
	
def cam_stop():
	global stop_req
	ptz.Stop(stop_req)

import PySimpleGUI as sg
CANVAS_RANGE=100
graph=sg.Graph(
  (CANVAS_RANGE*2,CANVAS_RANGE*2),
  (-CANVAS_RANGE,-CANVAS_RANGE),
  (CANVAS_RANGE,CANVAS_RANGE),
  drag_submits=True, change_submits=True, key='-GRAPH-'
)
layout=[[graph]]
window=sg.Window('PTZ GUI Win', layout, finalize=True)
c=graph.DrawCircle((0,0),10)

def scale_speed(x):
	if abs(x)<10: return 0
	if x > CANVAS_RANGE: return 1
	elif x < -CANVAS_RANGE: return -1
	else: return x/CANVAS_RANGE

# ~ cam_move(0.1,-0.1,0); sleep(3); cam_stop()
# ~ print(scale_speed(0.09))
# ~ exit(0)
	
while True:
	event, values = window.read()
	if event==sg.WIN_CLOSED:
		break
	if event=='-GRAPH-':
		# Mouse drag: move circle to new location
		graph.delete_figure(c)
		x, y = values['-GRAPH-']
		c=graph.DrawCircle((x,y),10)
		# Start camera moving proportionate to displacement
		print(scale_speed(x), scale_speed(y), 0)
		cam_move(scale_speed(x), scale_speed(y), 0)
		# ~ sleep(1)

	elif event=='-GRAPH-+UP':
		# Stopped drag, return circle to centre
		graph.delete_figure(c)
		c=graph.DrawCircle((0,0),10)
		# Stop camera movement
		cam_stop()
